from datetime import datetime
from typing import Iterable

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.receipt import Receipt


def query_receipts(
    db: Session,
    user_id,
    start_date: datetime | None,
    end_date: datetime | None,
    category: str | None,
    min_total: float | None,
    max_total: float | None,
    payment_type: str | None,
    vendor: str | None,
    page: int,
    page_size: int,
) -> tuple[Iterable[Receipt], int]:
    filters = [Receipt.user_id == user_id]
    if start_date:
        filters.append(Receipt.purchased_at >= start_date)
    if end_date:
        filters.append(Receipt.purchased_at <= end_date)
    if category:
        filters.append(Receipt.category == category)
    if min_total is not None:
        filters.append(Receipt.total >= min_total)
    if max_total is not None:
        filters.append(Receipt.total <= max_total)
    if payment_type:
        filters.append(Receipt.payment_type == payment_type)
    if vendor:
        filters.append(Receipt.vendor_name.ilike(f"%{vendor}%"))

    stmt = select(Receipt).where(and_(*filters)).order_by(Receipt.purchased_at.desc().nullslast())
    count_stmt = select(func.count()).select_from(Receipt).where(and_(*filters))

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return items, total
