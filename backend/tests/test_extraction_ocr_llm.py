from __future__ import annotations

import types

import pytest

import app.services.extraction as extraction


def test_get_ocr_is_cached(monkeypatch):
    calls = {"init": 0}

    class FakeOCR:
        def __init__(self, *args, **kwargs):
            calls["init"] += 1

        def ocr(self, _path: str, cls: bool):
            return []

    monkeypatch.setattr(extraction, "_ocr_instance", None)
    monkeypatch.setattr(extraction, "PaddleOCR", FakeOCR)

    o1 = extraction._get_ocr()
    o2 = extraction._get_ocr()
    assert o1 is o2
    assert calls["init"] == 1


def test_run_ocr_collects_non_empty_lines(monkeypatch):
    class FakeOCR:
        def ocr(self, _path: str, cls: bool):
            return [
                [
                    # entry format: [bbox, [text, score]]
                    (None, ("Hello", 0.9)),
                    (None, ("", 0.9)),
                    (None, ("World", 0.9)),
                ]
            ]

    monkeypatch.setattr(extraction, "_get_ocr", lambda: FakeOCR())
    text = extraction.run_ocr("dummy.png")
    assert text == "Hello\nWorld"


def test_run_llm_posts_and_parses_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            # wrapped json to exercise regex extraction path in _parse_json
            return {"response": "prefix {\"vendor_name\":\"X\",\"total\":1.23} suffix"}

    def fake_post(url, json, timeout):
        assert url.endswith("/api/generate")
        assert isinstance(json.get("prompt"), str) and "OCR text" in json["prompt"]
        return FakeResponse()

    monkeypatch.setattr(extraction, "requests", types.SimpleNamespace(post=fake_post))
    extracted, model = extraction.run_llm("OCR", currency="CAD")
    assert extracted["vendor_name"] == "X"
    assert model


def test_extract_receipt_sets_currency_when_missing(monkeypatch):
    monkeypatch.setattr(extraction, "run_ocr", lambda _p: "T")
    monkeypatch.setattr(extraction, "run_llm", lambda _t, _c: ({"total": 1.0}, "m"))
    result = extraction.extract_receipt("dummy.png", currency="CAD")
    assert result.extracted["currency"] == "CAD"

