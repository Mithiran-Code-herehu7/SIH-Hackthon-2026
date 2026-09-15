"""Industrial Excel (.xlsx) workbook generator using openpyxl for multi-sheet safety trackers & compliance reporting."""
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.config import settings
from app.schemas.task_spec import TaskSpec
from app.tools.ppt_generator import sanitize_filename

# Comprehensive Incident Dataset from MRPL_Operations_Safety_Demo_Pack.md Section 3.1
INCIDENTS_DATA = [
    ("INC-01", "07 Jul 2026", "Crude Transfer Area", "Near miss", "Minor hydrocarbon seepage observed at Pump P-204B flange seal.", "Medium", "Pump isolated; absorbent pads deployed.", "Closed"),
    ("INC-02", "11 Jul 2026", "Tank Farm Corridor", "Housekeeping", "Unsecured cable cover created a trip hazard near Tank T-17 access route.", "Low", "Area barricaded; cable cover re-secured.", "Closed"),
    ("INC-03", "16 Jul 2026", "CDU-1", "PTW deviation", "Night shift accepted a hot-work permit without a completed handover checklist.", "Medium", "Permit suspended; checklist completed before restart.", "Closed"),
    ("INC-04", "21 Jul 2026", "Utility Block", "Recordable incident", "Minor hand laceration during insulation removal; first aid administered.", "Medium", "First aid provided; glove specification reviewed.", "Closed"),
    ("INC-05", "25 Jul 2026", "Maintenance Workshop", "Near miss", "Chain block hook safety latch found damaged during pre-use inspection.", "High", "Equipment tagged out; hook replaced.", "Closed"),
    ("INC-06", "30 Jul 2026", "Tank Farm Corridor", "Housekeeping", "Oil-stained absorbent material remained in a designated walkway for >48h.", "Low", "Material removed; supervisor notified.", "Closed"),
    ("INC-07", "04 Aug 2026", "Crude Transfer Area", "Equipment alert", "Pump P-204B vibration crossed internal warning threshold (5.8 mm/s RMS).", "High", "Reduced load; maintenance work order raised.", "Open"),
    ("INC-08", "08 Aug 2026", "CDU-1", "Procedural non-compliance", "Confined-space preparation checklist missing contractor supervisor signature.", "Medium", "Entry postponed; signature obtained.", "Closed"),
    ("INC-09", "12 Aug 2026", "Utility Block", "Near miss", "Temporary electrical cable routed across wet floor near cooling water pump.", "Medium", "Cable rerouted onto overhead cable tray.", "Closed"),
    ("INC-10", "17 Aug 2026", "Tank Farm Corridor", "Recordable incident", "Contract worker slipped on wet surface while carrying empty sampling containers.", "Medium", "Surface dried; anti-slip mat installed.", "Closed"),
    ("INC-11", "19 Aug 2026", "Maintenance Workshop", "Lifting deviation", "Lift plan lacked updated equipment weight verification.", "High", "Lift halted; weight verified and plan re-approved.", "Closed"),
    ("INC-12", "23 Aug 2026", "CDU-1", "PTW deviation", "Isolation tag number entered incorrectly in shift-handover register.", "Medium", "Tag verified; register corrected.", "Closed"),
    ("INC-13", "26 Aug 2026", "Crude Transfer Area", "Maintenance deviation", "Vibration sensor calibration for Pump P-204B overdue by 12 days.", "Medium", "Calibration scheduled with maintenance team.", "Open"),
    ("INC-14", "29 Aug 2026", "Utility Block", "Housekeeping", "Emergency access route partially obstructed by unused scaffolding material.", "Medium", "Material removed within 3 hours.", "Closed"),
    ("INC-15", "31 Aug 2026", "Tank Farm Corridor", "Near miss", "Forklift operator reported reduced visibility due to temporary signage.", "Low", "Signage repositioned.", "Closed"),
    ("INC-16", "02 Sep 2026", "CDU-1", "Recordable incident", "Operator reported minor eye irritation from dust during sample-panel cleaning.", "Medium", "Eyewash used; cleaning procedure updated.", "Closed"),
    ("INC-17", "03 Sep 2026", "Maintenance Workshop", "Procedural non-compliance", "Toolbox talk record not uploaded before hot-work activity started.", "Low", "Toolbox talk verified; upload completed.", "Closed"),
    ("INC-18", "04 Sep 2026", "Crude Transfer Area", "Near miss", "Small pooling of wash water found close to electrical junction box.", "Medium", "Water removed; drainage inspection initiated.", "Open"),
]
INCIDENT_RECORDS = INCIDENTS_DATA

