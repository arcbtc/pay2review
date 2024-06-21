from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import CreateP2RData, P2R
from loguru import logger
from fastapi import Request
import datetime
import shortuuid

#######################################
########### Pay-2-Reviews #############
#######################################

async def create_p2r(
    wallet_id: str, data: CreateP2RData, req: Request
) -> P2R:
    p2r_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO p2r.maintable (id, wallet, name, description, review_length)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            p2r_id,
            wallet_id,
            data.name,
            data.description,
            data.review_length,
        ),
    )
    p2r = await get_p2r(p2r_id, req)
    assert p2r, "Newly created table couldn't be retrieved"
    return p2r


async def get_p2r(
    p2r_id: str, req: Optional[Request] = None
) -> Optional[P2R]:
    row = await db.fetchone(
        "SELECT * FROM p2r.maintable WHERE id = ?", (p2r_id,)
    )
    if not row:
        return None
    rowAmended = P2R(**row)

    return rowAmended


async def get_p2rs(
    wallet_ids: Union[str, List[str]], req: Optional[Request] = None
) -> List[P2R]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM p2r.maintable WHERE wallet IN ({q})", (*wallet_ids,)
    )
    tempRows = [P2R(**row) for row in rows]

    return tempRows


async def update_p2r(
    p2r_id: str, req: Optional[Request] = None, **kwargs
) -> P2R:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE p2r.maintable SET {q} WHERE id = ?",
        (*kwargs.values(), p2r_id),
    )
    p2r = await get_p2r(p2r_id, req)
    assert p2r, "Newly updated p2r couldn't be retrieved"
    return p2r


async def delete_p2r(p2r_id: str) -> None:
    await db.execute(
        "DELETE FROM p2r.maintable WHERE id = ?", (p2r_id,)
    )

#######################################
############### REVIEWS ###############
#######################################

async def create_review(
    wallet_id: str, data: CreateP2RData, req: Request
) -> Review:
    review_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO p2r.reviews (id, wallet, item_id, p2r_id, previous_id, name, description, review_int, review_text, paid, review_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            p2r_id,
            wallet_id,
            data.item_id,
            data.previous_id,
            data.name,
            data.description,
            data.review_int,
            data.review_text,
            paid = False,
            datetime.datetime.now()
        ),
    )
    review = await get_review(review_id, req)
    assert review, "Newly created table couldn't be retrieved"
    return review

async def get_review(
    review_id: str, req: Optional[Request] = None
) -> Optional[Review]:
    row = await db.fetchone(
        "SELECT * FROM p2r.reviews WHERE id = ?", (review_id,)
    )
    if not row:
        return None
    rowAmended = Review(**row)

    return rowAmended

async def get_reviews(
    p2r_id: str, req: Optional[Request] = None
) -> List[Review]:

    rows = await db.fetchall(
        "SELECT * FROM p2r.reviews WHERE wallet IN ?", (p2r_id,)
    )
    tempRows = [Review(**row) for row in rows]

    return tempRows