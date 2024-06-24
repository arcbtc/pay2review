from http import HTTPStatus
import json

import httpx
from fastapi import Depends, Query, Request
from loguru import logger
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_user
from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from lnbits.core.views.api import api_payment
from lnbits.decorators import (
    WalletTypeInfo,
    check_admin,
    get_key_type,
    require_admin_key,
    require_invoice_key,
)

from . import p2r_ext
from .crud import (
    create_p2r,
    update_p2r,
    delete_p2r,
    get_p2r,
    get_p2rs,
    create_review,
    get_reviews,
)
from .models import CreateP2RData, P2R, CreateReviewData, Review
from typing import Optional

#######################################
##### ADD YOUR API ENDPOINTS HERE #####
#######################################

## Get all the records belonging to the user


@p2r_ext.get("/api/v1/p2r", status_code=HTTPStatus.OK)
async def api_p2rs(
    req: Request,
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [
        p2r.dict() for p2r in await get_p2rs(wallet_ids, req)
    ]


## Get a single record


@p2r_ext.get("/api/v1/p2r/{p2r_id}", status_code=HTTPStatus.OK)
async def api_p2r(
    req: Request, p2r_id: str, WalletTypeInfo=Depends(get_key_type)
):
    p2r = await get_p2r(p2r_id, req)
    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )
    return p2r.dict()


## update a record


@p2r_ext.put("/api/v1/p2r/{p2r_id}")
async def api_p2r_update(
    req: Request,
    data: CreateP2RData,
    p2r_id: str,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if not p2r_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )
    p2r = await get_p2r(p2r_id, req)
    assert p2r, "P2R couldn't be retrieved"

    if wallet.wallet.id != p2r.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your P2R."
        )
    p2r = await update_p2r(
        p2r_id=p2r_id, **data.dict(), req=req
    )
    return p2r.dict()


## Create a new record


@p2r_ext.post("/api/v1/p2r", status_code=HTTPStatus.CREATED)
async def api_p2r_create(
    req: Request,
    data: CreateP2RData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    p2r = await create_p2r(
        wallet_id=wallet.wallet.id, data=data, req=req
    )
    return p2r.dict()


## Delete a record


@p2r_ext.delete("/api/v1/p2r/{p2r_id}")
async def api_p2r_delete(
    p2r_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    p2r = await get_p2r(p2r_id)

    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )

    if p2r.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your P2R."
        )

    await delete_p2r(p2r_id)
    return "", HTTPStatus.NO_CONTENT


## Create a new review


@p2r_ext.post("/api/v1/p2r/reviews", status_code=HTTPStatus.CREATED)
async def api_review_create(
    req: Request,
    data: CreateReviewData,
):
    p2r = await get_p2r(data.p2r_id, req)
    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"P2R {data.p2r_id} does not exist."
        )
    review = await create_review(
        data=data, req=req
    )
    payment_hash, payment_request = await create_invoice(
        wallet_id=p2r.wallet,
        amount=p2r.price,
        memo=data.p2r_id,
        unhashed_description=f'[["text/plain", "{data.p2r_id}"]]'.encode(),
        extra={
            "tag": "p2r",
            "reviewId": review.id,
        },
    )
    if not payment_request:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"Could not to create payment."
        )
    return {"payment_request": payment_request, "review_id": review.id}


@p2r_ext.get("/api/v1/p2r/reviews/{p2r_id}", status_code=HTTPStatus.OK)
async def api_reviews(
    req: Request,
    p2r_id: str,
    item_id: Optional[str] = None,
):
    p2r = await get_p2r(p2r_id, req)
    if not p2r:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="P2R does not exist."
        )
    return [
        review.dict() for review in await get_reviews(p2r_id, item_id, req)
    ]