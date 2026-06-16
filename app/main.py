from fastapi import FastAPI, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi import WebSocket, Query
from sqlalchemy import select

from app.config import get_settings
from app.templating import templates
from app.database import get_db, SessionLocal

from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.models.group import Group
from app.routers.auth import router as auth_router
from app.routers.groups import router as groups_router
from app.routers.categories import router as categories_router
from app.routers.templates import router as templates_router
from app.routers.executions import router as executions_router
from app.routers.agenda import router as agenda_router
from app.routers.notifications import router as notifications_router
from app.routers.legal import router as legal
from app.routers.offline import router as offline_router
from app.websocket.handlers import execution_ws_handler
from app.utils.security import decode_access_token

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de Criação e Gerenciamento de Listas de Compras",
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth_router)
app.include_router(groups_router)
app.include_router(categories_router)
app.include_router(templates_router)
app.include_router(executions_router)
app.include_router(agenda_router)
app.include_router(notifications_router)
app.include_router(legal)
app.include_router(offline_router)

@app.middleware("http")
async def add_unread_count(request: Request, call_next):
    """
    Injeta unread_count no request.state para todas as requisições.
    Lê o cookie de sessão para identificar o usuário.
    """
    unread_count = 0
    refreshed_tokens = None
    
    token = request.cookies.get("jaci_session")
    payload = decode_access_token(token) if token else None
    if not payload:
        refresh_token = request.cookies.get("jaci_refresh")
        if refresh_token:
            try:
                from app.services.tupa_auth_service import refresh

                refreshed_tokens = await refresh(refresh_token)
                token = refreshed_tokens["access_token"]
                payload = decode_access_token(token)
                request._cookies["jaci_session"] = token
                request._cookies["jaci_refresh"] = refreshed_tokens["refresh_token"]
            except Exception:
                payload = None

    if token:
        if payload:
            tupa_user_id = payload.get("sub")
            if tupa_user_id:
                db = SessionLocal()
                try:
                    from app.services.notification_service import get_unread_count
                    user = db.scalar(
                        select(User).where(User.tupa_user_id == str(tupa_user_id))
                    )
                    if user:
                        unread_count = get_unread_count(db, user.id)
                except Exception:
                    pass
                finally:
                    db.close()
    
    request.state.unread_count = unread_count
    
    response = await call_next(request)
    if refreshed_tokens:
        from app.utils.security import set_auth_cookies

        set_auth_cookies(response, **refreshed_tokens)
    return response


# ─── Rotas de página ───


@app.get("/")
async def home(
    request: Request,
    db=Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Painel operacional do grupo ativo."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    dashboard = None
    if active_group:
        from app.services.home_service import build_home_dashboard

        dashboard = build_home_dashboard(db, active_group.id)

    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "home",
            "dashboard": dashboard,
        },
    )

@app.websocket("/ws/executions/{execution_id}")
async def websocket_execution(
    websocket: WebSocket,
    execution_id: int,
    token: str = Query(None),
):
    """
    WebSocket para sincronização em tempo real de uma execução.
    Autenticação via token JWT como query parameter.
    """
    await execution_ws_handler(websocket, execution_id, token)

@app.get("/health")
async def health_check():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "modules_completed": ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"],
    }


@app.get("/service-worker.js", include_in_schema=False)
async def service_worker():
    """Serve o service worker na raiz para permitir cache offline da aplicação."""
    return FileResponse(
        "app/static/js/service-worker.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.get("/manifest.webmanifest", include_in_schema=False)
async def web_app_manifest():
    """Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores."""
    return FileResponse(
        "app/static/manifest.webmanifest",
        media_type="application/manifest+json",
    )
