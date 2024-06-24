
from lnbits.db import Database

async def m001_initial(db):
    """
    Initial templates table.
    """
    await db.execute(
        """
        CREATE TABLE p2r.maintable (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            price INTEGER default 10,
            name TEXT NOT NULL,
            description TEXT,
            review_length integer DEFAULT 0
        );
    """
    )

async def m002_add_reviews(db):
    """
    Add total to templates table
    """
    await db.execute(
        """
        CREATE TABLE p2r.reviews (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            p2r_id TEXT NOT NULL,
            previous_id TEXT,
            name TEXT NOT NULL,
            review_int INTEGER DEFAULT 0,
            review_text TEXT,
            paid BOOLEAN DEFAULT FALSE,
            review_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """
    )