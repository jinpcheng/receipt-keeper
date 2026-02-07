import pytest

from app.services.extraction import _parse_json


def test_parse_json_accepts_plain_json():
    assert _parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_extracts_json_from_wrapped_text():
    text = "prefix blah\n{\"vendor_name\": \"X\", \"total\": 1.23}\ntrailing"
    assert _parse_json(text)["vendor_name"] == "X"


def test_parse_json_raises_when_no_json_present():
    with pytest.raises(Exception):
        _parse_json("no braces here")

