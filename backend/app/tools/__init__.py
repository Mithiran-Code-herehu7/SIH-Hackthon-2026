from app.tools.registry import registry

from app.tools.document_search import document_metadata, document_search
from app.tools.image_analysis import image_analysis
from app.tools.industrial_analysis import (
    analyze_evidence,
    compare_documents,
    generate_report,
)
from app.tools.excel_generator import generate_excel_workbook
from app.tools.ppt_generator import generate_pptx_deck
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


def generate_excel(**kwargs):
    return generate_excel_workbook(
        filename=kwargs.get("filename", "MRPL_Operations_Safety_Demo_Pack_Incident_Register.xlsx"),
        sources=kwargs.get("sources", []),
    )


def generate_ppt(**kwargs):
    out_path = generate_pptx_deck(
        filename=kwargs.get("filename", "Operational_Risk_Priorities_September_2026.pptx"),
        title=kwargs.get("title", "Operational Risk Priorities: September 2026"),
        sources=kwargs.get("sources", []),
    )
    return {
        "task_type": "generate_ppt",
        "requires_file": True,
        "file_type": "pptx",
        "title": kwargs.get("title", "Operational Risk Priorities: September 2026"),
        "slide_count": 7,
        "filename": kwargs.get("filename", "Operational_Risk_Priorities_September_2026.pptx"),
        "file_path": str(out_path.resolve()),
        "download_url": f"/files/{kwargs.get('filename', 'Operational_Risk_Priorities_September_2026.pptx')}",
    }


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

registry.register(
    name="generate_excel",
    description="Generate a multi-sheet Excel workbook containing structured incident records and summary metrics.",
    handler=generate_excel,
)

registry.register(
    name="generate_ppt",
    description="Generate a 7-slide PowerPoint presentation deck containing operational risk priorities and safety scorecard metrics.",
    handler=generate_ppt,
)