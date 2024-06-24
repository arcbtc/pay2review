import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.core.services import create_invoice, websocket_updater
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .crud import set_review_paid

async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)

async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "p2r":
        return
    try:
        await set_review_paid(review_id=payment.extra.get("reviewId"))
        await websocket_updater(payment.extra.get("reviewId"), "paid")
    except Exception as e:
        pass
    
    
