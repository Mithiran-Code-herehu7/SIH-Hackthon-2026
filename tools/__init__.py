from app.tools.registry import registry

from app.tools.document_search import document_metadata, document_search
from app.tools.image_analysis import image_analysis
from app.tools.industrial_analysis import (
    analyze_evidence,
    compare_documents,
    generate_report,
)
from app.tools.industrial_calculator import industrial_calculator


def process_analysis(**kwargs):
    return analyze_evidence(
        kind="process",
        sources=kwargs.get("sources", []),
        image_result=kwargs.get("image_result"),
    )


def safety_analysis(**kwargs):
    return analyze_evidence(
        kind="safety",
        sources=kwargs.get("sources", []),
        image_result=kwargs.get("image_result"),
    )


def equipment_analysis(**kwargs):
    return analyze_evidence(
        kind="equipment",
        sources=kwargs.get("sources", []),
        image_result=kwargs.get("image_result"),
    )


def procedure_lookup(**kwargs):
    return analyze_evidence(
        kind="procedure",
        sources=kwargs.get("sources", []),
        image_result=kwargs.get("image_result"),
    )


registry.register(
    name="document_search",
    description="Search confidential documents in the local FAISS knowledge base.",
    handler=document_search,
)

registry.register(
    name="document_metadata",
    description="Retrieve metadata for a document from the local SQLite database.",
    handler=document_metadata,
)

registry.register(
    name="industrial_calculator",
    description="Perform safe deterministic industrial calculations.",
    handler=industrial_calculator,
)

registry.register(
    name="image_analysis",
    description="Analyze an approved local image or extracted PDF visual using an optional local vision model.",
    handler=image_analysis,
)

registry.register(
    name="process_analysis",
    description="Analyze an industrial process using bounded retrieved document evidence.",
    handler=process_analysis,
)

registry.register(
    name="safety_analysis",
    description="Analyze industrial safety information using bounded retrieved evidence.",
    handler=safety_analysis,
)

registry.register(
    name="equipment_analysis",
    description="Analyze equipment using bounded document evidence and optional approved visual evidence.",
    handler=equipment_analysis,
)

registry.register(
    name="procedure_lookup",
    description="Look up procedures from bounded local document evidence.",
    handler=procedure_lookup,
)

registry.register(
    name="document_comparison",
    description="Compare evidence retrieved from distinct local documents.",
    handler=compare_documents,
)

registry.register(
    name="report_generation",
    description="Generate a structured industrial analysis report from bounded evidence and deterministic calculations.",
    handler=generate_report,
)