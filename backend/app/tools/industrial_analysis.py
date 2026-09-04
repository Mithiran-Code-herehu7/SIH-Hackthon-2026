"""Bounded, conservative industrial evidence analysis helpers."""
from datetime import datetime
import re
from typing import Any, Literal

from app.schemas.industrial import EvidenceReference, IndustrialAnalysis, IndustrialReport

SAFETY_WORDS = (
    "hazard", "warning", "ppe", "emergency", "shutdown",
    "limit", "inspect", "alarm", "fire", "leak", "safety", "precaution", "protective",
)
PROCESS_WORDS = (
    "process", "stage", "distill", "fraction", "feed", "product",
    "column", "condenser", "reboiler", "pump", "valve", "furnace", "cdu", "temperature",
)
EQUIPMENT_WORDS = (
    "pump", "valve", "compressor", "column", "vessel", "heat exchanger",
    "tank", "instrument", "equipment", "piping", "inspection", "vibration", "leak", "maintenance",
)
PROCEDURE_WORDS = (
    "procedure", "step", "emergency", "shutdown", "response",
    "instruction", "follow", "action", "verify", "report", "start", "stop",
)

SAFETY_CATEGORIES: dict[str, tuple[str, ...]] = {
    "hazards": ("hazard", "risk", "leak", "fire", "toxic", "explosion", "corrosion", "abnormal", "deterioration", "upset"),
    "warnings": ("warning", "caution", "alarm", "danger", "alert", "notice"),
    "ppe": ("ppe", "personal protective equipment", "protective equipment", "helmet", "footwear", "eye protection", "clothing", "goggles", "gloves", "respirator", "workwear"),
    "limits": ("limit", "operating limit", "maximum", "minimum", "pressure", "temperature", "flow", "level", "threshold", "cdu furnace", "atmospheric"),
    "emergency": ("emergency", "shutdown", "isolation", "evacuation", "emergency-response", "emergency response", "pressure-relief"),
}


def _evidence(source: dict[str, Any]) -> EvidenceReference:
    return EvidenceReference(
        file_id=str(source["file_id"]),
        filename=str(source.get("filename", "unknown")),
        chunk_index=int(source["chunk_index"]),
        score=float(source["score"]) if source.get("score") is not None else None,
    )


def _sentences(sources: list[dict[str, Any]], words: tuple[str, ...], limit: int = 12) -> list[tuple[str, EvidenceReference]]:
    found: list[tuple[str, EvidenceReference]] = []
    seen: set[str] = set()
    for source in sources:
        ref = _evidence(source)
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", str(source.get("text", ""))):
            cleaned = " ".join(sentence.split())
            if cleaned and cleaned not in seen and any(word in cleaned.lower() for word in words):
                seen.add(cleaned)
                found.append((cleaned[:600], ref))
                if len(found) >= limit:
                    return found
    return found


