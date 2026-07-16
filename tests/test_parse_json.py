from research_summarizer_agent import parse_json


def test_parse_json_reads_plain_json():
    assert parse_json('{"summary": "Done"}') == {"summary": "Done"}


def test_parse_json_reads_fenced_json():
    assert parse_json('```json\n{"summary": "Done"}\n```') == {"summary": "Done"}


def test_parse_json_reads_embedded_json():
    assert parse_json('Here is the result: {"summary": "Done"}') == {"summary": "Done"}
