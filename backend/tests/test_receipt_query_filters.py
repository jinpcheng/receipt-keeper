from datetime import datetime, timezone

from app.crud.receipt_query import query_receipts
from app.models.enums import PaymentType, ReceiptCategory
from app.models.receipt import Receipt
from app.models.user import User


def test_query_receipts_filters_all_branches(db_session):
    user = User(email="filters@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    r1 = Receipt(
        user_id=user_id,
        vendor_name="Alpha Station",
        purchased_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        category=ReceiptCategory.gas,
        payment_type=PaymentType.credit_card,
        total=10.00,
    )
    r2 = Receipt(
        user_id=user_id,
        vendor_name="Bravo Cafe",
        purchased_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        category=ReceiptCategory.food,
        payment_type=PaymentType.cash,
        total=25.00,
    )
    r3 = Receipt(
        user_id=user_id,
        vendor_name="Charlie Office",
        purchased_at=None,
        category=ReceiptCategory.office,
        payment_type=PaymentType.debit_card,
        total=99.99,
    )
    db_session.add_all([r1, r2, r3])
    db_session.commit()

    # No filters besides user_id
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=None,
        min_total=None,
        max_total=None,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 3
    assert len(list(items)) == 3

    # start_date
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
        end_date=None,
        category=None,
        min_total=None,
        max_total=None,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 1

    # end_date
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        category=None,
        min_total=None,
        max_total=None,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 1

    # category
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=ReceiptCategory.food,
        min_total=None,
        max_total=None,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 1

    # min_total
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=None,
        min_total=20.0,
        max_total=None,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 2

    # max_total
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=None,
        min_total=None,
        max_total=20.0,
        payment_type=None,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 1

    # payment_type
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=None,
        min_total=None,
        max_total=None,
        payment_type=PaymentType.cash,
        vendor=None,
        page=1,
        page_size=50,
    )
    assert total == 1

    # vendor ilike
    items, total = query_receipts(
        db=db_session,
        user_id=user_id,
        start_date=None,
        end_date=None,
        category=None,
        min_total=None,
        max_total=None,
        payment_type=None,
        vendor="bravo",
        page=1,
        page_size=50,
    )
    assert total == 1
