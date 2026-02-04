from app.services.extraction import extract_receipt


def test_extract_receipt_merges_currency(monkeypatch):
    def fake_run_ocr(_path: str) -> str:
        return "Store\nTotal 9.99"

    def fake_run_llm(_text: str, _currency: str | None):
        return {"vendor_name": "Sample", "total": 9.99}, "fake-model"

    monkeypatch.setattr("app.services.extraction.run_ocr", fake_run_ocr)
    monkeypatch.setattr("app.services.extraction.run_llm", fake_run_llm)

    result = extract_receipt("dummy.png", "CAD")
    assert result.extracted["currency"] == "CAD"
    assert result.extracted["vendor_name"] == "Sample"
    assert result.model_name == "fake-model"
