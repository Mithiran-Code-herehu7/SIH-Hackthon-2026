import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.agent.orchestrator import (
    _calculator_arguments,
    _fallback_classify,
    _validate_decision,
    classify_intent,
    run_agent,
)
from app.api.v1.chat.router import generate_final_answer
from app.documents.visuals import ALLOWED_IMAGE_EXTENSIONS, save_image
from app.rag.chunker import chunk_text
from app.tools import registry
from app.tools.industrial_analysis import (
    analyze_evidence,
    compare_documents,
    generate_report,
)
from app.tools.industrial_calculator import industrial_calculator


# 1. All 10 tool registrations
def test_all_10_tools_registered():
    registered = {t["name"] for t in registry.list_tools()}
    expected_tools = {
        "document_search",
        "document_metadata",
        "industrial_calculator",
        "image_analysis",
        "process_analysis",
        "safety_analysis",
        "equipment_analysis",
        "procedure_lookup",
        "document_comparison",
        "report_generation",
    }
    assert expected_tools.issubset(registered), f"Missing tools: {expected_tools - registered}"
    for tool_name in expected_tools:
        tool = registry.get(tool_name)
        assert tool is not None
        assert callable(tool.handler)
        assert tool.description


# 2. Safe industrial calculations and invalid inputs
def test_safe_industrial_calculations_and_invalid_inputs():
    assert industrial_calculator("efficiency", 850, 1000)["result"] == 85
    assert industrial_calculator("ratio", 850, 1000)["result"] == 0.85
    assert industrial_calculator("mass_balance", 1000, 150)["result"] == 850
    assert industrial_calculator("percentage", 25, 200)["result"] == 50
    assert industrial_calculator("multiply", 5, 4)["result"] == 20
    assert industrial_calculator("divide", 10, 2)["result"] == 5
    assert industrial_calculator("convert_pressure", 1, 0, "bar", "kpa")["result"] == 100
    assert industrial_calculator("convert_temperature", 100, 0, "c", "f")["result"] == 212

    # Division by zero
    with pytest.raises(ValueError, match="Division by zero"):
        industrial_calculator("divide", 1, 0)
    with pytest.raises(ValueError, match="Division by zero"):
        industrial_calculator("efficiency", 100, 0)
    with pytest.raises(ValueError, match="Division by zero"):
        industrial_calculator("ratio", 100, 0)

    # Unsupported unit pairs
    with pytest.raises(ValueError, match="Unsupported pressure"):
        industrial_calculator("convert_pressure", 1, 0, "bar", "c")
    with pytest.raises(ValueError, match="Unsupported temperature"):
        industrial_calculator("convert_temperature", 100, 0, "c", "bar")

    # Non-finite inputs
    with pytest.raises(ValueError, match="finite"):
        industrial_calculator("multiply", float("nan"), 2)
    with pytest.raises(ValueError, match="finite"):
        industrial_calculator("multiply", 2, float("inf"))

    # Booleans rejected
    with pytest.raises(ValueError, match="numeric"):
        industrial_calculator("divide", True, 2)


# 3. Intent classification and tool matching for all intents
def test_every_industrial_intent_classification():
    # Process
    d_proc = _fallback_classify("What are the main stages and fractions produced by the CDU?")
    assert d_proc.intent == "process_analysis"
    assert d_proc.tool == "process_analysis"

    # Safety
    d_safe = _fallback_classify("What safety precautions are mentioned for CDU operation?")
    assert d_safe.intent == "safety_analysis"
    assert d_safe.tool == "safety_analysis"

    # Procedure
    d_proc_lk = _fallback_classify("What does the manual say about emergency response procedure?")
    assert d_proc_lk.intent == "procedure_lookup"
    assert d_proc_lk.tool == "procedure_lookup"

    # Equipment (without image)
    d_equip = _fallback_classify("What routine inspection is required for pump and valve equipment?")
    assert d_equip.intent == "equipment_analysis"
    assert d_equip.tool == "equipment_analysis"

    # Equipment (with image)
    d_equip_img = _fallback_classify("Inspect pump condition shown in photo", image_available=True)
    assert d_equip_img.intent == "equipment_analysis"
    assert d_equip_img.tool == "equipment_analysis"

    # Comparison
    d_comp = _fallback_classify("Compare the two documents for differences")
    assert d_comp.intent == "comparison"
    assert d_comp.tool == "document_comparison"

    # Report generation
    d_rep = _fallback_classify("Generate report for CDU operations")
    assert d_rep.intent == "report_generation"
    assert d_rep.tool == "report_generation"

    # Calculation
    d_calc = _fallback_classify("calculate efficiency: output 850 and input 1000")
    assert d_calc.intent == "calculation"
    assert d_calc.tool == "industrial_calculator"

    # Metadata
    d_meta = _fallback_classify("What is the filename and uploaded metadata?")
    assert d_meta.intent == "document_metadata"
    assert d_meta.tool == "document_metadata"

    # General question
    d_gen = _fallback_classify("Hello, how are you?")
    assert d_gen.intent == "general_question"
    assert d_gen.tool is None


