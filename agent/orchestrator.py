import json
import re
from dataclasses import dataclass
from math import isfinite
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.provider import get_llm_provider
from app.tools import registry
from app.tools.industrial_calculator import ALLOWED_OPERATIONS


Intent = Literal[
    "document_question",
    "document_metadata",
    "calculation",
    "process_analysis",
    "safety_analysis",
    "equipment_analysis",
    "procedure_lookup",
    "comparison",
    "report_generation",
    "image_analysis",
    "general_question",
]

_TOOL_BY_INTENT: dict[str, str | None] = {
    "document_question": "document_search",
    "document_metadata": "document_metadata",
    "calculation": "industrial_calculator",
    "process_analysis": "process_analysis",
    "safety_analysis": "safety_analysis",
    "equipment_analysis": "equipment_analysis",
    "procedure_lookup": "procedure_lookup",
    "comparison": "document_comparison",
    "report_generation": "report_generation",
    "image_analysis": "image_analysis",
    "general_question": None,
}


@dataclass
class AgentDecision:
    intent: Intent
    tool: str | None
    reason: str
    arguments: dict[str, Any]


def _number(value: Any) -> float:
    """Convert an LLM or parser value to a finite numeric input."""
    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid calculation inputs.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Calculation values must be numeric.") from exc
    if not isfinite(number):
        raise ValueError("Calculation values must be finite.")
    return number


def _calculator_arguments(query: str) -> dict[str, Any] | None:
    """Extract only supported human-readable calculation requests."""
    number = r"([-+]?(?:\d+(?:\.\d+)?|\.\d+))"

    # Pressure conversions
    m_press = re.search(
        rf"(?:convert|change)?\s*{number}\s*(bar|kpa|psi)\s+(?:to|in|into)\s*(bar|kpa|psi)",
        query, flags=re.IGNORECASE,
    )
    if m_press:
        return {
            "operation": "convert_pressure",
            "value_a": _number(m_press.group(1)),
            "value_b": 0.0,
            "input_unit": m_press.group(2).lower(),
            "output_unit": m_press.group(3).lower(),
        }

    # Temperature conversions
    m_temp = re.search(
        rf"(?:convert|change)?\s*{number}\s*(?:°|deg|degrees)?\s*([cfk])\s+(?:to|in|into)\s*(?:°|deg|degrees)?\s*([cfk])",
        query, flags=re.IGNORECASE,
    )
    if m_temp:
        return {
            "operation": "convert_temperature",
            "value_a": _number(m_temp.group(1)),
            "value_b": 0.0,
            "input_unit": m_temp.group(2).lower(),
            "output_unit": m_temp.group(3).lower(),
        }

    # Efficiency
    m_eff = re.search(
        rf"efficiency\b[^\d\-+]*{number}[^\d\-+]+(?:input\s*)?{number}",
        query, flags=re.IGNORECASE,
    )
    if m_eff:
        return {
            "operation": "efficiency",
            "value_a": _number(m_eff.group(1)),
            "value_b": _number(m_eff.group(2)),
        }

    # Ratio
    m_ratio = re.search(
        rf"ratio\b[^\d\-+]*{number}[^\d\-+]+{number}",
        query, flags=re.IGNORECASE,
    )
    if m_ratio:
        return {
            "operation": "ratio",
            "value_a": _number(m_ratio.group(1)),
            "value_b": _number(m_ratio.group(2)),
        }

    # Mass balance
    m_mb = re.search(
        rf"mass[- ]?balance\b[^\d\-+]*{number}[^\d\-+]+{number}",
        query, flags=re.IGNORECASE,
    )
    if m_mb:
        return {
            "operation": "mass_balance",
            "value_a": _number(m_mb.group(1)),
            "value_b": _number(m_mb.group(2)),
        }

    # Flow rate
    m_flow = re.search(
        rf"flow[- ]?rate\b[^\d\-+]*{number}[^\d\-+]+{number}",
        query, flags=re.IGNORECASE,
    )
    if m_flow:
        return {
            "operation": "flow_rate",
            "value_a": _number(m_flow.group(1)),
            "value_b": _number(m_flow.group(2)),
        }

    # Percentage, divide, multiply
    patterns = (
        ("percentage", rf"{number}\s*%\s+of\s+{number}"),
        ("percentage", rf"{number}\s+percent\s+of\s+{number}"),

        ("divide", rf"{number}\s+(?:divided\s+by|/)\s*{number}"),
        ("multiply", rf"{number}\s+(?:multiplied\s+by|times|x|\*)\s*{number}"),
    )
    for operation, pattern in patterns:
        match = re.search(pattern, query, flags=re.IGNORECASE)
        if match:
            return {
                "operation": operation,
                "value_a": _number(match.group(1)),
                "value_b": _number(match.group(2)),
            }
    return None


