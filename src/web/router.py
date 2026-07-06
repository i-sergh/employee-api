from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="web/templates")

@router.get("/", response_class=HTMLResponse)
async def employee_list(request: Request):
    return templates.TemplateResponse(name="employee/list.html", request=request)


@router.get("/{id}", response_class=HTMLResponse)
async def employee_list(request: Request, id:int):
    return templates.TemplateResponse(name="employee/edit.html",
                                      request=request,
                                      context={"employee_id": id})