# 4. Process analysis with evidence
def test_process_analysis_with_evidence():
    source = {
        "file_id": "doc-cdu-001",
        "filename": "cdu_process_manual.pdf",
        "chunk_index": 0,
        "score": 0.92,
        "text": (
            "Crude oil is processed in a crude distillation unit (CDU). "
            "The feed is preheated and heated in a furnace before entering the distillation column. "
            "Typical CDU fractions include refinery gas, naphtha, kerosene, diesel-range material and atmospheric gas oil."
        ),
    }
    result = analyze_evidence("process", [source])
    assert result["analysis_type"] == "process"
    assert len(result["findings"]) > 0
    assert result["findings"][0]["classification"] == "observed"
    assert result["findings"][0]["evidence"][0]["file_id"] == "doc-cdu-001"
    assert result["findings"][0]["evidence"][0]["filename"] == "cdu_process_manual.pdf"
    assert result["disclaimer"]


# 5. Process analysis with no evidence
def test_process_analysis_with_no_evidence():
    result = analyze_evidence("process", [])
    assert result["analysis_type"] == "process"
    assert len(result["findings"]) == 0
    assert len(result["uncertainties"]) > 0
    assert "No retrieved document evidence was available" in result["uncertainties"][0]


# 6. Safety analysis (hazards, warnings, PPE, limits, emergency, evidence, no fabrication)
def test_safety_analysis_comprehensive():
    source = {
        "file_id": "safe-001",
        "filename": "safety_rules.pdf",
        "chunk_index": 1,
        "score": 0.88,
        "text": (
            "Warning: wear PPE including safety helmet, safety footwear, and eye protection. "
            "Operators must verify alarms and emergency shutdown systems. "
            "Hazard: any abnormal pressure or leak must be reported immediately. "
            "Operating limit: CDU furnace outlet temperature 350-370 C."
        ),
    }
    result = analyze_evidence("safety", [source])
    assert result["analysis_type"] == "safety"
    assert len(result["findings"]) > 0
    for finding in result["findings"]:
        assert finding["classification"] == "observed"
        assert finding["evidence"][0]["file_id"] == "safe-001"
    # Document warnings extracted
    assert any("warning" in w.lower() for w in result["warnings"])
    assert result["disclaimer"]

    # Never fabricate safety procedures when empty
    empty_safety = analyze_evidence("safety", [])
    assert len(empty_safety["findings"]) == 0
    assert any("never be fabricated" in u.lower() for u in empty_safety["uncertainties"])


# 7. Procedure lookup prioritizes retrieved evidence
def test_procedure_lookup_prioritizes_evidence():
    source = {
        "file_id": "proc-001",
        "filename": "sop_manual.pdf",
        "chunk_index": 2,
        "score": 0.95,
        "text": "When a significant process upset is detected, personnel should follow emergency response procedure and evacuate area.",
    }
    result = analyze_evidence("procedure", [source])
    assert result["analysis_type"] == "procedure"
    assert len(result["findings"]) > 0
    assert result["findings"][0]["classification"] == "observed"
    assert "emergency response procedure" in result["findings"][0]["statement"].lower()


