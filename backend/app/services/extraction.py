import json
import re
from dataclasses import dataclass
from typing import Any

import requests
from paddleocr import PaddleOCR

from app.core.config import settings


@dataclass
class ExtractionResult:
    ocr_text: str
    extracted: dict[str, Any]
    model_name: str
    confidence: float | None = None


_ocr_instance: PaddleOCR | None = None


def _get_ocr() -> PaddleOCR:
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang=settings.ocr_lang)
    return _ocr_instance


def run_ocr(image_path: str) -> str:
    ocr = _get_ocr()
    result = ocr.ocr(image_path, cls=True)
    lines: list[str] = []
    for block in result:
        for entry in block:
            text = entry[1][0]
            if text:
                lines.append(text)
    return "\n".join(lines)


def _build_prompt(ocr_text: str, currency: str | None) -> str:
    return (
        "You are extracting structured receipt data from OCR text. "
        "Return ONLY valid JSON with these fields: "
        "vendor_name, location, purchased_at, category, subtotal, tax, total, currency, "
        "payment_type, card_type, card_last4, ref_number, invoice_number, auth_number, notes. "
        "If a field is unknown, use null. "
        "Use ISO 8601 for purchased_at when possible. "
        "Category must be one of: gas, food, office, travel, lodging, entertainment, medical, personal, other. "
        "payment_type must be one of: credit_card, debit_card, cash, transfer, mobile_pay, other. "
        "card_type must be one of: visa, mastercard, amex, discover, other, unknown. "
        f"Default currency is {currency or 'CAD'} if not present. "
        "OCR text:\n"
        f"{ocr_text}"
    )


def _parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def run_llm(ocr_text: str, currency: str | None) -> tuple[dict[str, Any], str]:
    payload = {
        "model": settings.ollama_model,
        "prompt": _build_prompt(ocr_text, currency),
        "stream": False,
    }
    response = requests.post(
        f"{settings.ollama_url}/api/generate",
        json=payload,
        timeout=settings.ollama_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    return _parse_json(data.get("response", "{}")), settings.ollama_model


def extract_receipt(image_path: str, currency: str | None) -> ExtractionResult:
    ocr_text = run_ocr(image_path)
    extracted, model_name = run_llm(ocr_text, currency)
    if currency and not extracted.get("currency"):
        extracted["currency"] = currency
    return ExtractionResult(
        ocr_text=ocr_text,
        extracted=extracted,
        model_name=model_name,
        confidence=None,
    )
