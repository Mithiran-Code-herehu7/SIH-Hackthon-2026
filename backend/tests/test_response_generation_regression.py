import pytest
from app.api.v1.chat.router import generate_structured_response, sanitize_answer, generate_final_answer


def test_scenario_a_ppt_generation():
    query = "Generate a 5-slide PowerPoint titled July–August 2026 Operations Safety Review."
    agent_result = {
        "intent": "report_generation",
        "tool": "report_generation",
        "reason": "User requested PowerPoint generation",
        "sources": [{"file_id": "doc1", "filename": "MRPL_Operations_Safety_Demo_Pack.md", "chunk_index": 0}],
        "tool_result": None,
    }
    res = generate_structured_response(query, agent_result, "req_ppt_01")
    
    assert "July–August 2026 Operations Safety Review" in res["title"]
    assert "July–August 2026 Operations Safety Review" in res["answer"]
    assert len(res["files"]) == 1
    assert res["files"][0]["type"] == "ppt"
    
    # Defensive checks: No leaked tags or prompts
    for tag in ["[OBSERVED]", "[UNCERTAINTY]", "[PLAN]", "[TOOL]", "[SOURCE]", "UNCERTAINTY:"]:
        assert tag not in res["answer"]


def test_scenario_b_incident_count():
    query = "How many recordable incidents occurred?"
    agent_result = {
        "intent": "safety_analysis",
        "tool": "safety_analysis",
        "reason": "Count recordable incidents",
        "sources": [{"file_id": "doc1", "filename": "HSE_Report_2025.pdf", "chunk_index": 2}],
        "tool_result": None,
    }
    res = generate_structured_response(query, agent_result, "req_inc_01")
    
    assert res["title"] == "Incident Analysis"
    assert "3 recordable incidents" in res["answer"]
    assert res["uncertainties"] == []
    
    # Defensive checks
    for tag in ["[OBSERVED]", "[UNCERTAINTY]", "[PLAN]", "[TOOL]", "[SOURCE]", "UNCERTAINTY:"]:
        assert tag not in res["answer"]


def test_scenario_c_monetary_loss_grounded_refusal():
    query = "What was the exact monetary loss caused by Pump P-204B?"
    agent_result = {
        "intent": "document_question",
        "tool": "document_search",
        "reason": "Lookup monetary loss",
        "sources": [],
        "tool_result": None,
    }
    res = generate_structured_response(query, agent_result, "req_mon_01")
    
    assert res["title"] == "Information Not Available in Corpus"
    assert "The uploaded document does not provide a monetary-loss figure for Pump P-204B." in res["answer"]
    assert len(res["uncertainties"]) == 1
    assert "The uploaded document does not provide a monetary-loss figure for Pump P-204B." in res["uncertainties"][0]
    
    # No raw UNCERTAINTY: prefix in answer string
    assert not res["answer"].startswith("UNCERTAINTY:")
    assert "[UNCERTAINTY]" not in res["answer"]


def test_scenario_d_open_corrective_actions():
    query = "List open corrective actions."
    agent_result = {
        "intent": "safety_analysis",
        "tool": "safety_analysis",
        "reason": "List CAP items",
        "sources": [{"file_id": "doc1", "filename": "SOP_Operations.docx", "chunk_index": 5}],
        "tool_result": None,
    }
    res = generate_structured_response(query, agent_result, "req_cap_01")
    
    assert res["title"] == "Open Corrective Action Items"
    for cap_item in ["CAP-01", "CAP-02", "CAP-03", "CAP-04", "CAP-05", "CAP-07", "CAP-08"]:
        assert cap_item in res["answer"]
    
    # Defensive checks: No leaked system or planner content
    for tag in ["[OBSERVED]", "[UNCERTAINTY]", "[PLAN]", "[TOOL]", "[SOURCE]", "UNCERTAINTY:"]:
        assert tag not in res["answer"]


def test_defensive_sanitization_and_fallback():
    raw_dirty_text = """
    [OBSERVED] CDU operates near atmospheric pressure.
    [INFERRED] Temperature gradient is nominal.
    UNCERTAINTY: Specific PPE details were not identified.
    WARNING: High temperature hazard.
    [Task Mode: chat] What are the operating limits?
    """
    cleaned = sanitize_answer(raw_dirty_text)
    assert "[OBSERVED]" not in cleaned
    assert "[INFERRED]" not in cleaned
    assert "UNCERTAINTY:" not in cleaned
    assert "[Task Mode: chat]" not in cleaned
    assert "CDU operates near atmospheric pressure." in cleaned

    # Fallback check for empty text
    empty_cleaned = sanitize_answer("   \n\n  ")
    assert empty_cleaned == "I could not prepare a clean response from the retrieved evidence. Please try again."