# 8. Equipment analysis (with and without visual artifact; observed vs inferred vs uncertain)
def test_equipment_analysis_with_and_without_visual():
    doc_source = {
        "file_id": "equip-doc",
        "filename": "maintenance.pdf",
        "chunk_index": 0,
        "score": 0.85,
        "text": "Routine inspection should check pumps, valves, and rotating equipment for abnormal vibration and leaks.",
    }
    # Without image
    result_no_img = analyze_evidence("equipment", [doc_source], image_result=None)
    assert result_no_img["analysis_type"] == "equipment"
    assert all(f["classification"] == "observed" for f in result_no_img["findings"])

    # With image
    image_result = {"analysis": "Surface rust and corrosion on centrifugal pump casing."}
    result_img = analyze_evidence("equipment", [doc_source], image_result=image_result)
    assert any(f["classification"] == "observed" for f in result_img["findings"])
    inferred_findings = [f for f in result_img["findings"] if f["classification"] == "inferred"]
    assert len(inferred_findings) == 1
    assert "Surface rust" in inferred_findings[0]["statement"]
    assert inferred_findings[0]["evidence"] == []
    assert any("do not prove equipment condition" in u.lower() for u in result_img["uncertainties"])


# 9. Document comparison requires two documents
def test_comparison_requires_two_documents():
    doc1 = {
        "file_id": "doc-a",
        "filename": "manual_a.txt",
        "chunk_index": 0,
        "score": 0.9,
        "text": "Emergency shutdown valve procedure for pump maintenance and pressure relief.",
    }
    # Only 1 document
    res_one = compare_documents([doc1])
    assert len(res_one["findings"]) == 0
    assert any("at least two distinct documents" in u for u in res_one["uncertainties"])

    # 2 documents
    doc2 = {
        "file_id": "doc-b",
        "filename": "manual_b.txt",
        "chunk_index": 0,
        "score": 0.85,
        "text": "Routine inspection of distillation column and emergency response protocol.",
    }
    res_two = compare_documents([doc1, doc2])
    assert len(res_two["findings"]) > 0
    assert res_two["findings"][0]["classification"] == "observed"
    assert len(res_two["evidence"]) == 2
    assert "manual_a.txt" in str(res_two["findings"]) or "Shared" in str(res_two["findings"])


# 10. Report generation structure
def test_report_generation_structure():
    doc_source = {
        "file_id": "doc-rep",
        "filename": "refinery.pdf",
        "chunk_index": 0,
        "score": 0.9,
        "text": "CDU operates at atmospheric pressure with furnace preheating.",
    }
    analysis = analyze_evidence("process", [doc_source])
    calc = industrial_calculator("efficiency", 850, 1000)

    report = generate_report(
        request_id="req-12345",
        question="What are CDU conditions?",
        analyses=[analysis],
        calculations=[calc],
    )
    assert report["request_id"] == "req-12345"
    assert report["objective"] == "What are CDU conditions?"
    assert len(report["findings"]) > 0
    assert len(report["calculations"]) == 1
    assert report["calculations"][0]["result"] == 85
    assert len(report["evidence"]) > 0
    assert len(report["risks_warnings"]) > 0
    assert len(report["assumptions"]) > 0
    assert "generated_at" in report
    assert "conclusion" in report


# 11. Strict intent/tool mismatch rejection
def test_strict_intent_tool_mismatch_rejection():
    registered = {t["name"] for t in registry.list_tools()}
    # Mismatch between intent and tool
    with pytest.raises(ValueError, match="mismatch"):
        _validate_decision({"intent": "process_analysis", "tool": "industrial_calculator", "reason": "test"}, registered)

    # Unregistered tool
    with pytest.raises(ValueError, match="unregistered"):
        _validate_decision({"intent": "process_analysis", "tool": "unregistered_custom_tool", "reason": "test"}, registered)

    # Invalid intent
    with pytest.raises(ValueError, match="invalid intent"):
        _validate_decision({"intent": "execute_code", "tool": "code_runner", "reason": "test"}, registered)

    # Image analysis without image available
    with pytest.raises(ValueError, match="without an image artifact"):
        _validate_decision({"intent": "image_analysis", "tool": "image_analysis", "reason": "test"}, registered, image_available=False)


