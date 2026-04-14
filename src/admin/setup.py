from pathlib import Path
from starlette_admin.contrib.sqla import Admin, ModelView

from src.admin.models import PriceDoc
from src.catalog.models import Category, Product
from src.auth.models import AdminUser
from src.admin.auth import MyAuthProvider
from src.admin.views import PriceDocView
from src.config import settings

def setup_admin(app, engine):

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    my_templates_dir = str(BASE_DIR / "templates" / "admin")

    admin = Admin(
        engine, 
        title="ГлавКрепеж Админ",
        base_url=settings.ADMIN_PANEL_PATH,
        auth_provider=MyAuthProvider(),
        templates_dir=my_templates_dir,
    )

    admin.add_view(PriceDocView(PriceDoc, icon="fa fa-upload"))

    admin.add_view(ModelView(Category, icon="fa fa-folder", label="Категории"))
    admin.add_view(ModelView(Product, icon="fa fa-tag", label="Товары"))
    admin.add_view(ModelView(AdminUser, icon="fa fa-user", label="Админы"))
    
    admin.mount_to(app, settings.ADMIN_PANEL_PATH)