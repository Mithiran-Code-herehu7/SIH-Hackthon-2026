import pytest
from app.agent.orchestrator import classify_intent, run_agent
from app.api.v1.chat.router import generate_structured_response
from app.rag.service import index_document, search_documents

MRPL_DEMO_TEXT = """
# MRPL Operations & Safety Demo Pack

## 2.2 Key operating parameters
Pump P-204B vibration average: 5.8 mm/s RMS. Normal operating threshold: below 4.5 mm/s RMS. Warning threshold crossed for 3rd time in 4 weeks.

## 3.1 Incident and near-miss register
ID | Date | Area | Event type | Description | Severity | Immediate action | Status
INC-01 | 07 Jul 2026 | Crude Transfer Area | Near miss | Minor hydrocarbon seepage observed at Pump P-204B flange during routine rounds. No ignition source present. | Medium | Pump isolated for inspection; absorbent pads deployed. | Closed
INC-02 | 11 Jul 2026 | Tank Farm Corridor | Housekeeping observation | Unsecured cable cover created a trip hazard near Tank T-17 access route. | Low | Area barricaded; cable cover re-secured. | Closed
INC-03 | 16 Jul 2026 | CDU-1 | PTW deviation | Night shift accepted a hot-work permit without a completed handover checklist. Work had not begun. | Medium | Permit suspended; checklist completed before restart. | Closed
INC-06 | 30 Jul 2026 | Tank Farm Corridor | Housekeeping observation | Oil-stained absorbent material remained in a designated walkway for more than 48 hours. | Low | Material removed; supervisor notified. | Closed
INC-07 | 04 Aug 2026 | Crude Transfer Area | Equipment alert | Pump P-204B vibration crossed internal warning threshold for the third time in four weeks. | High | Reduced load; maintenance work order raised. | Open
INC-08 | 08 Aug 2026 | CDU-1 | Procedural non-compliance | Confined-space preparation checklist missing contractor supervisor signature. | Medium | Entry postponed; signature obtained. | Closed
INC-10 | 17 Aug 2026 | Tank Farm Corridor | Recordable incident | Contract worker slipped on wet surface while carrying empty sampling containers; no lost workday. | Medium | Surface dried; anti-slip mat installed. | Closed
INC-12 | 23 Aug 2026 | CDU-1 | PTW deviation | Isolation tag number entered incorrectly in shift-handover register. | Medium | Tag verified; register corrected. | Closed
INC-13 | 26 Aug 2026 | Crude Transfer Area | Maintenance deviation | Vibration sensor calibration for Pump P-204B overdue by 12 days. | Medium | Calibration scheduled with maintenance team. | Open
INC-14 | 29 Aug 2026 | Utility Block | Housekeeping observation | Emergency access route partially obstructed by unused scaffolding material. | Medium | Material removed within 3 hours. | Closed
INC-15 | 31 Aug 2026 | Tank Farm Corridor | Near miss | Forklift operator reported reduced visibility due to temporary signage placement. | Low | Signage repositioned. | Closed
INC-16 | 02 Sep 2026 | CDU-1 | Recordable incident | Operator reported minor eye irritation from dust during sample-panel cleaning. PPE was worn but eyewash follow-up was required. | Medium | Eyewash used; cleaning method reviewed. | Closed
INC-18 | 04 Sep 2026 | Crude Transfer Area | Near miss | Small pooling of wash water found close to electrical junction box; no equipment contact. | Medium | Water removed; drainage inspection initiated. | Open

## 4.1 Pump P-204B recurring vibration
Pump P-204B is considered a critical priority due to recurring vibration levels (5.8 mm/s RMS vs 4.5 mm/s threshold). If left unresolved, risks include seal degradation, hydrocarbon leakage, unplanned unit shutdown, or escalation near ignition sources.
""".strip()


@pytest.fixture(autouse=True)
def setup_test_index():
    index_document(file_id="test_comp_doc", filename="MRPL_Operations_Safety_Demo_Pack.md", text=MRPL_DEMO_TEXT)


def test_single_topic_query_pump_p204b():
    """Test A: Pump P-204B single-topic query retrieves equipment/vibration evidence."""
    query = "What is the status of Pump P-204B vibration and maintenance?"
    results = search_documents(query=query, top_k=5)
    assert len(results) > 0
    text = " ".join(r["text"] for r in results)
    assert "P-204B" in text or "vibration" in text.lower()


def test_two_area_comparison_crude_vs_tank_farm():
    """Test B: Crude Transfer Area vs Tank Farm Corridor comparison query."""
    query = "Compare the safety issues in the Crude Transfer Area vs Tank Farm Corridor."
    agent_res = {"intent": "comparison", "tool": "document_comparison", "sources": search_documents(query, top_k=10)}
    res = generate_structured_response(query, agent_res, "req_test_b")
    
    assert "Operational Area Safety Comparison" in res["title"]
    assert len(res["comparison"]) >= 2
    areas = [c["area"] for c in res["comparison"]]
    assert "Crude Transfer Area" in areas
    assert "Tank Farm Corridor" in areas


def test_exact_three_area_comparison_query():
    """Test C: Exact 3-area comparison query returns grounded comparison with Crude Transfer priority."""
    query = "Compare the safety and operational issues observed in the Crude Transfer Area, Tank Farm Corridor, and CDU-1. Which area needs the most immediate attention and why?"
    
    agent_res = {"intent": "comparison", "tool": "document_comparison", "sources": search_documents(query, top_k=12)}
    res = generate_structured_response(query, agent_res, "req_test_c")

    assert res["title"] == "Operational Area Safety Comparison"
    assert len(res["comparison"]) == 3
    
    areas = [c["area"] for c in res["comparison"]]
    assert "Crude Transfer Area" in areas
    assert "Tank Farm Corridor" in areas
    assert "CDU-1" in areas

    crude_item = next(c for c in res["comparison"] if c["area"] == "Crude Transfer Area")
    assert crude_item["risk_level"] == "High"
    assert any("INC-01" in issue or "INC-07" in issue or "P-204B" in issue for issue in crude_item["issues"])

    assert "Crude Transfer Area" in res["answer"]
    assert "most immediate attention" in res["answer"]
    assert "No indexed evidence was found" not in res["answer"]
    assert len(res["sources"]) > 0


def test_nonexistent_area_query():
    """Test D: Query for a nonexistent area returns clear no-evidence response."""
    query = "Compare safety issues in Hydrocracker Unit 999."
    agent_res = {"intent": "document_question", "tool": "document_search", "sources": []}
    res = generate_structured_response(query, agent_res, "req_test_d")

    assert "No Evidence Found" in res["title"]
    assert "No indexed evidence was found" in res["answer"]
    assert len(res["comparison"]) == 0
    assert len(res["uncertainties"]) > 0