# 12. Calculator argument extraction regexes
def test_calculator_argument_extraction():
    eff = _calculator_arguments("calculate efficiency for output 850 and input 1000")
    assert eff is not None
    assert eff["operation"] == "efficiency"
    assert eff["value_a"] == 850
    assert eff["value_b"] == 1000

    ratio = _calculator_arguments("calculate ratio of 850 to 1000")
    assert ratio is not None
    assert ratio["operation"] == "ratio"
    assert ratio["value_a"] == 850
    assert ratio["value_b"] == 1000

    press = _calculator_arguments("convert 1 bar to kpa")
    assert press is not None
    assert press["operation"] == "convert_pressure"
    assert press["value_a"] == 1
    assert press["input_unit"] == "bar"
    assert press["output_unit"] == "kpa"

    temp = _calculator_arguments("convert 100 c to f")
    assert temp is not None
    assert temp["operation"] == "convert_temperature"
    assert temp["value_a"] == 100
    assert temp["input_unit"] == "c"
    assert temp["output_unit"] == "f"

    mb = _calculator_arguments("mass-balance of 1000 minus 150")
    assert mb is not None
    assert mb["operation"] == "mass_balance"
    assert mb["value_a"] == 1000
    assert mb["value_b"] == 150


# 13. Controlled multi-step execution order in run_agent
@pytest.mark.asyncio
async def test_controlled_orchestrator_multi_step_execution():
    # Efficiency calculation: only industrial_calculator executed
    res_calc = await run_agent("efficiency of 850 and 1000")
    assert res_calc["tool_execution_status"] == "success"
    assert res_calc["tools_executed"] == ["industrial_calculator"]
    assert res_calc["execution_order"] == ["industrial_calculator"]
    assert res_calc["tool_result"]["result"] == 85

    # Process query: document_search -> process_analysis
    with patch("app.agent.orchestrator.classify_intent") as mock_classify:
        from app.agent.orchestrator import AgentDecision
        mock_classify.return_value = AgentDecision(
            intent="process_analysis",
            tool="process_analysis",
            reason="test process",
            arguments={},
        )
        with patch("app.agent.orchestrator.registry.execute") as mock_exec:
            mock_exec.side_effect = [
                [{"file_id": "f1", "filename": "m.pdf", "chunk_index": 0, "score": 0.9, "text": "CDU distillation column process."}],
                {"analysis_type": "process", "findings": []},
            ]
            res_proc = await run_agent("What are CDU stages?")
            assert res_proc["tools_executed"] == ["document_search", "process_analysis"]
            assert res_proc["execution_order"] == ["document_search", "process_analysis"]

    # Equipment with image: image_analysis -> document_search -> equipment_analysis
    with patch("app.agent.orchestrator.classify_intent") as mock_classify:
        mock_classify.return_value = AgentDecision(
            intent="equipment_analysis",
            tool="equipment_analysis",
            reason="test equip with image",
            arguments={},
        )
        with patch("app.agent.orchestrator.registry.execute") as mock_exec:
            mock_exec.side_effect = [
                {"analysis": "pump photo analysis"},
                [{"file_id": "f1", "filename": "m.pdf", "chunk_index": 0, "score": 0.9, "text": "Pump maintenance inspection."}],
                {"analysis_type": "equipment", "findings": []},
            ]
            res_equip = await run_agent("Inspect pump condition", image_ref="images/pump.png")
            assert res_equip["tools_executed"] == ["image_analysis", "document_search", "equipment_analysis"]
            assert res_equip["execution_order"] == ["image_analysis", "document_search", "equipment_analysis"]
            assert res_equip["visual_artifact_ids"] == ["images/pump.png"]


# 14. Final answer formatting
def test_final_answer_formatting():
    # Calculation
    calc_res = {"tool": "industrial_calculator", "sources": [], "tool_execution_status": "success", "failure": None, "tool_result": {"operation": "efficiency", "value_a": 850, "value_b": 1000, "result": 85}}
    ans_calc = generate_final_answer("efficiency", calc_res)
    assert "85%" in ans_calc

    # Ratio
    ratio_res = {"tool": "industrial_calculator", "sources": [], "tool_execution_status": "success", "failure": None, "tool_result": {"operation": "ratio", "value_a": 850, "value_b": 1000, "result": 0.85}}
    ans_ratio = generate_final_answer("ratio", ratio_res)
    assert "0.85" in ans_ratio

    # Process findings with OBSERVED prefix
    proc_res = {
        "tool": "process_analysis",
        "sources": [],
        "tool_execution_status": "success",
        "failure": None,
        "tool_result": {
            "findings": [{"classification": "observed", "statement": "CDU processes crude oil."}],
            "warnings": [],
            "uncertainties": [],
        },
    }
    ans_proc = generate_final_answer("CDU query", proc_res)
    assert "[OBSERVED]" in ans_proc
    assert "CDU processes crude oil." in ans_proc

    # Report generation formatting
    rep_res = {
        "tool": "report_generation",
        "sources": [],
        "tool_execution_status": "success",
        "failure": None,
        "tool_result": {
            "title": "Industrial Analysis Report: CDU",
            "objective": "Evaluate CDU",
            "findings": [{"classification": "observed", "statement": "Column separates hydrocarbons."}],
            "risks_warnings": ["Operating risk"],
            "uncertainties": ["Uncertainty note"],
            "conclusion": "Conclusion statement.",
        },
    }
    ans_rep = generate_final_answer("generate report", rep_res)
    assert "=== Industrial Analysis Report: CDU ===" in ans_rep
    assert "Key Findings:" in ans_rep
    assert "[OBSERVED] Column separates hydrocarbons." in ans_rep


