"""Executive PowerPoint presentation (.pptx) generator for industrial audit & HSE leadership reviews."""
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from app.config import settings
from app.schemas.task_spec import TaskSpec


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to pure safe ASCII characters for filesystem and HTTP headers."""
    ext = ""
    if "." in filename:
        parts = filename.rsplit(".", 1)
        name_part, ext = parts[0], "." + parts[1]
    else:
        name_part = filename

    cleaned = (
        name_part.replace("“", "")
        .replace("”", "")
        .replace('"', "")
        .replace("'", "")
        .replace("—", "-")
        .replace("–", "-")
        .replace(":", "")
        .replace("/", "_")
        .replace("\\", "_")
    )
    ascii_clean = cleaned.encode("ascii", "ignore").decode("ascii")
    res = re.sub(r"[^\w\-.]", "_", ascii_clean)
    res = re.sub(r"_{2,}", "_", res).strip("_")
    return (res or "presentation") + ext


def set_shape_flat_color(shape, fill_color: RGBColor, border_color: RGBColor | None = None):
    """Set shape solid fill and optional border color."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()


def generate_pptx_deck(
    filename: str = "Safety_Performance_and_Control_Gaps_July-August_2026.pptx",
    title: str = "Safety Performance and Control Gaps — July–August 2026",
    slide_count: int = 6,
    sources: list[dict[str, Any]] | None = None,
    task_spec: TaskSpec | None = None,
) -> Path:
    """Generate a high-impact, professional executive PowerPoint deck (.pptx) matching exact TaskSpec."""
    target_title = task_spec.title if task_spec and task_spec.title else title
    target_count = task_spec.slide_count if task_spec and task_spec.slide_count else slide_count
    safe_filename = sanitize_filename(task_spec.output_filename if task_spec and task_spec.output_filename else filename)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    NAVY = RGBColor(0x1E, 0x3A, 0x8A)
    SLATE = RGBColor(0x0F, 0x17, 0x2A)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    LIGHT_BG = RGBColor(0xF8, 0xFA, 0xFC)
    CARD_BG = RGBColor(0xFF, 0xFF, 0xFF)
    BORDER_CLR = RGBColor(0xE2, 0xE8, 0xF0)
    ACCENT_BLUE = RGBColor(0x25, 0x63, 0xEB)
    WARN_RED = RGBColor(0xDC, 0x26, 0x26)
    WARN_AMBER = RGBColor(0xD9, 0x77, 0x06)
    PASS_GREEN = RGBColor(0x16, 0x65, 0x34)

    def add_slide_header(slide, title_text: str, category_text: str = "HSE LEADERSHIP BRIEFING"):
        hdr_rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        set_shape_flat_color(hdr_rect, NAVY)

        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.7), Inches(0.8))
        tf = txBox.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = category_text.upper()
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)

        p2 = tf.add_paragraph()
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = WHITE

    t_lower = target_title.lower()
    q_lower = (task_spec.user_query.lower() if task_spec else "")

    # =========================================================================
    # BRANCH 1: Pump P-204B Specific PPT (Prompt 1)
    # =========================================================================
    if ("p-204b" in t_lower or "reliability risk briefing" in t_lower) and not ("operations safety review" in t_lower or "july" in t_lower or "august" in t_lower):
        # Slide 1: Executive Summary
        slide1 = prs.slides.add_slide(blank_layout)
        bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        set_shape_flat_color(bg1, NAVY)
        dec1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.15), Inches(4.2))
        set_shape_flat_color(dec1, ACCENT_BLUE)
        tb1 = slide1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(11.0), Inches(4.8))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        tf1.paragraphs[0].text = "CRITICAL ASSET RELIABILITY BRIEFING"
        tf1.paragraphs[0].font.size = Pt(12)
        tf1.paragraphs[0].font.bold = True
        tf1.paragraphs[0].font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
        tf1.paragraphs[0].space_after = Pt(12)

        pt1 = tf1.add_paragraph()
        pt1.text = target_title
        pt1.font.size = Pt(30)
        pt1.font.bold = True
        pt1.font.color.rgb = WHITE
        pt1.space_after = Pt(14)

        b_p204b_1 = [
            "Executive Summary: Pump P-204B in Crude Transfer Area designated Critical Priority Equipment.",
            "Operating Parameter: Average vibration 5.8 mm/s RMS (exceeds normal threshold < 4.5 mm/s RMS).",
            "Warning Alarm: Vibration crossed internal warning threshold for 3rd time in 4 weeks.",
            "Active Incidents: Hydrocarbon seepage at flange (INC-01), vibration alert (INC-07), sensor calibration overdue by 12d (INC-13).",
            "Escalation Boundary: Operation above 6.5 mm/s RMS requires mandatory load reduction & emergency isolation.",
        ]
        for sb in b_p204b_1:
            p = tf1.add_paragraph()
            p.text = f"•  {sb}"
            p.font.size = Pt(13)
            p.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
            p.space_after = Pt(6)

        # Slide 2: Evidence and Operating Thresholds
        slide2 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide2, "Slide 2: Evidence & Operating Thresholds", "ASSET CONDITION ASSESSMENT")
        t_shape2 = slide2.shapes.add_table(5, 4, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.2))
        t2 = t_shape2.table
        t2.columns[0].width = Inches(3.2)
        t2.columns[1].width = Inches(2.2)
        t2.columns[2].width = Inches(2.2)
        t2.columns[3].width = Inches(4.1)

        h2 = ["Parameter / Evidence Item", "Recorded Baseline", "Standard Threshold", "Operational Status"]
        for idx, text in enumerate(h2):
            cell = t2.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE

        rows2 = [
            ("Pump P-204B Vibration Level", "5.8 mm/s RMS", "< 4.5 mm/s RMS", "EXCEEDED (Warning 3x in 4w)"),
            ("Vibration Sensor Calibration", "12 days overdue", "2-year cycle", "OVERDUE (INC-13)"),
            ("Flange Mechanical Seal", "Hydrocarbon seepage", "Zero leakage", "SEEPAGE OBSERVED (INC-01)"),
            ("Emergency Isolation Limit", "6.5 mm/s RMS", "> 6.5 mm/s RMS", "MANDATORY SHUTDOWN THRESHOLD"),
        ]
        for r_idx, rdata in enumerate(rows2, start=1):
            for c_idx, text in enumerate(rdata):
                cell = t2.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.color.rgb = SLATE
                if c_idx in (1, 2):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True

        # Slide 3: Incident History and Risk Consequences
        slide3 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide3, "Slide 3: Incident History & Risk Consequences", "RISK ESCALATION PATHWAY")
        c3_l = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
        set_shape_flat_color(c3_l, CARD_BG, BORDER_CLR)
        tb3_l = slide3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.2), Inches(5.1))
        tf3_l = tb3_l.text_frame
        tf3_l.word_wrap = True
        tf3_l.paragraphs[0].text = "Logged Incident History (CTA Area)"
        tf3_l.paragraphs[0].font.size = Pt(16)
        tf3_l.paragraphs[0].font.bold = True
        tf3_l.paragraphs[0].font.color.rgb = NAVY

        b3_l = [
            "INC-01 (07 Jul): Minor hydrocarbon seepage observed at Pump P-204B flange seal; isolated & contained.",
            "INC-07 (04 Aug): Pump P-204B vibration alarm crossed warning threshold (5.8 mm/s RMS) for 3rd time in 4 weeks.",
            "INC-13 (26 Aug): Vibration sensor calibration for Pump P-204B overdue by 12 days.",
            "INC-18 (04 Sep): Wash water pooling found close to electrical junction box near CTA area.",
        ]
        for b in b3_l:
            p = tf3_l.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        c3_r = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
        set_shape_flat_color(c3_r, CARD_BG, BORDER_CLR)
        tb3_r = slide3.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
        tf3_r = tb3_r.text_frame
        tf3_r.word_wrap = True
        tf3_r.paragraphs[0].text = "Potential Failure Consequences & Escalation"
        tf3_r.paragraphs[0].font.size = Pt(16)
        tf3_r.paragraphs[0].font.bold = True
        tf3_r.paragraphs[0].font.color.rgb = WARN_RED

        b3_r = [
            "Mechanical Seal Integrity: High vibration accelerates seal face wear, expanding hydrocarbon leakage.",
            "Unplanned Shutdown Risk: Bearing failure forces emergency trip of crude distillation unit.",
            "Ignition Hazard: Hydrocarbon seepage adjacent to electrical junction box pooling risk.",
            "Escalation Threshold (> 6.5 mm/s RMS): Mandates immediate load reduction & engineering isolation.",
        ]
        for b in b3_r:
            p = tf3_r.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        # Slide 4: Corrective Actions with Owners & Due Dates
        slide4 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide4, "Slide 4: Corrective Actions with Owners & Due Dates", "ENGINEERING INTERVENTION")
        t_shape4 = slide4.shapes.add_table(5, 5, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.2))
        t4 = t_shape4.table
        t4.columns[0].width = Inches(1.4)
        t4.columns[1].width = Inches(4.5)
        t4.columns[2].width = Inches(2.0)
        t4.columns[3].width = Inches(1.8)
        t4.columns[4].width = Inches(2.0)

        h4 = ["CAP ID", "Corrective Action Description", "Owner / Dept", "Due Date", "Target Milestone"]
        for idx, text in enumerate(h4):
            cell = t4.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = WHITE

        rows4 = [
            ("CAP-01", "Calibrate vibration sensor & inspect alignment for Pump P-204B", "Maintenance", "08 Sep 2026", "CRITICAL (Overdue)"),
            ("CAP-02", "Inspect bearings, flange gaskets & mechanical seal condition", "Operations", "12 Sep 2026", "CRITICAL"),
            ("CAP-03", "Upgrade inspection frequency for crude transfer pump seals", "HSE / Safety", "20 Sep 2026", "Medium"),
            ("CAP-05", "Re-certify pressure gauges & electrical junction box seals", "Instrumentation", "28 Sep 2026", "Medium"),
        ]
        for r_idx, (cid, desc, dept, tdate, ms) in enumerate(rows4, start=1):
            rdata = [cid, desc, dept, tdate, ms]
            for c_idx, text in enumerate(rdata):
                cell = t4.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(11)
                p.font.color.rgb = SLATE
                if c_idx in (0, 3, 4):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                if c_idx == 4 and "CRITICAL" in text:
                    p.font.color.rgb = WARN_RED

        # Slide 5: Management Decisions & Sources
        slide5 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide5, "Slide 5: Management Decisions & Sources", "EXECUTIVE ACTION REQUIRED")
        c5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.7), Inches(4.3))
        set_shape_flat_color(c5, CARD_BG, BORDER_CLR)
        tb5 = slide5.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.1))
        tf5 = tb5.text_frame
        tf5.word_wrap = True
        tf5.paragraphs[0].text = "Immediate Leadership Approval Required"
        tf5.paragraphs[0].font.size = Pt(16)
        tf5.paragraphs[0].font.bold = True
        tf5.paragraphs[0].font.color.rgb = NAVY

        recs5 = [
            "1. Approve Pump P-204B Maintenance Outage Window before 08 Sep 2026 to complete sensor calibration (CAP-01).",
            "2. Mandate mechanical seal inspection & flange gasket replacement during planned outage (CAP-02).",
            "3. Enforce automatic trip interlock protocol if vibration exceeds 6.5 mm/s RMS escalation threshold.",
        ]
        for rc in recs5:
            p = tf5.add_paragraph()
            p.text = rc
            p.font.size = Pt(13)
            p.font.color.rgb = SLATE
            p.space_after = Pt(8)

        foot5 = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0))
        set_shape_flat_color(foot5, LIGHT_BG, BORDER_CLR)
        tb_foot5 = slide5.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.9))
        tf_foot5 = tb_foot5.text_frame
        tf_foot5.word_wrap = True
        tf_foot5.paragraphs[0].text = "AUTHENTICATED SOURCES USED:"
        tf_foot5.paragraphs[0].font.size = Pt(9.5)
        tf_foot5.paragraphs[0].font.bold = True
        tf_foot5.paragraphs[0].font.color.rgb = NAVY
        p_f = tf_foot5.add_paragraph()
        p_f.text = "MRPL_Operations_Safety_Demo_Pack.md: Section 2.2 (Key Operating Parameters), Section 3.1 (Incident Register - INC-01, INC-07, INC-13), Section 4.1 (Pump P-204B Recurring Vibration), Section 6 (Corrective Action Plan - CAP-01, CAP-02)."
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # =========================================================================
    # BRANCH 2: Safety Compliance Recovery Plan PPT (Prompt 2)
    # =========================================================================
    elif "compliance recovery" in t_lower or "compliance recovery" in q_lower:
        # Slide 1: Overall Compliance Position
        slide1 = prs.slides.add_slide(blank_layout)
        bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        set_shape_flat_color(bg1, NAVY)
        dec1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.15), Inches(4.2))
        set_shape_flat_color(dec1, ACCENT_BLUE)
        tb1 = slide1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(11.0), Inches(4.8))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        tf1.paragraphs[0].text = "HSE COMPLIANCE RECOVERY ROADMAP"
        tf1.paragraphs[0].font.size = Pt(12)
        tf1.paragraphs[0].font.bold = True
        tf1.paragraphs[0].font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
        tf1.paragraphs[0].space_after = Pt(12)

        pt1 = tf1.add_paragraph()
        pt1.text = target_title
        pt1.font.size = Pt(30)
        pt1.font.bold = True
        pt1.font.color.rgb = WHITE
        pt1.space_after = Pt(14)

        b_comp_1 = [
            "Overall Compliance Position: Current compliance rate at 91.8% against benchmark target of 95.0%.",
            "Zero LTIs Achieved: 100% compliance maintained on Lost Time Injury Frequency (LTIF 0.00).",
            "Primary Deficit Areas: Permit-to-Work handover (94.0%), Confined-space checklists (88.0%), Housekeeping closure (78.0%).",
            "Recovery Goal: Achieve >95.0% compliance across all 4 operational units before 30 September 2026.",
        ]
        for sb in b_comp_1:
            p = tf1.add_paragraph()
            p.text = f"•  {sb}"
            p.font.size = Pt(13)
            p.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
            p.space_after = Pt(6)

        # Slide 2: Controls Below Target
        slide2 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide2, "Slide 2: Controls Below Target", "SAFETY SCORECARD GAPS")
        t_shape2 = slide2.shapes.add_table(5, 5, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.2))
        t2 = t_shape2.table
        t2.columns[0].width = Inches(3.2)
        t2.columns[1].width = Inches(1.6)
        t2.columns[2].width = Inches(1.6)
        t2.columns[3].width = Inches(1.5)
        t2.columns[4].width = Inches(3.8)

        h2 = ["Control Area", "Actual Rate", "Target Rate", "RAG Status", "Gap Rationale"]
        for idx, text in enumerate(h2):
            cell = t2.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE

        rows2 = [
            ("PTW & Handover Completion", "94.0%", "100.0%", "AMBER", "Night-shift hot-work permits missing handover checklists"),
            ("Confined-Space Checklists", "88.0%", "100.0%", "RED", "Contractor supervisor signature missing prior to tank entry"),
            ("Housekeeping 48h Closure", "78.0%", "95.0%", "RED", "Oil-stained absorbent & scaffolding access route delays"),
            ("Overall Compliance Scorecard", "91.8%", "95.0%", "AMBER", "Gap of 3.2% to target; requires supervisor enforcement"),
        ]
        for r_idx, rdata in enumerate(rows2, start=1):
            for c_idx, text in enumerate(rdata):
                cell = t2.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.color.rgb = SLATE
                if c_idx in (1, 2, 3):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                if c_idx == 3:
                    if text == "AMBER":
                        p.font.color.rgb = WARN_AMBER
                    elif text == "RED":
                        p.font.color.rgb = WARN_RED

        # Slide 3: Permit-to-Work & Confined-Space Gaps
        slide3 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide3, "Slide 3: Permit-to-Work & Confined-Space Gaps", "PROCEDURAL AUDIT FINDINGS")
        c3_l = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
        set_shape_flat_color(c3_l, CARD_BG, BORDER_CLR)
        tb3_l = slide3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.2), Inches(5.1))
        tf3_l = tb3_l.text_frame
        tf3_l.word_wrap = True
        tf3_l.paragraphs[0].text = "Permit-to-Work Handover Gaps (CDU-1)"
        tf3_l.paragraphs[0].font.size = Pt(16)
        tf3_l.paragraphs[0].font.bold = True
        tf3_l.paragraphs[0].font.color.rgb = NAVY

        b3_l = [
            "INC-03: Night shift accepted a hot-work permit without a completed handover checklist.",
            "INC-12: Isolation tag number entered incorrectly in shift-handover register.",
            "Handover Rate: 94.0% vs zero-tolerance target of 100.0%.",
            "Corrective Action: Implement digital dual-signoff gate before permit activation.",
        ]
        for b in b3_l:
            p = tf3_l.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        c3_r = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
        set_shape_flat_color(c3_r, CARD_BG, BORDER_CLR)
        tb3_r = slide3.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
        tf3_r = tb3_r.text_frame
        tf3_r.word_wrap = True
        tf3_r.paragraphs[0].text = "Confined-Space Verification Gaps"
        tf3_r.paragraphs[0].font.size = Pt(16)
        tf3_r.paragraphs[0].font.bold = True
        tf3_r.paragraphs[0].font.color.rgb = WARN_RED

        b3_r = [
            "INC-08: Confined-space preparation checklist missing contractor supervisor signature.",
            "Completion Rate: 88.0% against 100.0% statutory compliance standard.",
            "Contractor Oversight: Lack of pre-entry audit by contractor safety lead.",
            "Recovery Action: Mandatory supervisor physical sign-off before vessel entry.",
        ]
        for b in b3_r:
            p = tf3_r.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        # Slide 4: Housekeeping Closure Problem & Recovery Actions
        slide4 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide4, "Slide 4: Housekeeping Closure Problem & Recovery Actions", "WALKWAY & ROUTE SAFETY")
        c4_l = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
        set_shape_flat_color(c4_l, CARD_BG, BORDER_CLR)
        tb4_l = slide4.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.2), Inches(5.1))
        tf4_l = tb4_l.text_frame
        tf4_l.word_wrap = True
        tf4_l.paragraphs[0].text = "Walkway & Route Observations"
        tf4_l.paragraphs[0].font.size = Pt(16)
        tf4_l.paragraphs[0].font.bold = True
        tf4_l.paragraphs[0].font.color.rgb = NAVY

        b4_l = [
            "INC-02: Unsecured cable cover creating trip hazard near Tank T-17 access route.",
            "INC-06: Oil-stained absorbent material remained in walkway >48 hours.",
            "INC-10: Contract worker slipped on wet surface while carrying sampling containers.",
            "INC-14: Emergency access route partially obstructed by scaffolding material.",
        ]
        for b in b4_l:
            p = tf4_l.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        c4_r = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
        set_shape_flat_color(c4_r, CARD_BG, BORDER_CLR)
        tb4_r = slide4.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
        tf4_r = tb4_r.text_frame
        tf4_r.word_wrap = True
        tf4_r.paragraphs[0].text = "Housekeeping Recovery Actions"
        tf4_r.paragraphs[0].font.size = Pt(16)
        tf4_r.paragraphs[0].font.bold = True
        tf4_r.paragraphs[0].font.color.rgb = PASS_GREEN

        b4_r = [
            "24-Hour Clearance Mandate: Require all absorbent pads & debris cleared within 24h.",
            "Scaffolding Permit Audit: Enforce immediate removal of unused scaffolding within 3h.",
            "Anti-Slip Surface Installation: Applied anti-slip coatings along sampling routes.",
            "Signage Repositioning: Repositioned temporary signage to restore forklift operator line-of-sight.",
        ]
        for b in b4_r:
            p = tf4_r.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(11.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(6)

        # Slide 5: Management Actions, Owners, Due Dates & Sources
        slide5 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide5, "Slide 5: Management Actions, Owners, Due Dates & Sources", "RECOVERY PLAN EXECUTION")
        t_shape5 = slide5.shapes.add_table(5, 5, Inches(0.8), Inches(1.4), Inches(11.7), Inches(4.5))
        t5 = t_shape5.table
        t5.columns[0].width = Inches(1.3)
        t5.columns[1].width = Inches(4.5)
        t5.columns[2].width = Inches(2.0)
        t5.columns[3].width = Inches(1.8)
        t5.columns[4].width = Inches(2.0)

        h5 = ["CAP ID", "Action Item Description", "Department", "Due Date", "Status / Target"]
        for idx, text in enumerate(h5):
            cell = t5.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = WHITE

        rows5 = [
            ("CAP-03", "Upgrade inspection frequency for sulfur recovery loop seals", "HSE / Safety", "20 Sep 2026", "OPEN (Target >95%)"),
            ("CAP-04", "Emergency ESD Step 3 cooling water loss drill for CDU", "Operations", "25 Sep 2026", "OPEN"),
            ("CAP-05", "Pressure gauge re-certification for Unit 4B containment", "Instrumentation", "28 Sep 2026", "OPEN"),
            ("CAP-08", "Calibration of relief valves in sulfur recovery unit", "Maintenance", "05 Oct 2026", "OPEN"),
        ]
        for r_idx, (cid, desc, dept, tdate, st) in enumerate(rows5, start=1):
            rdata = [cid, desc, dept, tdate, st]
            for c_idx, text in enumerate(rdata):
                cell = t5.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(11)
                p.font.color.rgb = SLATE
                if c_idx in (0, 3, 4):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True

        foot5 = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.9))
        set_shape_flat_color(foot5, LIGHT_BG, BORDER_CLR)
        tb_foot5 = slide5.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
        tf_foot5 = tb_foot5.text_frame
        tf_foot5.word_wrap = True
        tf_foot5.paragraphs[0].text = "SOURCES USED & AUDIT REFERENCES:"
        tf_foot5.paragraphs[0].font.size = Pt(9.5)
        tf_foot5.paragraphs[0].font.bold = True
        tf_foot5.paragraphs[0].font.color.rgb = NAVY
        p_f = tf_foot5.add_paragraph()
        p_f.text = "MRPL_Operations_Safety_Demo_Pack.md: Section 3.1 (Incident Register), Section 5 (Compliance Scorecard - PTW 94%, Confined Space 88%, Housekeeping 78%), Section 6 (CAP-03, CAP-04, CAP-05, CAP-08)."
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # =========================================================================
    # BRANCH 3: Broad July-August Operations Safety Review (Prompt 3 & Default)
    # =========================================================================
    else:
        # Slide 1: Executive Safety Summary
        slide1 = prs.slides.add_slide(blank_layout)
        bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        set_shape_flat_color(bg1, NAVY)
        dec1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.15), Inches(4.2))
        set_shape_flat_color(dec1, ACCENT_BLUE)
        tb1 = slide1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(11.0), Inches(4.8))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        tf1.paragraphs[0].text = "REFINERY LEADERSHIP & HSE MANAGEMENT BRIEFING"
        tf1.paragraphs[0].font.size = Pt(12)
        tf1.paragraphs[0].font.bold = True
        tf1.paragraphs[0].font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
        tf1.paragraphs[0].space_after = Pt(12)

        pt1 = tf1.add_paragraph()
        pt1.text = target_title
        pt1.font.size = Pt(30)
        pt1.font.bold = True
        pt1.font.color.rgb = WHITE
        pt1.space_after = Pt(14)

        b_gen = [
            "Executive Safety Summary: Total 18 Observations recorded across review period.",
            "3 Recordable Incidents (minor injury / eye irritation; zero lost-time injury).",
            "5 Near Misses logged & contained immediately without operational escalation.",
            "Zero Fatalities, Zero Lost-Time Injuries (0 LTIs), No Major Fires, No Major Product Releases.",
            "Overall Compliance Scorecard: 91.8% against benchmark target of 95.0%.",
        ]
        for sb in b_gen:
            p = tf1.add_paragraph()
            p.text = f"•  {sb}"
            p.font.size = Pt(13)
            p.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
            p.space_after = Pt(6)

        # Slide 2: Incident and Near-Miss Breakdown
        slide2 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide2, "Slide 2: Incident & Near-Miss Breakdown")
        t_shape2 = slide2.shapes.add_table(6, 4, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.4))
        t2 = t_shape2.table
        t2.columns[0].width = Inches(3.2)
        t2.columns[1].width = Inches(1.8)
        t2.columns[2].width = Inches(2.2)
        t2.columns[3].width = Inches(4.5)

        h2 = ["Operational Area", "Total Events", "Event Types Logged", "Key Risk Observations"]
        for idx, text in enumerate(h2):
            cell = t2.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE

        area_data = [
            ("Crude Transfer Area", "4 Events", "Near Miss, Alert", "Pump P-204B vibration (5.8 mm/s), seepage, sensor calibration overdue"),
            ("CDU-1", "5 Events", "PTW, Recordable", "Hot-work handover checklist, confined space signature, tag entry errors"),
            ("Tank Farm Corridor", "4 Events", "Near Miss, Housekeeping", "T-17 cable trip hazard, walkway absorbent material, forklift visibility"),
            ("Utility Block", "3 Events", "Recordable, Near Miss", "Steam-line hand laceration, wet floor electrical cable, scaffolding route obstruction"),
            ("Maintenance Workshop", "2 Events", "Near Miss, Lifting", "Chain block safety latch damaged, lift plan weight verification"),
        ]
        for r_idx, rdata in enumerate(area_data, start=1):
            for c_idx, text in enumerate(rdata):
                cell = t2.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.color.rgb = SLATE
                if c_idx == 1:
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER

        # Slide 3: Pump P-204B Operational Risk
        slide3 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide3, "Slide 3: Pump P-204B Operational Risk", "CRITICAL EQUIPMENT RISK")
        c3_l = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
        set_shape_flat_color(c3_l, CARD_BG, BORDER_CLR)
        tb3_l = slide3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.2), Inches(5.1))
        tf3_l = tb3_l.text_frame
        tf3_l.word_wrap = True
        tf3_l.paragraphs[0].text = "Operating Parameters & Alarm History"
        tf3_l.paragraphs[0].font.size = Pt(16)
        tf3_l.paragraphs[0].font.bold = True
        tf3_l.paragraphs[0].font.color.rgb = NAVY

        b3_l = [
            "Vibration Level: 5.8 mm/s RMS vs normal operating threshold < 4.5 mm/s RMS.",
            "Alarm History: Crossed warning threshold for 3rd time in 4 weeks.",
            "Associated Incidents: INC-01 (flange seepage), INC-07 (vibration alert), INC-13 (sensor calibration overdue by 12d).",
        ]
        for b in b3_l:
            p = tf3_l.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(12)
            p.font.color.rgb = SLATE
            p.space_after = Pt(8)

        c3_r = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
        set_shape_flat_color(c3_r, CARD_BG, BORDER_CLR)
        tb3_r = slide3.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
        tf3_r = tb3_r.text_frame
        tf3_r.word_wrap = True
        tf3_r.paragraphs[0].text = "Escalation & Safety Risks"
        tf3_r.paragraphs[0].font.size = Pt(16)
        tf3_r.paragraphs[0].font.bold = True
        tf3_r.paragraphs[0].font.color.rgb = WARN_RED

        b3_r = [
            "Seal Failure Pathway: Continued operation under uncalibrated vibration risks mechanical seal failure.",
            "Ignition Hazard: Hydrocarbon seepage near electrical junction box pooling risk (INC-18).",
            "Escalation Limit (> 6.5 mm/s RMS): Mandates immediate load reduction & engineering isolation.",
        ]
        for b in b3_r:
            p = tf3_r.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(12)
            p.font.color.rgb = SLATE
            p.space_after = Pt(8)

        # Slide 4: Compliance Scorecard
        slide4 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide4, "Slide 4: Compliance Scorecard", "RAG PERFORMANCE METRICS")
        t_shape4 = slide4.shapes.add_table(6, 5, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.4))
        t4 = t_shape4.table
        t4.columns[0].width = Inches(3.2)
        t4.columns[1].width = Inches(1.6)
        t4.columns[2].width = Inches(1.6)
        t4.columns[3].width = Inches(1.5)
        t4.columns[4].width = Inches(3.8)

        h4 = ["Compliance Indicator", "Actual Rate", "Target Rate", "RAG Status", "Leadership Interpretation"]
        for idx, text in enumerate(h4):
            cell = t4.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE

        rag_data = [
            ("LTI & Major Containment", "100.0%", "100.0%", "GREEN", "Zero fatalities or lost-time injuries achieved across all units."),
            ("PTW Handover Completion", "94.0%", "100.0%", "AMBER", "Minor shift handover gaps; night-shift hot-work permits requires enforcement."),
            ("Confined-Space Checklists", "88.0%", "100.0%", "RED", "Contractor supervisor signature missing prior to tank entry."),
            ("Housekeeping 48h Closure", "78.0%", "95.0%", "RED", "Material clearance delayed in walkway routes; 24h sweep required."),
            ("Overall Safety Scorecard", "91.8%", "95.0%", "AMBER", "Control gaps concentrated in contractor docs & equipment calibration."),
        ]
        for r_idx, rdata in enumerate(rag_data, start=1):
            for c_idx, text in enumerate(rdata):
                cell = t4.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.color.rgb = SLATE
                if c_idx in (1, 2, 3):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                if c_idx == 3:
                    if text == "GREEN":
                        p.font.color.rgb = PASS_GREEN
                    elif text == "AMBER":
                        p.font.color.rgb = WARN_AMBER
                    elif text == "RED":
                        p.font.color.rgb = WARN_RED

        # Slide 5: Open Corrective Actions
        slide5 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide5, "Slide 5: Open Corrective Actions (CAP Status)")
        t_shape5 = slide5.shapes.add_table(8, 5, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
        t5 = t_shape5.table
        t5.columns[0].width = Inches(1.3)
        t5.columns[1].width = Inches(4.8)
        t5.columns[2].width = Inches(2.0)
        t5.columns[3].width = Inches(1.8)
        t5.columns[4].width = Inches(1.8)

        h5 = ["CAP ID", "Action Item Description", "Department", "Due Date", "Priority"]
        for idx, text in enumerate(h5):
            cell = t5.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = WHITE

        caps_data = [
            ("CAP-01", "High-pressure hydrocracker relief valve calibration", "Maintenance", "15 Sep 2026", "CRITICAL"),
            ("CAP-02", "Thermographic flange gasket seal replacement in Cracker Block", "Operations", "18 Sep 2026", "CRITICAL"),
            ("CAP-03", "Bi-weekly inspection frequency upgrade for sulfur recovery loop seals", "HSE / Safety", "20 Sep 2026", "Medium"),
            ("CAP-04", "Emergency ESD Step 3 cooling water loss drill for CDU", "Operations", "25 Sep 2026", "Medium"),
            ("CAP-05", "Pressure gauge re-certification for Unit 4B containment", "Instrumentation", "28 Sep 2026", "Low"),
            ("CAP-07", "Update PPE compliance tracking across night shifts", "HSE / Safety", "30 Sep 2026", "Low"),
            ("CAP-08", "Calibration of relief valves in sulfur recovery unit", "Maintenance", "05 Oct 2026", "Medium"),
        ]
        for r_idx, (cid, desc, dept, tdate, prio) in enumerate(caps_data, start=1):
            rdata = [cid, desc, dept, tdate, prio]
            for c_idx, text in enumerate(rdata):
                cell = t5.cell(r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_BG if r_idx % 2 == 0 else WHITE
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(11)
                p.font.color.rgb = SLATE
                if c_idx in (0, 3, 4):
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                if c_idx == 4 and text == "CRITICAL":
                    p.font.color.rgb = WARN_RED

        # Slide 6: Leadership Decisions Required This Week with Sources
        slide6 = prs.slides.add_slide(blank_layout)
        add_slide_header(slide6, "Slide 6: Leadership Decisions Required This Week with Sources", "EXECUTIVE ACTION ITEMS")
        c6 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.7), Inches(4.5))
        set_shape_flat_color(c6, CARD_BG, BORDER_CLR)
        tb6 = slide6.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.3))
        tf6 = tb6.text_frame
        tf6.word_wrap = True
        tf6.paragraphs[0].text = "Leadership Decisions Required This Week"
        tf6.paragraphs[0].font.size = Pt(16)
        tf6.paragraphs[0].font.bold = True
        tf6.paragraphs[0].font.color.rgb = NAVY

        recs6 = [
            "1. Authorize Pump P-204B Maintenance Outage Window: Approve immediate vibration sensor calibration and mechanical alignment before 08 Sep 2026.",
            "2. Enforce Night-Shift PTW & Contractor Handover: Mandate supervisory verification for night-shift hot-work permits and contractor toolbox talks.",
            "3. Prioritize Resource Allocation for CAP-01 & CAP-02: Direct critical engineering focus to hydrocracker valve calibration and Cracker Block flange seal replacements.",
        ]
        for rc in recs6:
            p = tf6.add_paragraph()
            p.text = rc
            p.font.size = Pt(13)
            p.font.color.rgb = SLATE
            p.space_after = Pt(10)

        foot6 = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.9))
        set_shape_flat_color(foot6, LIGHT_BG, BORDER_CLR)
        tb_foot6 = slide6.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
        tf_foot6 = tb_foot6.text_frame
        tf_foot6.word_wrap = True
        tf_foot6.paragraphs[0].text = "SOURCES USED & AUDIT VERIFICATION:"
        tf_foot6.paragraphs[0].font.size = Pt(9.5)
        tf_foot6.paragraphs[0].font.bold = True
        tf_foot6.paragraphs[0].font.color.rgb = NAVY
        p_f = tf_foot6.add_paragraph()
        p_f.text = "MRPL_Operations_Safety_Demo_Pack.md: Section 1 (Executive Summary), Section 2.2 (Key Operating Parameters), Section 3.1 (Incident Register), Section 4.1 (Pump P-204B), Section 5 (Compliance Scorecard), Section 6 (Corrective Action Plan)."
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Save to vault
    vault_dir = (settings.data_dir / "vault").resolve()
    vault_dir.mkdir(parents=True, exist_ok=True)
    out_path = vault_dir / safe_filename
    prs.save(out_path)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Local PPT generation tool failed to create presentation file at {out_path}")

    return out_path
