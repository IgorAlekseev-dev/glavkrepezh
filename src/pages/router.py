from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from datetime import datetime, timezone
from pathlib import Path

from src.catalog.models import Category
from src.limiter import limiter
from src.depends import SessionDep

router = APIRouter(tags=["Pages"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/")
@limiter.limit("8/minute")
async def home_page(request: Request):
    return templates.TemplateResponse("HomePage.html", {"request": request})

# @router.get("/about")
# @limiter.limit("8/minute")
# async def about_page(request: Request):
#     return templates.TemplateResponse("AboutPage.html", {"request": request})

@router.get("/delivery")
@limiter.limit("8/minute")
async def delivery_page(request: Request):
    return templates.TemplateResponse("DeliveryPage.html", {"request": request})

@router.get("/contacts")
@limiter.limit("8/minute")
async def contacts_page(request: Request):
    return templates.TemplateResponse("ContactsPage.html", {"request": request})

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """
    SEO: Правила индексации сайта для поисковых роботов (Googlebot, Yandex).
    """
    # Замени glavkrepezh.ru на свой реальный домен, когда он появится!
    domain = "https://xn--80aebkagzf4bi.xn--p1ai"
    
    content = f"""User-agent: Yandex
Allow: /
Disallow: /api/
Disallow: /download-price
Disallow: /admin/
Disallow: /wp-admin/
Disallow: /wp-login.php
Disallow: /bitrix/
Disallow: /*?q=
Disallow: /*&q=
Disallow: /*prev_cat=
Clean-param: q&prev_cat&page /catalog
Crawl-delay: 1

User-agent: Googlebot
Allow: /
Disallow: /api/
Disallow: /download-price
Disallow: /admin/
Disallow: /wp-admin/
Disallow: /wp-login.php
Disallow: /bitrix/
Disallow: /*?q=
Disallow: /*&q=
Disallow: /*prev_cat=

User-agent: *
Allow: /
Disallow: /api/
Disallow: /download-price
Disallow: /admin/
Disallow: /wp-admin/
Disallow: /wp-login.php
Disallow: /bitrix/
Disallow: /*?q=
Disallow: /*&q=
Disallow: /*prev_cat=
Crawl-delay: 1

Sitemap: {domain}/sitemap.xml
"""
    return content

@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(db: SessionDep):
    """
    SEO: Динамическая карта сайта для поисковиков.
    Генерирует XML на лету, собирая все статические страницы и все категории из базы.
    """
    # ВАЖНО: Замени на свой реальный домен без слеша на конце!
    domain = "https://xn--80aebkagzf4bi.xn--p1ai"
    
    # Берем сегодняшнюю дату (поисковики любят, когда lastmod свежий)
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. СТАТИЧЕСКИЕ СТРАНИЦЫ (Те самые, которые мы хотим видеть в быстрых ссылках)
    static_urls =[
        {"loc": "/", "changefreq": "daily", "priority": "1.0"},
        {"loc": "/catalog", "changefreq": "daily", "priority": "0.9"},
        {"loc": "/delivery", "changefreq": "monthly", "priority": "0.8"},
        {"loc": "/contacts", "changefreq": "monthly", "priority": "0.8"},
    ]

    # 2. ДИНАМИЧЕСКИЕ СТРАНИЦЫ (Все категории из базы данных)
    # Нам нужны только слаги, поэтому select(Category.slug) работает молниеносно
    query = select(Category.slug).where(Category.name != "111")
    result = await db.execute(query)
    categories = result.scalars().all()

    # 3. ГЕНЕРАЦИЯ XML СТРОКИ
    xml_urls = ""
    
    # Добавляем статику
    for item in static_urls:
        xml_urls += f"""
  <url>
    <loc>{domain}{item['loc']}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>{item['changefreq']}</changefreq>
    <priority>{item['priority']}</priority>
  </url>"""

    # Добавляем категории
    for slug in categories:
        xml_urls += f"""
  <url>
    <loc>{domain}/catalog/{slug}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>"""

    # Оборачиваем всё в стандартный XML тег
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_urls}
</urlset>"""

    # Отдаем браузеру/роботу строго с типом application/xml
    return Response(content=sitemap_xml.strip(), media_type="application/xml")

@router.get("/privacy")
async def privacy_page(request: Request):
    return templates.TemplateResponse("PrivacyPage.html", {"request": request})

@router.get("/privacy-consent")
async def consent_page(request: Request):
    return templates.TemplateResponse("ConsentPage.html", {"request": request})

@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """
    Файл для нейросетей и LLM-ботов.
    Формат Markdown.
    """
    content = """# ГлавКрепеж

> Специализированный магазин строительного крепежа, метизной продукции и инструмента в Иваново. Ресурс предоставляет интерактивный каталог из 2000+ наименований товаров для частного строительства и промышленных предприятий.

## Основные разделы
- [Каталог продукции](/catalog): Полный ассортимент метизов, болтов, винтов, саморезов, анкерных систем и расходных материалов. Поддерживает интеллектуальный поиск с учетом опечаток.
- [Оплата и доставка](/delivery): Условия логистики по Иваново и РФ. Информация о наличном и безналичном расчете.
- [Контакты](/contacts): Географическое расположение склада, прямые линии связи и форма отправки сообщений руководству.

## Информация о бизнесе
- **Ассортимент**: Метрический крепеж, сверла, электроды, пена и герметики, болты, гайки, винты, шайбы, саморезы, анкеры, дюбели, такелаж, расходники и многое другое..
- **Уникальное преимущество**: Магазин в Иваново, работающий по графику 08:00 – 19:00 ежедневно без перерывов и выходных.
- **Сервис**: Автоматизированное обновление прайс-листа, оперативная доставка в день заказа, профессиональный подбор крепежа под задачи клиента.

## Технические данные
- **Адрес**: г. Иваново, ул. Бубнова 41.
- **Телефон**: +7 (4932) 28-54-54
- **Email**: [glavcrepezh@yandex.ru](mailto:glavcrepezh@yandex.ru)
- **Домен**: [https://главкрепеж.рф/](https://xn--80aebkagzf4bi.xn--p1ai/)

## Optional
- [Политика конфиденциальности](/privacy): Юридическая информация об обработке данных в соответствии с ФЗ-152.
- [Согласие на обработку данных](/privacy-consent): Форма официального согласия пользователя.
- [Скачать прайс-лист](/download-price): Актуальная выгрузка всей номенклатуры в формате Excel.

"""
    return content