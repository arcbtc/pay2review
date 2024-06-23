from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.settings import settings

from . import p2r_ext, p2r_renderer
from .crud import get_p2r
from loguru import logger
p2r = Jinja2Templates(directory="p2r")


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@p2r_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return p2r_renderer().TemplateResponse(
        "p2r/index.html", {"request": request, "user": user.dict()}
    )


# Frontend shareable page


@p2r_ext.get("/{p2r_id}/{item_id}")
async def p2r(request: Request, p2r_id, item_id):
    p2r = await get_p2r(p2r_id, request)
    logger.debug(p2r.review_length)
    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )
    return p2r_renderer().TemplateResponse(
        "p2r/p2r.html",
        {
            "request": request,
            "p2r_id": p2r_id,
            "item_id": item_id,
            "p2r_name": p2r.name,
            "p2r_description": p2r.description,
            "p2r_price": p2r.price,
            "review_length": p2r.review_length,
            "web_manifest": f"/p2r/manifest/{p2r_id}.webmanifest",
        },
    )


# Manifest for public page, customise or remove manifest completely


@p2r_ext.get("/manifest/{p2r_id}.webmanifest")
async def manifest(p2r_id: str):
    p2r = await get_p2r(p2r_id)
    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )

    return {
        "short_name": settings.lnbits_site_title,
        "name": p2r.name + " - " + settings.lnbits_site_title,
        "icons": [
            {
                "src": settings.lnbits_custom_logo
                if settings.lnbits_custom_logo
                else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png",
                "type": "image/png",
                "sizes": "900x900",
            }
        ],
        "start_url": "/p2r/" + p2r_id,
        "background_color": "#1F2234",
        "description": "Minimal extension to build on",
        "display": "standalone",
        "scope": "/p2r/" + p2r_id,
        "theme_color": "#1F2234",
        "shortcuts": [
            {
                "name": p2r.name + " - " + settings.lnbits_site_title,
                "short_name": p2r.name,
                "description": p2r.name + " - " + settings.lnbits_site_title,
                "url": "/p2r/" + p2r_id,
            }
        ],
    }
