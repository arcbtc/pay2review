import asyncio

from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

db = Database("ext_p2r")

p2r_ext: APIRouter = APIRouter(
    prefix="/p2r", tags=["P2R"]
)

p2r_static_files = [
    {
        "path": "/p2r/static",
        "name": "p2r_static",
    }
]


def p2r_renderer():
    return template_renderer(["p2r/templates"])


from .tasks import wait_for_paid_invoices
from .views import *
from .views_api import *

scheduled_tasks: list[asyncio.Task] = []

def p2r_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)

def p2r_start():
    task = create_permanent_unique_task("ext_p2r", wait_for_paid_invoices)
    scheduled_tasks.append(task)