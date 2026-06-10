"""Quick verification of DifyClient and service modules."""
import json
import sys
sys.path.insert(0, ".")

from app.integrations.dify_client import DifyClient, _parse_llm_json, _mock_customer_judgement_result


def test_mock_result():
    result = _mock_customer_judgement_result()
    assert "executive_summary" in result
    assert result["is_target_customer"] is True
    assert result["overall_match_score"] == 88
    assert result["overall_match_level"] == "high"
    assert "customer_profile" in result
    assert "product_a_evaluation" in result
    assert "product_b_evaluation" in result
    print("[PASS] Mock result structure valid")


def test_parse_plain_json():
    parsed = _parse_llm_json('{"executive_summary": "test", "is_target_customer": true}')
    assert parsed["executive_summary"] == "test"
    print("[PASS] Plain JSON parse")


def test_parse_markdown_json():
    text = '```json\n{"executive_summary": "test2", "is_target_customer": false}\n```'
    parsed = _parse_llm_json(text)
    assert parsed["executive_summary"] == "test2"
    print("[PASS] Markdown fenced JSON parse")


def test_parse_markdown_no_lang():
    text = '```\n{"executive_summary": "test3", "is_target_customer": true}\n```'
    parsed = _parse_llm_json(text)
    assert parsed["executive_summary"] == "test3"
    print("[PASS] Markdown no-lang JSON parse")


def test_dify_client_mock():
    client = DifyClient()
    result = client.call_customer_judgement("test customer info")
    assert "executive_summary" in result
    print("[PASS] DifyClient mock mode")


def test_empty_input():
    try:
        _parse_llm_json("")
        assert False, "Should have raised"
    except RuntimeError:
        print("[PASS] Empty input raises RuntimeError")


if __name__ == "__main__":
    test_mock_result()
    test_parse_plain_json()
    test_parse_markdown_json()
    test_parse_markdown_no_lang()
    test_dify_client_mock()
    test_empty_input()
    print("\nAll tests passed!")