def analyze_evidence(
    kind: Literal["process", "safety", "equipment", "procedure"],
    sources: list[dict[str, Any]],
    image_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    words_map = {
        "process": PROCESS_WORDS,
        "safety": SAFETY_WORDS,
        "equipment": EQUIPMENT_WORDS,
        "procedure": PROCEDURE_WORDS,
    }
    words = words_map[kind]
    refs = [_evidence(item) for item in sources]
    matched = _sentences(sources, words)
    findings = [
        {"statement": text, "classification": "observed", "evidence": [ref.model_dump()]}
        for text, ref in matched
    ]

    warnings: list[str] = []
    uncertainties: list[str] = []

    warning_disclaimer = "This is evidence assistance only, not an official operating instruction or certified engineering/safety assessment."

    if not sources:
        uncertainties.append("No retrieved document evidence was available; no industrial claim can be established.")
        if kind == "safety":
            uncertainties.append("Safety procedures must never be fabricated when evidence is absent.")
    elif not findings:
        uncertainties.append("Retrieved evidence did not explicitly address the requested topic.")

    if kind == "safety":
        warnings.append(warning_disclaimer)
        all_text = " ".join(str(s.get("text", "")).lower() for s in sources)
        for category, terms in SAFETY_CATEGORIES.items():
            if not any(term in all_text for term in terms):
                uncertainties.append(f"Specific {category.upper()} details were not identified in the retrieved evidence.")
        for text, _ in matched:
            text_lower = text.lower()
            if any(term in text_lower for term in ("warning", "caution", "danger", "hazard", "alarm")):
                if text not in warnings:
                    warnings.append(f"Document warning: {text}")

    if kind == "equipment" and image_result:
        observation = image_result.get("analysis") or image_result.get("response") or "Visual artifact was supplied."
        findings.append({
            "statement": f"Visual observation: {str(observation)[:600]}",
            "classification": "inferred",
            "evidence": [],
        })
        uncertainties.append(
            "Visual observations do not prove equipment condition, failure, or safety compliance and require qualified physical inspection."
        )

    return IndustrialAnalysis(
        analysis_type=kind,
        findings=findings,
        evidence=refs,
        warnings=warnings,
        uncertainties=uncertainties,
        disclaimer=warning_disclaimer,
    ).model_dump(mode="json")


def compare_documents(
    sources: list[dict[str, Any]],
    selected_file_ids: list[str] | None = None,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        grouped.setdefault(str(source["file_id"]), []).append(source)
    if selected_file_ids:
        grouped = {key: value for key, value in grouped.items() if key in selected_file_ids}

    refs = [_evidence(item) for values in grouped.values() for item in values]
    findings: list[dict[str, Any]] = []
    uncertainty: list[str] = []

    if len(grouped) < 2:
        uncertainty.append("Comparison requires evidence from at least two distinct documents.")
    else:
        doc_names = {
            str(s["file_id"]): str(s.get("filename", s["file_id"]))
            for s in sources
        }
        terms = {
            key: set(re.findall(r"[a-zA-Z]{5,}", " ".join(str(x.get("text", "")).lower() for x in values)))
            for key, values in grouped.items()
        }
        first, second = list(terms)[:2]
        shared = sorted(terms[first] & terms[second])[:12]
        only_first = sorted(terms[first] - terms[second])[:8]
        only_second = sorted(terms[second] - terms[first])[:8]

        first_name = doc_names.get(first, first)
        second_name = doc_names.get(second, second)

        if shared:
            findings.append({
                "statement": "Shared relevant terms across compared documents: " + ", ".join(shared),
                "classification": "observed",
                "evidence": [ref.model_dump() for ref in refs],
            })
        if only_first or only_second:
            findings.append({
                "statement": f"Distinct terms in evidence: {first_name}: {', '.join(only_first) or 'none'}; {second_name}: {', '.join(only_second) or 'none'}.",
                "classification": "observed",
                "evidence": [ref.model_dump() for ref in refs],
            })

    return IndustrialAnalysis(
        analysis_type="comparison",
        findings=findings,
        evidence=refs,
        uncertainties=uncertainty,
        disclaimer="Comparison is limited to retrieved excerpts, not entire documents.",
    ).model_dump(mode="json")


def generate_report(
    request_id: str,
    question: str,
    analyses: list[dict[str, Any]],
    calculations: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence = [ref for analysis in analyses for ref in analysis.get("evidence", [])]
    findings = [finding for analysis in analyses for finding in analysis.get("findings", [])]
    uncertainties = list(dict.fromkeys(item for analysis in analyses for item in analysis.get("uncertainties", [])))
    risks_warnings = list(dict.fromkeys(
        ["Not a substitute for approved site procedures or qualified engineering review."] +
        [warning for analysis in analyses for warning in analysis.get("warnings", [])]
    ))
    observations = [
        finding.get("statement", "")
        for finding in findings
        if finding.get("classification") in {"observed", "inferred"}
    ]
    assumptions = [
        "Analysis is strictly bounded to retrieved local confidential documents and deterministic calculations.",
        "Engineering parameters must be validated against licensed plant operational limits.",
    ]

    calc_keywords = ("efficiency", "ratio", "mass balance", "flow rate", "percentage", "pressure", "temperature", "calculate")
    if not calculations and any(w in question.lower() for w in calc_keywords):
        uncertainties.append(
            "Calculable parameters referenced in request, but required numeric inputs were missing or insufficient; no calculations were fabricated."
        )
    elif calculations:
        ops = ", ".join(c.get("operation", "calculation") for c in calculations)
        assumptions.append(
            f"Deterministic engineering calculation ({ops}) executed directly from explicit parameters without LLM arithmetic estimation."
        )

    title = f"Industrial Analysis Report: {question[:60].strip()}"
    conclusion = (
        f"Findings are strictly bounded to {len(evidence)} retrieved local evidence reference(s) "
        f"and {len(calculations)} deterministic calculation(s)."
    )

    return IndustrialReport(
        title=title,
        objective=question,
        findings=findings,
        calculations=calculations,
        evidence=evidence,
        observations=observations,
        risks_warnings=risks_warnings,
        assumptions=assumptions,
        uncertainties=uncertainties,
        conclusion=conclusion,
        generated_at=datetime.utcnow(),
        request_id=request_id,
    ).model_dump(mode="json")