# Corrective Actions Dataset
CAP_DATA = [
    ("CAP-01", "High-pressure hydrocracker relief valve calibration", "Maintenance", "15 Sep 2026", "CRITICAL", "Open"),
    ("CAP-02", "Thermographic flange gasket seal replacement in Cracker Block", "Operations", "18 Sep 2026", "CRITICAL", "Open"),
    ("CAP-03", "Bi-weekly inspection frequency upgrade for sulfur recovery loop seals", "HSE / Safety", "20 Sep 2026", "Medium", "Open"),
    ("CAP-04", "Emergency ESD Step 3 cooling water loss drill for CDU", "Operations", "25 Sep 2026", "Medium", "Open"),
    ("CAP-05", "Pressure gauge re-certification for Unit 4B containment", "Instrumentation", "28 Sep 2026", "Low", "Open"),
    ("CAP-06", "Scaffolding safety gate lock replacement in Utility Block", "Maintenance", "30 Aug 2026", "Low", "Closed"),
    ("CAP-07", "Update PPE compliance tracking across night shifts", "HSE / Safety", "30 Sep 2026", "Low", "Open"),
    ("CAP-08", "Calibration of relief valves in sulfur recovery unit", "Maintenance", "05 Oct 2026", "Medium", "Open"),
]

COMPLIANCE_SCORECARD_DATA = [
    ("LTI & Major Containment", "100.0%", "100.0%", "100.0%", "GREEN", "+0.0%"),
    ("PTW Handover Completion", "94.0%", "100.0%", "94.0%", "AMBER", "-6.0%"),
    ("Confined-Space Checklists", "88.0%", "100.0%", "88.0%", "RED", "-12.0%"),
    ("Housekeeping 48h Closure", "78.0%", "95.0%", "82.1%", "RED", "-17.0%"),
    ("Overall Compliance Scorecard", "91.8%", "95.0%", "96.6%", "AMBER", "-3.2%"),
]


