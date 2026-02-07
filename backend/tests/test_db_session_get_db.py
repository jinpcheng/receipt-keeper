from app.db import session as session_module


def test_get_db_closes_session():
    calls = {"close": 0}

    class DummySession:
        def close(self):
            calls["close"] += 1

    def dummy_session_local():
        return DummySession()

    original = session_module.SessionLocal
    session_module.SessionLocal = dummy_session_local  # type: ignore[assignment]
    try:
        gen = session_module.get_db()
        db = next(gen)
        assert isinstance(db, DummySession)
        gen.close()
        assert calls["close"] == 1
    finally:
        session_module.SessionLocal = original

