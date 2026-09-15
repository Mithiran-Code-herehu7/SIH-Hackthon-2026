import os
from pathlib import Path
import pytest
import openpyxl

from app.agent.orchestrator import classify_intent, run_agent
from app.api.v1.chat.router import generate_structured_response
from app.config import settings
from app.rag.service import index_document, search_documents
from app.tools.excel_generator import generate_excel_workbook, INCIDENT_RECORDS


# Sample MRPL document text containing Sections 3.1 & 3.2 as well as instructional demo text
MRPL_FULL_DEMO_TEXT = """
# MRPL Operations & Safety Demo Pack

## 1. Executive summary
Reporting period: July–August 2026. Recorded 18 safety and operational observations.

## 3. Incident and near-miss register
### 3.1 Incident and near-miss register
ID | Date | Area | Event type | Description | Severity | Immediate action | Status
INC-01 | 07 Jul 2026 | Crude Transfer Area | Near miss | Minor hydrocarbon seepage observed at Pump P-204B flange during routine rounds. No ignition source present. | Medium | Pump isolated for inspection; absorbent pads deployed. | Closed
INC-02 | 11 Jul 2026 | Tank Farm Corridor | Housekeeping observation | Unsecured cable cover created a trip hazard near Tank T-17 access route. | Low | Area barricaded; cable cover re-secured. | Closed
INC-03 | 16 Jul 2026 | CDU-1 | PTW deviation | Night shift accepted a hot-work permit without a completed handover checklist. Work had not begun. | Medium | Permit suspended; checklist completed before restart. | Closed
INC-04 | 21 Jul 2026 | Utility Block | Recordable incident | Technician sustained a minor hand laceration while removing insulation near a steam-line support. First aid provided. | Medium | Work stopped; tool inspection and PPE briefing conducted. | Closed
INC-05 | 25 Jul 2026 | Maintenance Workshop | Near miss | Chain block hook safety latch found partially damaged before lifting operation. | High | Lifting activity stopped; chain block quarantined. | Closed
INC-06 | 30 Jul 2026 | Tank Farm Corridor | Housekeeping observation | Oil-stained absorbent material remained in a designated walkway for more than 48 hours. | Low | Material removed; supervisor notified. | Closed
INC-07 | 04 Aug 2026 | Crude Transfer Area | Equipment alert | Pump P-204B vibration crossed internal warning threshold for the third time in four weeks. | High | Reduced load; maintenance work order raised. | Open
INC-08 | 08 Aug 2026 | CDU-1 | Procedural non-compliance | Confined-space preparation checklist missing contractor supervisor signature. | Medium | Entry postponed; signature obtained. | Closed
INC-09 | 12 Aug 2026 | Utility Block | Near miss | Temporary electrical cable was routed across a wet floor near cooling-water skid. | Medium | Cable rerouted; insulation check completed. | Closed
INC-10 | 17 Aug 2026 | Tank Farm Corridor | Recordable incident | Contract worker slipped on wet surface while carrying empty sampling containers; no lost workday. | Medium | Surface dried; anti-slip mat installed. | Closed
INC-11 | 19 Aug 2026 | Maintenance Workshop | Lifting deviation | Lift plan lacked updated equipment weight verification. No lift started. | High | Plan corrected and approved before work resumed. | Closed
INC-12 | 23 Aug 2026 | CDU-1 | PTW deviation | Isolation tag number entered incorrectly in shift-handover register. | Medium | Tag verified; register corrected. | Closed
INC-13 | 26 Aug 2026 | Crude Transfer Area | Maintenance deviation | Vibration sensor calibration for Pump P-204B overdue by 12 days. | Medium | Calibration scheduled with maintenance team. | Open
INC-14 | 29 Aug 2026 | Utility Block | Housekeeping observation | Emergency access route partially obstructed by unused scaffolding material. | Medium | Material removed within 3 hours. | Closed
INC-15 | 31 Aug 2026 | Tank Farm Corridor | Near miss | Forklift operator reported reduced visibility due to temporary signage placement. | Low | Signage repositioned. | Closed
INC-16 | 02 Sep 2026 | CDU-1 | Recordable incident | Operator reported minor eye irritation from dust during sample-panel cleaning. PPE was worn but eyewash follow-up was required. | Medium | Eyewash used; cleaning method reviewed. | Closed
INC-17 | 03 Sep 2026 | Maintenance Workshop | Procedural non-compliance | Contractor toolbox talk record was not uploaded before hot-work activity. | Low | Upload completed; contractor supervisor counselled. | Closed
INC-18 | 04 Sep 2026 | Crude Transfer Area | Near miss | Small pooling of wash water found close to electrical junction box; no equipment contact. | Medium | Water removed; drainage inspection initiated. | Open

### 3.2 Event summary by category
- Recordable incidents: 3
- Near misses: 5
- Maintenance deviations / equipment alerts: 2
- PTW / procedural non-compliances: 5
- Housekeeping observations: 3

## 5. Compliance scorecard
- Permit-to-work handover completion: 94% (Target 100%, Amber)
- Confined-space checklist completion: 88% (Target 100%, Red)

## 6. Corrective action plan
- CAP-01: Calibrate Pump P-204B vibration sensor by 08 Sep 2026.
""".strip()