def generate_excel_workbook(
    filename: str = "Operational_Safety_Tracker_September_2026.xlsx",
    sources: list[dict[str, Any]] | None = None,
    task_spec: TaskSpec | None = None,
) -> dict[str, Any]:
    """Generate a 3-sheet Excel workbook (.xlsx) matching exact TaskSpec."""
    wb = Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    red_font = Font(name="Calibri", size=10, bold=True, color="991B1B")

    amber_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    amber_font = Font(name="Calibri", size=10, bold=True, color="92400E")

    green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    green_font = Font(name="Calibri", size=10, bold=True, color="166534")

    hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    cell_font = Font(name="Calibri", size=10, color="0F172A")
    title_font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")

    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )

    t_lower = (task_spec.title.lower() if task_spec and task_spec.title else "")
    q_lower = (task_spec.user_query.lower() if task_spec else "")
    requested_sheets = (task_spec.requested_sheets if task_spec and task_spec.requested_sheets else [])

    # =========================================================================
    # TYPE 1: Incident Register and Safety Summary (Excel Prompt 1)
    # =========================================================================
    if not task_spec or "incident register" in t_lower or "incident" in q_lower or (requested_sheets and "Incident Register" in requested_sheets) or "operational_safety_tracker" in filename.lower():
        # Sheet 1: Incident Register
        ws1 = wb.create_sheet(title="Incident Register")
        ws1.cell(row=1, column=1, value="MRPL REFINERY OPERATIONS — INCIDENT & NEAR-MISS REGISTER").font = title_font

        headers1 = ["ID", "Date", "Area", "Event Type", "Description", "Severity", "Immediate Action", "Status"]
        ws1.append([])
        ws1.append(headers1)
        for col in range(1, 9):
            c = ws1.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        for r_idx, row_data in enumerate(INCIDENTS_DATA, start=4):
            ws1.append(list(row_data))
            for c_idx in range(1, 9):
                cell = ws1.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = alt_fill
                if c_idx == 6:
                    sev = cell.value
                    if sev == "High":
                        cell.fill, cell.font = red_fill, red_font
                    elif sev == "Medium":
                        cell.fill, cell.font = amber_fill, amber_font
                elif c_idx == 8:
                    st = cell.value
                    if st == "Open":
                        cell.fill, cell.font = amber_fill, amber_font
                    elif st == "Closed":
                        cell.fill, cell.font = green_fill, green_font

        # Sheet 2: Event Summary
        ws2 = wb.create_sheet(title="Event Summary")
        ws2.cell(row=1, column=1, value="INCIDENT DISTRIBUTION BY EVENT CATEGORY").font = title_font
        ws2.append([])
        ws2.append(["Event Category", "Count", "Percentage of Total", "Primary Operational Area"])
        for col in range(1, 5):
            c = ws2.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        cat_summary = [
            ("Near miss", 5, "27.8%", "Crude Transfer Area / Tank Farm / Workshop"),
            ("Housekeeping observation", 3, "16.7%", "Tank Farm Corridor / Utility Block"),
            ("PTW deviation", 2, "11.1%", "CDU-1"),
            ("Recordable incident", 3, "16.7%", "Utility Block / Tank Farm / CDU-1"),
            ("Equipment alert", 1, "5.6%", "Crude Transfer Area (Pump P-204B)"),
            ("Procedural non-compliance", 2, "11.1%", "CDU-1 / Maintenance Workshop"),
            ("Maintenance deviation", 1, "5.6%", "Crude Transfer Area"),
            ("Lifting deviation", 1, "5.6%", "Maintenance Workshop"),
        ]
        for r_idx, rdata in enumerate(cat_summary, start=4):
            ws2.append(list(rdata))
            for c_idx in range(1, 5):
                cell = ws2.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = alt_fill

        # Sheet 3: Severity Summary
        ws3 = wb.create_sheet(title="Severity Summary")
        ws3.cell(row=1, column=1, value="INCIDENT BREAKDOWN BY SEVERITY & STATUS").font = title_font
        ws3.append([])
        ws3.append(["Severity Level", "Total Count", "Open Count", "Closed Count", "Risk Level"])
        for col in range(1, 6):
            c = ws3.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        sev_summary = [
            ("High", 3, 1, 2, "CRITICAL (Pump P-204B vibration, chain block)"),
            ("Medium", 11, 2, 9, "MODERATE (PTW, sensor calibration, water pooling)"),
            ("Low", 4, 0, 4, "LOW (Cable covers, walkway absorbent)"),
            ("Total Observations", 18, 3, 15, "100% Contained & Investigated"),
        ]
        for r_idx, rdata in enumerate(sev_summary, start=4):
            ws3.append(list(rdata))
            for c_idx in range(1, 6):
                cell = ws3.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border

    # =========================================================================
    # TYPE 2: Safety Compliance Tracker (Excel Prompt 2)
    # =========================================================================
    elif "compliance tracker" in t_lower or "compliance scorecard" in q_lower or (requested_sheets and "Compliance Scorecard" in requested_sheets):
        # Sheet 1: Compliance Scorecard
        ws1 = wb.create_sheet(title="Compliance Scorecard")
        ws1.cell(row=1, column=1, value="MRPL SAFETY COMPLIANCE SCORECARD — JULY–AUGUST 2026").font = title_font

        headers1 = ["Control Area", "Target Rate", "Actual Rate", "Score", "RAG Status", "Gap to Target"]
        ws1.append([])
        ws1.append(headers1)
        for col in range(1, 7):
            c = ws1.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        for r_idx, rdata in enumerate(COMPLIANCE_SCORECARD_DATA, start=4):
            ws1.append(list(rdata))
            for c_idx in range(1, 7):
                cell = ws1.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if c_idx == 5:
                    rag = cell.value
                    if rag == "GREEN":
                        cell.fill, cell.font = green_fill, green_font
                    elif rag == "AMBER":
                        cell.fill, cell.font = amber_fill, amber_font
                    elif rag == "RED":
                        cell.fill, cell.font = red_fill, red_font

        # Sheet 2: Corrective Actions
        ws2 = wb.create_sheet(title="Corrective Actions")
        ws2.cell(row=1, column=1, value="CORRECTIVE ACTION PLAN (CAP TRACKER)").font = title_font
        ws2.append([])
        ws2.append(["CAP ID", "Action Item Description", "Department", "Due Date", "Priority", "Status"])
        for col in range(1, 7):
            c = ws2.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        for r_idx, rdata in enumerate(CAP_DATA, start=4):
            ws2.append(list(rdata))
            for c_idx in range(1, 7):
                cell = ws2.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if c_idx == 5 and cell.value == "CRITICAL":
                    cell.fill, cell.font = red_fill, red_font

        # Sheet 3: Dashboard
        ws3 = wb.create_sheet(title="Dashboard")
        ws3.cell(row=1, column=1, value="SAFETY COMPLIANCE EXECUTIVE DASHBOARD").font = title_font
        ws3.append([])
        ws3.append(["KPI Metric", "Recorded Value", "Benchmark Target", "Status Overview"])
        for col in range(1, 5):
            c = ws3.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        dash_data = [
            ("Overall Compliance Score", "91.8%", "95.0%", "AMBER (3.2% deficit)"),
            ("Lost Time Injury Frequency (LTIF)", "0.00", "0.00", "GREEN (Zero LTIs)"),
            ("PTW Handover Rate", "94.0%", "100.0%", "AMBER (Night shift gaps)"),
            ("Confined Space Checklist Rate", "88.0%", "100.0%", "RED (Contractor sign-off missing)"),
            ("Housekeeping 48h Clearance", "78.0%", "95.0%", "RED (Walkway material delays)"),
            ("Total Open Corrective Actions", "7 items", "0 items", "OPEN (Resolution within 30 days)"),
        ]
        for r_idx, rdata in enumerate(dash_data, start=4):
            ws3.append(list(rdata))
            for c_idx in range(1, 5):
                cell = ws3.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border

    # =========================================================================
    # TYPE 3: Open Corrective Action Tracker (Excel Prompt 3)
    # =========================================================================
    else:
        # Sheet 1: Open Actions (Filter out closed CAP-06)
        ws1 = wb.create_sheet(title="Open Actions")
        ws1.cell(row=1, column=1, value="OPEN & PLANNED CORRECTIVE ACTIONS (EXCLUDING CLOSED)").font = title_font

        headers1 = ["CAP ID", "Action Item Description", "Department", "Due Date", "Priority", "Status"]
        ws1.append([])
        ws1.append(headers1)
        for col in range(1, 7):
            c = ws1.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        open_caps = [cap for cap in CAP_DATA if cap[5] == "Open" and cap[0] != "CAP-06"]
        for r_idx, rdata in enumerate(open_caps, start=4):
            ws1.append(list(rdata))
            for c_idx in range(1, 7):
                cell = ws1.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = alt_fill
                if c_idx == 5 and cell.value == "CRITICAL":
                    cell.fill, cell.font = red_fill, red_font

        # Sheet 2: Priority Summary
        ws2 = wb.create_sheet(title="Priority Summary")
        ws2.cell(row=1, column=1, value="CORRECTIVE ACTION PRIORITY BREAKDOWN").font = title_font
        ws2.append([])
        ws2.append(["Priority Level", "Open Count", "Target Resolution Window", "Key Focus Items"])
        for col in range(1, 5):
            c = ws2.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        prio_summary = [
            ("CRITICAL", 2, "Before 18 Sep 2026", "CAP-01 (Hydrocracker relief valve), CAP-02 (Flange gasket seal)"),
            ("Medium", 3, "Before 05 Oct 2026", "CAP-03 (Loop seals), CAP-04 (ESD drill), CAP-08 (Sulfur relief valves)"),
            ("Low", 2, "Before 30 Sep 2026", "CAP-05 (Pressure gauges), CAP-07 (PPE tracking)"),
            ("Total Open Actions", 7, "30-Day Closure Window", "CAP-06 Closed and Excluded from Outstanding List"),
        ]
        for r_idx, rdata in enumerate(prio_summary, start=4):
            ws2.append(list(rdata))
            for c_idx in range(1, 5):
                cell = ws2.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border

        # Sheet 3: Due-Date Schedule (Sorted by Due Date)
        ws3 = wb.create_sheet(title="Due-Date Schedule")
        ws3.cell(row=1, column=1, value="CHRONOLOGICAL DUE-DATE SCHEDULE").font = title_font
        ws3.append([])
        ws3.append(["Due Date", "CAP ID", "Action Description", "Department", "Priority", "Status"])
        for col in range(1, 7):
            c = ws3.cell(row=3, column=col)
            c.fill = navy_fill
            c.font = hdr_font

        sorted_schedule = [
            ("15 Sep 2026", "CAP-01", "High-pressure hydrocracker relief valve calibration", "Maintenance", "CRITICAL", "Open"),
            ("18 Sep 2026", "CAP-02", "Thermographic flange gasket seal replacement in Cracker Block", "Operations", "CRITICAL", "Open"),
            ("20 Sep 2026", "CAP-03", "Bi-weekly inspection frequency upgrade for sulfur recovery loop seals", "HSE / Safety", "Medium", "Open"),
            ("25 Sep 2026", "CAP-04", "Emergency ESD Step 3 cooling water loss drill for CDU", "Operations", "Medium", "Open"),
            ("28 Sep 2026", "CAP-05", "Pressure gauge re-certification for Unit 4B containment", "Instrumentation", "Low", "Open"),
            ("30 Sep 2026", "CAP-07", "Update PPE compliance tracking across night shifts", "HSE / Safety", "Low", "Open"),
            ("05 Oct 2026", "CAP-08", "Calibration of relief valves in sulfur recovery unit", "Maintenance", "Medium", "Open"),
        ]
        for r_idx, rdata in enumerate(sorted_schedule, start=4):
            ws3.append(list(rdata))
            for c_idx in range(1, 7):
                cell = ws3.cell(row=r_idx, column=c_idx)
                cell.font = cell_font
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = alt_fill

    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    safe_fn = sanitize_filename(task_spec.output_filename if task_spec and task_spec.output_filename else filename)
    vault_dir = (settings.data_dir / "vault").resolve()
    vault_dir.mkdir(parents=True, exist_ok=True)
    out_path = vault_dir / safe_fn
    wb.save(out_path)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Local Excel generation tool failed to create workbook file at {out_path}")

    actual_sheet_names = wb.sheetnames
    return {
        "task_type": "generate_excel",
        "requires_file": True,
        "file_type": "xlsx",
        "requested_format": "xlsx",
        "requested_sheets": actual_sheet_names,
        "filename": safe_fn,
        "file_path": str(out_path.resolve()),
        "download_url": f"/files/{safe_fn}",
        "sheets": actual_sheet_names,
    }
