from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.core.files.base import ContentFile
from io import BytesIO
import datetime


def generate_invoice_pdf(invoice):
    """
    Generate PDF invoice for an appointment
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
    )
    
    # Title
    title = Paragraph("VISHUBH HEALTHCARE", title_style)
    elements.append(title)
    
    subtitle = Paragraph("Medical Invoice", styles['Heading2'])
    elements.append(subtitle)
    elements.append(Spacer(1, 12))
    
    # Invoice details
    invoice_data = [
        ['Invoice Number:', f'#{invoice.id}'],
        ['Date:', invoice.generated_date.strftime('%d %B %Y')],
        ['Status:', 'PAID' if invoice.appointment.status == 'completed' else 'PENDING'],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading_style))
    patient = invoice.appointment.patient
    patient_data = [
        ['Name:', patient.user.get_full_name()],
        ['Contact:', patient.contact],
        ['Age:', str(patient.age) if patient.age else 'N/A'],
        ['Blood Group:', patient.blood_group if patient.blood_group else 'N/A'],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))
    
    # Doctor Information
    elements.append(Paragraph("Doctor Information", heading_style))
    doctor = invoice.appointment.doctor
    doctor_data = [
        ['Doctor:', f"Dr. {doctor.user.get_full_name()}"],
        ['Specialization:', doctor.specialization],
        ['Contact:', doctor.contact],
    ]
    
    doctor_table = Table(doctor_data, colWidths=[2*inch, 4*inch])
    doctor_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(doctor_table)
    elements.append(Spacer(1, 20))
    
    # Appointment Details
    elements.append(Paragraph("Appointment Details", heading_style))
    appointment_data = [
        ['Date:', invoice.appointment.appointment_date.strftime('%d %B %Y')],
        ['Time:', invoice.appointment.appointment_time.strftime('%I:%M %p')],
        ['Symptoms:', invoice.appointment.symptoms],
    ]
    
    appointment_table = Table(appointment_data, colWidths=[2*inch, 4*inch])
    appointment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(appointment_table)
    elements.append(Spacer(1, 30))
    
    # Billing Information
    elements.append(Paragraph("Billing Summary", heading_style))
    billing_data = [
        ['Description', 'Amount'],
        ['Consultation Fee', f'₹{invoice.amount}'],
        ['', ''],
        ['Total Amount', f'₹{invoice.amount}'],
    ]
    
    billing_table = Table(billing_data, colWidths=[4*inch, 2*inch])
    billing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ('GRID', (0, 0), (-1, -2), 1, colors.grey),
        ('BOX', (0, -1), (-1, -1), 2, colors.HexColor('#2563eb')),
    ]))
    elements.append(billing_table)
    elements.append(Spacer(1, 40))
    
    # Footer
    footer_text = Paragraph(
        "Thank you for choosing Vishubh Healthcare!<br/>For any queries, please contact us.",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and save it to the model
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