def _fallback_classify(query: str, image_available: bool = False) -> AgentDecision:
    """Safe deterministic fallback when the local LLM decision is unusable."""
    query_lower = query.lower()
    is_report = (
        bool(re.search(r"\b(?:generate|create|produce|compile|write)\s+(?:an?\s+)?report\b", query_lower))
        or any(keyword in query_lower for keyword in ("generate report", "create report", "analysis report", "produce report", "report generation"))
    )
    if is_report:
        return AgentDecision("report_generation", "report_generation", "Fallback classifier identified structured report generation.", {})

    calculation = _calculator_arguments(query)
    if calculation:
        return AgentDecision(
            intent="calculation",
            tool="industrial_calculator",
            reason="Fallback classifier identified a supported calculation.",
            arguments=calculation,
        )
    if any(keyword in query_lower for keyword in ("compare", "comparison", "similarities", "differences", "versus", "vs ")):
        return AgentDecision("comparison", "document_comparison", "Fallback classifier identified a bounded document comparison.", {})
    if any(keyword in query_lower for keyword in ("hazard", "ppe", "safety precaution", "safety analysis", "safety", "precaution", "alarm")):
        return AgentDecision("safety_analysis", "safety_analysis", "Fallback classifier identified a safety evidence request.", {})
    if any(keyword in query_lower for keyword in ("emergency shutdown", "emergency response", "procedure", "instruction", "manual step", "steps")):
        return AgentDecision("procedure_lookup", "procedure_lookup", "Fallback classifier identified a procedure lookup.", {})
    if any(keyword in query_lower for keyword in ("equipment", "inspect", "condition", "pump", "valve", "compressor", "vessel", "heat exchanger")):
        return AgentDecision("equipment_analysis", "equipment_analysis", "Fallback classifier identified equipment analysis.", {})
    if any(keyword in query_lower for keyword in ("cdu", "distillation", "fractions", "main stages", "process analysis", "stages produced", "crude")):
        return AgentDecision("process_analysis", "process_analysis", "Fallback classifier identified process analysis.", {})
    visual_keywords = ["image", "diagram", "flow diagram", "shown", "visible", "inspection photo"]
    if image_available and any(keyword in query_lower for keyword in visual_keywords):
        return AgentDecision(
            intent="image_analysis", tool="image_analysis",
            reason="Fallback classifier identified a request for supplied visual evidence.",
            arguments={},
        )
    metadata_keywords = [
        "metadata", "file size", "file type", "filename", "uploaded",
        "when was", "document information",
    ]
    document_keywords = [
        "document", "file", "report", "procedure", "manual", "refinery",
        "process", "policy", "safety", "equipment", "maintenance", "inspection",
        "crude", "distillation", "fraction",
    ]
    if any(keyword in query_lower for keyword in metadata_keywords):
        return AgentDecision(
            intent="document_metadata", tool="document_metadata",
            reason="Fallback classifier identified a document metadata request.",
            arguments={},
        )
    if any(keyword in query_lower for keyword in document_keywords):
        return AgentDecision(
            intent="document_question", tool="document_search",
            reason="Fallback classifier identified a document content request.",
            arguments={},
        )
    return AgentDecision(
        intent="general_question", tool=None,
        reason="No available tool is required.", arguments={},
    )


