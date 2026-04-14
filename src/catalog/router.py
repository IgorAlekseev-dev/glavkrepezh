from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, func, literal 
from sqlalchemy.orm import joinedload, aliased

from src.catalog.models import Category, Product
from src.depends import SessionDep
from src.config import settings
from src.limiter import limiter

router = APIRouter(tags=["Catalog"])
templates = Jinja2Templates(directory="templates")

async def render_catalog_view(
    request: Request, 
    db: SessionDep, 
    category_obj: Category = None, 
    q: str = None, 
    page: int = 1,
    prev_cat: str = None
):
    # --- 1. ЛОГИКА КАТЕГОРИЙ (КВАДРАТИКИ) ---
    
    # Базовый запрос + ИСКЛЮЧАЕМ "111"
    cats_query = select(Category).where(Category.name != "111").order_by(Category.id)

    if q:
        # Поиск по категориям
        cats_query = cats_query.where(Category.name.ilike(f"%{q}%"))
        if category_obj:
             cats_query = cats_query.where(Category.parent_id == category_obj.id)
    else:
        if category_obj:
            cats_query = cats_query.where(Category.parent_id == category_obj.id)
        else:
            cats_query = cats_query.where(Category.parent_id == None)
        
    cats_result = await db.execute(cats_query)
    categories_list = cats_result.scalars().all()


    # --- 2. ЛОГИКА ТОВАРОВ (ТАБЛИЦА) ---
    limit = 50
    offset = (page - 1) * limit

    products_query = (
        select(Product)
        .options(joinedload(Product.category))
        .join(Category)
    )

    if category_obj:
        # Рекурсивный поиск для товаров (CTE)
        cte = select(Category.id).where(Category.id == category_obj.id).cte(recursive=True)
        parent = aliased(Category)
        child_query = select(parent.id).where(parent.parent_id == cte.c.id)
        cte = cte.union_all(child_query)
        products_query = products_query.where(Product.category_id.in_(select(cte.c.id)))

    # --- ПРОДВИНУТЫЙ ПОИСК (FTS + Триграммы) ---
    # --- ПРОДВИНУТЫЙ ПОИСК (FTS + Триграммы) ---
    if q:
        ts_query = func.websearch_to_tsquery('russian', q)
        ts_vector = func.to_tsvector('russian', Product.name)
        
        # 1. ПОВЫШАЕМ ПОРОГ до 0.4 (40%), чтобы суффиксы типа "-льный" не пролетали
        search_filter = or_(
            ts_vector.op('@@')(ts_query),
            Product.name.ilike(f"%{q}%"),
            func.word_similarity(q, Product.name) > 0.4 
        )
        
        if hasattr(Product, 'article'):
             search_filter = or_(search_filter, Product.article.ilike(f"%{q}%"))
             
        products_query = products_query.where(search_filter)

        # 2. ИЗМЕНЯЕМ СОРТИРОВКУ ДЛЯ ПОИСКА
        # Сначала сортируем по 'расстоянию' (самые похожие - наверх)
        # А уже потом по имени категории и товара
        products_query = products_query.order_by(
            Product.name.op('<->')(q),  # Самое важное совпадение - первое!
            Category.name,
            Product.name
        ).limit(limit).offset(offset)
        
    else:
        # ОБЫЧНАЯ СОРТИРОВКА (Без поиска)
        # Здесь мы сохраняем алфавитный порядок категорий
        products_query = products_query.order_by(
            Category.name, 
            Product.name
        ).limit(limit).offset(offset)

    result = await db.execute(products_query)
    products_list = result.scalars().all()

    result = await db.execute(products_query)
    products_list = result.scalars().all()

    # --- 3. ОТВЕТ HTMX ---
    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return templates.TemplateResponse(
            "components/product_rows.html", 
            {
                "request": request, 
                "products": products_list, 
                "page": page,
                "q": q,
                "current_category": category_obj,
                "prev_cat": prev_cat
            }
        )
    
    # --- 4. ПОЛНАЯ СТРАНИЦА ---
    return templates.TemplateResponse(
        "CatalogPage.html",
        {
            "request": request,
            "categories": categories_list,
            "products": products_list,
            "current_category": category_obj,
            "page": page,
            "search_query": q,
            "prev_cat": None
        }
    )

@router.get("/catalog")
@limiter.limit("15/minute")
async def catalog_root(
    request: Request, 
    db: SessionDep,
    q: str = Query(None),
    page: int = 1,
    prev_cat: str = Query(None)
):
    return await render_catalog_view(request, db, None, q, page, prev_cat)

@router.get("/catalog/{cat_slug}")
@limiter.limit("20/minute")
async def show_category(
    request: Request,
    cat_slug: str,
    db: SessionDep,
    q: str = Query(None),
    page: int = 1,
    prev_cat: str = Query(None)
):
    query = select(Category).options(joinedload(Category.parent)).where(Category.slug == cat_slug)
    result = await db.execute(query)
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return await render_catalog_view(request, db, category, q, page, prev_cat)


@router.get("/download-price")
async def download_price():
    path = settings.UPLOAD_DIR / "price.xlsx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Прайс-лист еще не загружен")

    return FileResponse(
        path=path,
        filename="Прайс-Главкрепеж.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
