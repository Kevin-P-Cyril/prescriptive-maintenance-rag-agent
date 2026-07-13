"""
Generates a sample industrial maintenance manual PDF (with tables and
multiple sections/pages) so the project can be demoed end-to-end without
requiring the user to source a real manual first.

Usage:
    python scripts/generate_sample_manual.py
"""
from pathlib import Path

from fpdf import FPDF

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "manuals" / "cnc_204_maintenance_manual.pdf"


def build_pdf() -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Cover / Section 1 ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "CNC-204 Milling Machine", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Technical Maintenance & Repair Manual", ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "1. Overview", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0, 6,
        "The CNC-204 is a 3-axis precision milling machine used for machining metal and "
        "composite parts. This manual covers routine maintenance, common fault diagnosis, "
        "and step-by-step repair procedures for field technicians. Always isolate power "
        "and follow lockout/tagout (LOTO) procedures before performing any maintenance."
    )

    # --- Section 2: Spindle overheating ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "2. Fault Code E-108: Spindle Overheating", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0, 6,
        "Error E-108 is triggered when the spindle temperature sensor reports a reading "
        "above 75 degrees C for more than 30 continuous seconds. Overheating is most "
        "commonly caused by worn spindle bearings, insufficient coolant flow, or a "
        "degraded coolant pump. Left unaddressed, this can cause permanent spindle damage."
    )
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "2.1 Diagnostic Steps", ln=True)
    pdf.set_font("Helvetica", "", 11)
    steps = [
        "Step 1: Power down the machine and engage lockout/tagout.",
        "Step 2: Inspect the coolant reservoir level; refill if below the minimum line.",
        "Step 3: Check the coolant pump (Part SKU: CLP-0876) for flow output; replace if flow is below 2 L/min.",
        "Step 4: Remove the spindle housing cover and inspect the spindle bearing set (Part SKU: SPB-2201) for pitting, discoloration, or excessive play.",
        "Step 5: If bearing play exceeds 0.05mm radial clearance, replace the spindle bearing set.",
        "Step 6: Reassemble, refill coolant, and run a 10-minute idle test while monitoring spindle temperature.",
    ]
    for s in steps:
        pdf.multi_cell(0, 6, s)
        pdf.ln(1)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "2.2 Torque Specifications", ln=True)
    pdf.set_font("Helvetica", "", 10)

    # Table of torque specs
    headers = ["Component", "Fastener", "Torque (Nm)"]
    rows = [
        ["Spindle housing cover", "M6 bolt", "9.5"],
        ["Bearing retainer plate", "M5 bolt", "6.0"],
        ["Coolant pump mount", "M8 bolt", "18.0"],
        ["Drive belt tensioner", "M6 bolt", "9.5"],
    ]
    col_widths = [80, 50, 40]
    pdf.set_fill_color(230, 230, 230)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    for row in rows:
        for val, w in zip(row, col_widths):
            pdf.cell(w, 7, val, border=1)
        pdf.ln()

    # --- Section 3: Drive belt / conveyor faults ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "3. Fault Code E-212: Drive Belt Slippage", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0, 6,
        "Error E-212 indicates the X-axis drive belt encoder has detected slippage "
        "greater than 2 percent between commanded and actual position. This is usually "
        "caused by a worn or under-tensioned drive belt (Part SKU: DBT-1145)."
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "3.1 Repair Procedure", ln=True)
    pdf.set_font("Helvetica", "", 11)
    steps2 = [
        "Step 1: Power down and lockout/tagout the machine.",
        "Step 2: Remove the axis cover panel (4x M4 screws).",
        "Step 3: Inspect the drive belt for cracking, glazing, or fraying.",
        "Step 4: If damaged, replace with Drive Belt (Type A), SKU DBT-1145.",
        "Step 5: Set belt tension using a tension gauge to 45-50 N; adjust via the tensioner bolt to 9.5 Nm torque.",
        "Step 6: Reinstall the axis cover and run the axis homing cycle to confirm the fault has cleared.",
    ]
    for s in steps2:
        pdf.multi_cell(0, 6, s)
        pdf.ln(1)

    # --- Section 4: Servo / encoder faults ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "4. Fault Code E-330: Servo Encoder Fault", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0, 6,
        "Error E-330 signals a loss of signal from the servo motor encoder (Part SKU: "
        "SME-5521), typically caused by a damaged encoder cable or a failed encoder unit. "
        "This fault requires immediate machine shutdown to prevent uncontrolled axis motion."
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "4.1 Repair Procedure", ln=True)
    pdf.set_font("Helvetica", "", 11)
    steps3 = [
        "Step 1: Power down and lockout/tagout the machine immediately.",
        "Step 2: Disconnect and visually inspect the encoder cable for pinching or fraying.",
        "Step 3: If the cable is intact, test encoder output using a multimeter at the terminal block.",
        "Step 4: If no signal is present, replace the Servo Motor Encoder, SKU SME-5521.",
        "Step 5: Recalibrate axis zero position after replacement using the controller's homing wizard.",
        "Step 6: Verify by jogging the axis and confirming smooth position feedback with no fault codes.",
    ]
    for s in steps3:
        pdf.multi_cell(0, 6, s)
        pdf.ln(1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "4.2 Safety Notice", ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(
        0, 6,
        "Only qualified technicians should perform electrical repairs. Always verify "
        "zero-energy state with a voltage tester before touching any electrical components."
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT_PATH))
    print(f"Sample manual written to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