def _validate_decision(data: Any, registered_tools: set[str], image_available: bool = False) -> AgentDecision:
    """Validate untrusted LLM output before it can reach the tool registry."""
    if not isinstance(data, dict):
        raise ValueError("LLM decision must be a JSON object.")
    intent = data.get("intent")
    tool = data.get("tool")
    reason = data.get("reason")
    arguments = data.get("arguments", {})
    if intent not in _TOOL_BY_INTENT:
        raise ValueError("LLM returned an invalid intent.")
    if intent == "image_analysis" and not image_available:
        raise ValueError("LLM selected image analysis without an image artifact.")
    if tool is not None and tool not in registered_tools:
        raise ValueError("LLM returned an unregistered tool.")
    if tool != _TOOL_BY_INTENT[intent]:
        raise ValueError("LLM returned a tool/intent mismatch.")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("LLM decision is missing a reason.")
    if not isinstance(arguments, dict):
        raise ValueError("LLM tool arguments must be an object.")
    if intent == "calculation":
        operation = arguments.get("operation")
        if not isinstance(operation, str) or operation.strip().lower() not in ALLOWED_OPERATIONS:
            raise ValueError("LLM returned an unsupported calculation operation.")
        op_clean = operation.strip().lower()
        val_a = _number(arguments.get("value_a"))
        val_b = _number(arguments.get("value_b", 0) if "convert" in op_clean else arguments.get("value_b"))
        args_clean: dict[str, Any] = {
            "operation": op_clean,
            "value_a": val_a,
            "value_b": val_b,
        }
        if "input_unit" in arguments:
            args_clean["input_unit"] = str(arguments["input_unit"]).strip().lower()
        if "output_unit" in arguments:
            args_clean["output_unit"] = str(arguments["output_unit"]).strip().lower()
        arguments = args_clean
    elif arguments:
        raise ValueError("This intent does not accept tool arguments.")
    return AgentDecision(intent=intent, tool=tool, reason=reason.strip(), arguments=arguments)


def classify_intent(query: str, image_available: bool = False) -> AgentDecision:
    """Use local Qwen for selection, then strictly validate its structured output."""
    tools = registry.list_tools()
    tool_descriptions = "\n".join(f"- {tool['name']}: {tool['description']}" for tool in tools)
    prompt = f"""
You are the decision component of a sovereign industrial AI system.
Choose exactly one allowed intent and its matching tool. Never execute code or commands.

Available registered tools:
{tool_descriptions}

Allowed intent/tool pairs:
- document_question / document_search: General questions answered by document text search.
- document_metadata / document_metadata: Document upload date, file size, or filename queries.
- calculation / industrial_calculator: Deterministic math (efficiency, ratio, percentage, mass_balance, unit conversions).
- process_analysis / process_analysis: Industrial processes, crude distillation, stages, fractions, column feeds/products.
- safety_analysis / safety_analysis: Safety precautions, PPE, hazards, operating limits, alarms.
- equipment_analysis / equipment_analysis: Equipment inspection, condition, pumps, valves, rotating equipment.
- procedure_lookup / procedure_lookup: Step-by-step operating procedures, emergency shutdown, emergency response steps.
- comparison / document_comparison: Comparing multiple documents, procedures, or specifications.
- report_generation / report_generation: Requests to generate an analysis or summary report.
- image_analysis / image_analysis: Direct visual analysis of a supplied image artifact (only when available).
- general_question / null: Generic conversation, greetings, or non-technical questions.

For calculation, return arguments with operation (percentage, efficiency, ratio, mass_balance, divide, multiply, convert_pressure, convert_temperature) and numeric values:
{{"intent":"calculation","tool":"industrial_calculator","reason":"short explanation","arguments":{{"operation":"efficiency","value_a":850,"value_b":1000}}}}
For all non-calculation intents, use empty arguments: {{}}.

Return ONLY a single valid JSON object:
{{"intent":"process_analysis","tool":"process_analysis","reason":"User is asking about CDU stages and fractions.","arguments":{{}}}}

User request:
{query}
""".strip()
    try:
        response = get_llm_provider().generate(prompt).strip()
        if response.startswith("```"):
            response = re.sub(r"^```(?:json)?\s*|\s*```$", "", response, flags=re.IGNORECASE)
        return _validate_decision(json.loads(response), {tool["name"] for tool in tools}, image_available=image_available)
    except Exception:
        return _fallback_classify(query, image_available=image_available)


