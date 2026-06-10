from fastapi import FastAPI, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import WebSocket, Query

from app.config import get_settings
from app.templating import templates
from app.database import engine, Base, SessionLocal, ensure_schema_compatibility
from app.dependencies import get_current_user, get_active_group, get_unread_notification_count
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.groups import router as groups_router
from app.routers.categories import router as categories_router
from app.routers.templates import router as templates_router
from app.routers.executions import router as executions_router
from app.routers.agenda import router as agenda_router
from app.routers.notifications import router as notifications_router
from app.routers.legal import router as legal
from app.websocket.handlers import execution_ws_handler

settings = get_settings()

# Cria tabelas
Base.metadata.create_all(bind=engine)
ensure_schema_compatibility()

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

@app.middleware("http")
async def add_unread_count(request: Request, call_next):
    """
    Injeta unread_count no request.state para todas as requisições.
    Lê o cookie de sessão para identificar o usuário.
    """
    unread_count = 0
    
    token = request.cookies.get("jaci_session")
    if token:
        from app.utils.security import decode_access_token
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                db = SessionLocal()
                try:
                    from app.services.notification_service import get_unread_count
                    unread_count = get_unread_count(db, int(user_id))
                except Exception:
                    pass
                finally:
                    db.close()
    
    request.state.unread_count = unread_count
    
    response = await call_next(request)
    return response


# ─── Rotas de página ───


@app.get("/")
async def home(request: Request, user: User | None = Depends(get_current_user), active_group=Depends(get_active_group),):
    """Cancel an execution."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # Placeholder até o Módulo 7 (Agenda)
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "home",
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
