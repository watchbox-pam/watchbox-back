from fastapi import APIRouter, Depends

from api.admin import movies, users
from api.admin.dependencies import verify_admin_api_key

# Toutes les routes /admin/* sont protégées par la clé API admin,
# inutile de répéter la dépendance sur chaque route.
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_api_key)],
)

admin_router.include_router(movies.router)
admin_router.include_router(users.router)