async def run_agent(
    query: str,
    top_k: int = 5,
    db: AsyncSession | None = None,
    file_id: str | None = None,
    image_ref: str | None = None,
    request_id: str = "",
) -> dict[str, Any]:
    """Select and execute one approved registered tool, with safe failure reporting."""
    decision = classify_intent(query, image_available=bool(image_ref))
    result: dict[str, Any] = {
        "query": query, "intent": decision.intent, "tool": decision.tool,
        "reason": decision.reason, "sources": [], "tool_result": None,
        "tool_execution_status": "not_required", "failure": None,
        "tools_executed": [], "execution_order": [], "calculation_operations": [],
        "visual_artifact_ids": [image_ref] if image_ref else [],
    }
    if decision.tool is None:
        return result
    try:
        def execute(name: str, **kwargs: Any) -> Any:
            result["tools_executed"].append(name)
            result["execution_order"].append(name)
            return registry.execute(name, **kwargs)

        if decision.tool == "document_search":
            result["sources"] = execute("document_search", query=query, top_k=top_k, file_id=file_id)
        elif decision.tool == "document_metadata":
            if db is None:
                raise ValueError("Database session is required for document metadata.")
            if not file_id:
                raise ValueError("A file_id is required to retrieve document metadata.")
            result["tools_executed"].append("document_metadata")
            result["execution_order"].append("document_metadata")
            result["tool_result"] = await registry.execute("document_metadata", db=db, file_id=file_id)
        elif decision.tool == "image_analysis":
            if not image_ref:
                raise ValueError("An image artifact is required for visual analysis.")
            result["tool_result"] = execute("image_analysis", image_ref=image_ref)
        elif decision.tool == "industrial_calculator":
            result["tool_result"] = execute("industrial_calculator", **decision.arguments)
            result["calculation_operations"] = [decision.arguments["operation"]]
        elif decision.tool == "equipment_analysis":
            image_result = None
            if image_ref:
                # Explicit execution order: image_analysis -> document_search -> equipment_analysis
                image_result = execute("image_analysis", image_ref=image_ref)
            result["sources"] = execute("document_search", query=query, top_k=min(top_k, 5), file_id=file_id)
            result["tool_result"] = execute(
                "equipment_analysis",
                kind="equipment",
                sources=result["sources"],
                image_result=image_result,
            )
        elif decision.tool in {"process_analysis", "safety_analysis", "procedure_lookup"}:
            result["sources"] = execute("document_search", query=query, top_k=min(top_k, 5), file_id=file_id)
            kind = {
                "process_analysis": "process",
                "safety_analysis": "safety",
                "procedure_lookup": "procedure",
            }[decision.tool]
            result["tool_result"] = execute(decision.tool, kind=kind, sources=result["sources"])
        elif decision.tool == "document_comparison":
            result["sources"] = execute("document_search", query=query, top_k=min(top_k, 5), file_id=file_id)
            result["tool_result"] = execute("document_comparison", sources=result["sources"])
        elif decision.tool == "report_generation":
            result["sources"] = execute("document_search", query=query, top_k=min(top_k, 5), file_id=file_id)
            analysis_kind = "safety" if any(w in query.lower() for w in ("safety", "hazard", "ppe")) else ("equipment" if "equipment" in query.lower() else "process")
            analysis = execute(f"{analysis_kind}_analysis", kind=analysis_kind, sources=result["sources"])

            calculations: list[dict[str, Any]] = []
            calc_args = _calculator_arguments(query)
            if calc_args:
                try:
                    calc_res = execute("industrial_calculator", **calc_args)
                    calculations.append(calc_res)
                    result["calculation_operations"].append(calc_args["operation"])
                except Exception:
                    pass

            result["tool_result"] = execute(
                "report_generation",
                request_id=request_id,
                question=query,
                analyses=[analysis] if analysis else [],
                calculations=calculations,
            )
        else:
            raise ValueError("Selected tool is not executable.")
        result["tool_execution_status"] = "success"
    except (KeyError, TypeError, ValueError) as exc:
        result["tool_execution_status"] = "failed"
        result["failure"] = str(exc)
    return result
