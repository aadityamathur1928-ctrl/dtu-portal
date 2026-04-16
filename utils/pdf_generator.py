import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# DTU brand colors
DTU_RED = colors.HexColor('#8B0000')
DTU_DARK = colors.HexColor('#1A1A2E')
LIGHT_GRAY = colors.HexColor('#F5F5F5')
BORDER_GRAY = colors.HexColor('#CCCCCC')
TEXT_DARK = colors.HexColor('#333333')


def generate_admit_card(student, exams) -> io.BytesIO:
    """Generate a PDF Admit Card for the given student and exam list."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Header ──────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
                                  fontSize=18, fontName='Helvetica-Bold',
                                  textColor=DTU_RED, alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'],
                                     fontSize=11, fontName='Helvetica',
                                     textColor=TEXT_DARK, alignment=TA_CENTER, spaceAfter=2)
    small_center = ParagraphStyle('SmallCenter', parent=styles['Normal'],
                                   fontSize=9, fontName='Helvetica',
                                   textColor=colors.gray, alignment=TA_CENTER)
    doc_title_style = ParagraphStyle('DocTitle', parent=styles['Normal'],
                                      fontSize=13, fontName='Helvetica-Bold',
                                      textColor=colors.white, alignment=TA_CENTER)

    elements.append(Paragraph("DELHI TECHNOLOGICAL UNIVERSITY", title_style))
    elements.append(Paragraph("(Formerly Delhi College of Engineering)", subtitle_style))
    elements.append(Paragraph("Shahbad Daulatpur, Main Bawana Road, Delhi – 110042", small_center))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=DTU_RED))
    elements.append(Spacer(1, 0.2 * cm))

    # Admit card title banner
    banner_data = [[Paragraph("ADMIT CARD – END SEMESTER EXAMINATION", doc_title_style)]]
    banner_table = Table(banner_data, colWidths=[16.7 * cm])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DTU_RED),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Student Details ─────────────────────────────────────────────────────────
    field_label = ParagraphStyle('Label', parent=styles['Normal'],
                                  fontSize=9, fontName='Helvetica-Bold', textColor=DTU_DARK)
    field_value = ParagraphStyle('Value', parent=styles['Normal'],
                                  fontSize=10, fontName='Helvetica', textColor=TEXT_DARK)

    student_data = [
        [Paragraph('Roll Number', field_label), Paragraph(str(student.roll_number), field_value),
         Paragraph('Programme', field_label), Paragraph(str(student.programme or 'B.Tech'), field_value)],
        [Paragraph('Student Name', field_label), Paragraph(str(student.name), field_value),
         Paragraph('Branch', field_label), Paragraph(str(student.branch or '—'), field_value)],
        [Paragraph('Semester', field_label), Paragraph(str(student.semester or '—'), field_value),
         Paragraph('Date of Issue', field_label), Paragraph(str(date.today().strftime('%d %B %Y')), field_value)],
    ]

    student_table = Table(student_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 4.7 * cm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Exam Schedule Table ─────────────────────────────────────────────────────
    section_header = ParagraphStyle('SectionHeader', parent=styles['Normal'],
                                     fontSize=11, fontName='Helvetica-Bold',
                                     textColor=DTU_DARK, spaceAfter=6)
    elements.append(Paragraph("Examination Schedule", section_header))

    col_header_style = ParagraphStyle('ColHeader', parent=styles['Normal'],
                                       fontSize=9, fontName='Helvetica-Bold',
                                       textColor=colors.white, alignment=TA_CENTER)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'],
                                 fontSize=9, fontName='Helvetica',
                                 textColor=TEXT_DARK, alignment=TA_CENTER)
    cell_left = ParagraphStyle('CellLeft', parent=styles['Normal'],
                                fontSize=9, fontName='Helvetica', textColor=TEXT_DARK)

    if exams:
        headers = ['S.No.', 'Subject Code', 'Subject Name', 'Date', 'Time', 'Duration', 'Venue']
        exam_rows = [[
            Paragraph(h, col_header_style) for h in headers
        ]]

        for i, exam in enumerate(exams, 1):
            exam_rows.append([
                Paragraph(str(i), cell_style),
                Paragraph(exam.subject_code, cell_style),
                Paragraph(exam.subject_name, cell_left),
                Paragraph(exam.exam_date.strftime('%d-%m-%Y'), cell_style),
                Paragraph(exam.exam_time, cell_style),
                Paragraph(f"{exam.duration_hours} Hrs", cell_style),
                Paragraph(exam.venue or '—', cell_style),
            ])

        exam_table = Table(
            exam_rows,
            colWidths=[1 * cm, 2.5 * cm, 5.5 * cm, 2.5 * cm, 1.8 * cm, 1.5 * cm, 2.4 * cm]
        )
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DTU_RED),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(exam_table)
    else:
        elements.append(Paragraph("No upcoming examinations found.", field_value))

    elements.append(Spacer(1, 0.6 * cm))

    # ── Instructions ────────────────────────────────────────────────────────────
    instructions_header = ParagraphStyle('InstHeader', parent=styles['Normal'],
                                          fontSize=10, fontName='Helvetica-Bold',
                                          textColor=DTU_DARK)
    instruction_text = ParagraphStyle('Inst', parent=styles['Normal'],
                                       fontSize=8.5, fontName='Helvetica',
                                       textColor=TEXT_DARK, leading=14)

    elements.append(Paragraph("Important Instructions", instructions_header))
    instructions = [
        "1. This Admit Card must be produced at the Examination Centre for entry into the Examination Hall.",
        "2. Students must carry a valid DTU Identity Card along with this Admit Card.",
        "3. Entry is not allowed in the Examination Hall 30 minutes after the commencement of the Examination.",
        "4. Use of mobile phones, electronic gadgets, or any other unfair means is strictly prohibited.",
        "5. Students are not permitted to leave the Examination Hall during the first 30 minutes.",
        "6. This Admit Card is provisional and subject to verification of eligibility.",
    ]
    for inst in instructions:
        elements.append(Paragraph(inst, instruction_text))

    elements.append(Spacer(1, 1 * cm))

    # ── Signature Section ────────────────────────────────────────────────────────
    sign_style = ParagraphStyle('Sign', parent=styles['Normal'],
                                 fontSize=9, fontName='Helvetica', alignment=TA_CENTER)
    sign_bold = ParagraphStyle('SignBold', parent=styles['Normal'],
                                fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER)

    sign_data = [
        [Paragraph("", sign_style), Paragraph("", sign_style), Paragraph("", sign_style)],
        [Paragraph("________________________", sign_style),
         Paragraph("________________________", sign_style),
         Paragraph("________________________", sign_style)],
        [Paragraph("Student Signature", sign_style),
         Paragraph("Invigilator Signature", sign_style),
         Paragraph("Controller of Examinations", sign_bold)],
    ]
    sign_table = Table(sign_data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sign_table)

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER_GRAY))
    footer = ParagraphStyle('Footer', parent=styles['Normal'],
                             fontSize=7.5, fontName='Helvetica',
                             textColor=colors.gray, alignment=TA_CENTER, spaceBefore=4)
    elements.append(Paragraph(
        "This is a computer-generated document. For queries, contact: examdtu@gmail.com | 011-27892202",
        footer
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