# 15. RAG chunker integration
def test_rag_chunker_integration():
    sample_text = (
        "Section 1. Plant Operation Overview\n"
        "Crude distillation units operate continuously under bounded temperature and pressure conditions.\n"
        "The atmospheric tower separates various hydrocarbons based on boiling ranges.\n\n"
        "Section 2. Safety Regulations\n"
        "All operators must wear mandatory personal protective equipment including helmet and flame-resistant clothing.\n"
        "Emergency shutdown valves and safety relief systems must be inspected regularly.\n"
    )
    chunks = chunk_text(sample_text, chunk_size=150, overlap=30)
    assert len(chunks) >= 2
    assert all(isinstance(c, str) for c in chunks)


# 16. Image handling validation
def test_image_handling_validation():
    assert ".png" in ALLOWED_IMAGE_EXTENSIONS
    assert ".jpg" in ALLOWED_IMAGE_EXTENSIONS
    assert ".jpeg" in ALLOWED_IMAGE_EXTENSIONS
    assert ".webp" in ALLOWED_IMAGE_EXTENSIONS

    # Reject invalid extension
    with pytest.raises(ValueError, match="Unsupported image type"):
        save_image("malicious.exe", b"fake binary")

    # Reject empty content
    with pytest.raises(ValueError, match="non-empty"):
        save_image("photo.png", b"")


# 17. FastAPI app import and route structure
def test_fastapi_app_import_and_routes():
    from app.main import app
    assert app.title == "Sovereign AI Workbench"
    paths = list(app.openapi()["paths"].keys())
    assert "/" in paths
    assert "/api/v1/chat" in paths
    assert "/api/v1/documents/search" in paths
    assert "/api/v1/images/analyze" in paths
    assert "/api/v1/audit/{request_id}" in paths



# 18. Audit logging metadata and confidentiality check
@pytest.mark.asyncio
async def test_audit_logging_and_confidentiality():
    import json
    from app.core.audit import log_audit
    from app.storage.database import AsyncSessionLocal, init_db
    from app.storage.models import AuditLog
    from sqlalchemy import select

    import uuid
    await init_db()
    async with AsyncSessionLocal() as session:
        req_id = f"test-audit-{uuid.uuid4()}"
        details = {
            "intent": "safety_analysis",
            "tool": "safety_analysis",
            "tools_executed": ["document_search", "safety_analysis"],
            "execution_order": ["document_search", "safety_analysis"],
            "source_document_ids": ["doc-123"],
            "visual_artifact_ids": [],
            "calculation_operations": [],
            "provider": "OllamaLLMProvider (qwen3:8b)",
        }
        await log_audit(
            db=session,
            request_id=req_id,
            action="agent_chat",
            status="success",
            details=details,
        )

        res = await session.execute(select(AuditLog).where(AuditLog.request_id == req_id))
        audit_entry = res.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.action == "agent_chat"
        assert audit_entry.status == "success"
        parsed_details = json.loads(audit_entry.details)
        assert parsed_details["intent"] == "safety_analysis"
        assert parsed_details["tools_executed"] == ["document_search", "safety_analysis"]
        assert parsed_details["source_document_ids"] == ["doc-123"]
        # Ensure confidentiality: NO raw document text content is stored in audit
        assert "text" not in parsed_details
        assert "raw_content" not in parsed_details
        assert "content" not in parsed_details