def test_excel_generation_task_classification_and_tool_execution():
    query = (
        "Create an Excel workbook containing the incident register, compliance scorecard, and corrective-action tracker."
    )

    # 1. Verify task classification
    decision = classify_intent(query)
    assert decision.intent == "generate_excel"
    assert decision.tool == "generate_excel"

    # 2. Ingest test document and run agent
    file_id = "test-mrpl-excel-doc"
    filename = "MRPL_Operations_Safety_Demo_Pack.md"
    chunks = index_document(file_id=file_id, filename=filename, text=MRPL_FULL_DEMO_TEXT)
    assert chunks > 0

    # 3. Test generate_excel_workbook directly
    tool_res = generate_excel_workbook(filename="Operational_Safety_Tracker_September_2026.xlsx")
    assert tool_res["task_type"] == "generate_excel"
    assert tool_res["requires_file"] is True
    assert tool_res["requested_format"] == "xlsx"
    assert tool_res["requested_sheets"] in (["Incident Register", "Compliance Scorecard", "Corrective Actions"], ["Incident Register", "Event Summary", "Severity Summary"])

    excel_path = Path(tool_res["file_path"])
    assert excel_path.exists()

    # 4. Inspect generated openpyxl workbook
    wb = openpyxl.load_workbook(excel_path)
    assert "Incident Register" in wb.sheetnames
    assert len(wb.sheetnames) >= 3

    ws1 = wb["Incident Register"]
    expected_headers = ["ID", "Date", "Area", "Event Type", "Description", "Severity", "Immediate Action", "Status"]
    actual_headers = [ws1.cell(row=3, column=c).value for c in range(1, 9)]
    assert actual_headers == expected_headers or [ws1.cell(row=1, column=c).value for c in range(1, 9)] == expected_headers

    ws2 = wb[wb.sheetnames[1]]
    assert ws2.max_row >= 4

    ws3 = wb[wb.sheetnames[2]]
    assert ws3.max_row >= 4

    wb.close()

    # 5. Verify generate_structured_response formatting
    agent_result = {
        "intent": "generate_excel",
        "tool": "generate_excel",
        "reason": "Excel creation request",
        "sources": [{"filename": filename, "file_id": file_id, "chunk_index": 0}],
        "tool_result": tool_res,
        "tool_execution_status": "success",
    }
    res = generate_structured_response(query, agent_result, "req_excel_test_01")

    assert res["task_type"] == "generate_excel"
    assert res["requires_file"] is True
    assert res["requested_format"] == "xlsx"
    assert res["requested_sheets"] in (["Incident Register", "Compliance Scorecard", "Corrective Actions"], ["Incident Register", "Event Summary", "Severity Summary"])
    assert "created an Excel workbook" in res["answer"]
    assert len(res["files"]) == 1
    assert res["files"][0]["type"] == "excel"

    # Verify sources cite Sections 3.1, 5 & 6
    assert len(res["sources"]) == 3
    sections = [s["section"] for s in res["sources"]]
    assert "3.1 Incident and near-miss register" in sections
    assert "5 Compliance scorecard" in sections
    assert "6 Corrective action plan" in sections


@pytest.mark.asyncio
async def test_full_flow_end_to_end(async_client=None):
    """Verify full workflow: classify -> extract -> generate Excel -> return file response."""
    query = "Create an Excel file containing the incident register, compliance scorecard, and corrective actions."
    
    # 1. Classify
    decision = classify_intent(query)
    assert decision.intent == "generate_excel"

    # 2. Run agent
    agent_res = await run_agent(query=query, top_k=5)
    assert agent_res["intent"] == "generate_excel"
    assert agent_res["tool"] == "generate_excel"
    assert agent_res["tool_execution_status"] == "success"

    # 3. Generate response
    res = generate_structured_response(query, agent_res, "req_e2e_01")
    assert res["task_type"] == "generate_excel"
    assert len(res["files"]) == 1
    assert res["files"][0]["type"] == "excel"
    assert res["files"][0]["download_url"].startswith("/files/")
    assert res["files"][0]["download_url"].endswith(".xlsx")
    assert "created an Excel workbook" in res["answer"]


def test_excel_tool_failure_fallback_message():
    query = "Create an Excel file containing the incident register."
    failed_agent_result = {
        "intent": "generate_excel",
        "tool": "generate_excel",
        "reason": "Excel creation request",
        "sources": [],
        "tool_result": None,
        "tool_execution_status": "failed",
    }
    res = generate_structured_response(query, failed_agent_result, "req_failed_01")
    assert res["answer"] == "I found the relevant evidence, but the local Excel generation tool failed. No workbook was created."
