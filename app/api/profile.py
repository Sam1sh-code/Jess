from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Аутентификация"])
templates = Jinja2Templates(directory="frontend")

@router.get("/profile")
def render_profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")