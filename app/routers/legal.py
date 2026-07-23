from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Legal"])


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Privacy Policy page - LGPD"""
    from app.main import templates
    return templates.TemplateResponse(
        request,
        "pages/legal/privacy.html",
        {"request": request}
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms_of_use(request: Request):
    """Terms of Use page"""
    from app.main import templates
    return templates.TemplateResponse(
        request,
        "pages/legal/terms.html",
        {"request": request}
    )