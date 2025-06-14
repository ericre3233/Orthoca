import requests
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
import json
import re

def clean_prescription_text(text):
    """Remove section markers from prescription text for PDF generation"""
    if not text:
        return ""
    
    # Remove the section markers
    text = re.sub(r'--- Suplementos Selecionados ---', '', text)
    text = re.sub(r'--- Fim dos Suplementos ---', '', text)
    
    # Clean up extra whitespace and line breaks
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
    text = text.strip()
    
    return text

def send_appointment_confirmation(patient, appointment):
    """Send appointment confirmation via API"""
    try:
        payload = {
            "nome": patient.name,
            "contato": patient.phone,
            "email": patient.email or "",
            "mensagem": f"Sua consulta foi agendada para {appointment.appointment_date.strftime('%d/%m/%Y às %H:%M')}.",
            "canal": "whatsapp"
        }
        
        response = requests.post(
            'http://localhost:8001/api/send',
            json=payload,
            timeout=10
        )
        
        if response.ok:
            print(f"Confirmation sent successfully for appointment {appointment.id}")
        else:
            print(f"Failed to send confirmation: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending confirmation: {str(e)}")

def generate_prescription_pdf(prescription):
    """Generate PDF for prescription"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add clinic name
    clinic_style = ParagraphStyle(
        'ClinicStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#007bff'),
        alignment=1  # Center alignment
    )
    story.append(Paragraph("CLÍNICA ORTOMOLECULAR", clinic_style))
    story.append(Spacer(1, 20))

    # Add doctor info
    doctor_style = ParagraphStyle(
        'DoctorStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1
    )
    story.append(Paragraph(f"Dr. {prescription.doctor.name}", doctor_style))
    story.append(Paragraph(f"CRM: {prescription.doctor.crm or 'N/A'}", doctor_style))
    story.append(Paragraph(f"Especialidade: {prescription.doctor.specialty or 'Medicina Ortomolecular'}", doctor_style))
    story.append(Spacer(1, 20))

    # Add patient info
    patient_data = [
        ["Paciente:", prescription.patient.name],
        ["Data de Nascimento:", prescription.patient.birth_date.strftime('%d/%m/%Y')],
        ["CPF:", prescription.patient.cpf],
        ["Data da Prescrição:", prescription.date.strftime('%d/%m/%Y')]
    ]
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 20))

    # Add custom formulas if any
    if prescription.custom_formulas:
        story.append(Paragraph("FÓRMULAS MANIPULADAS", styles['Heading2']))
        story.append(Paragraph(clean_prescription_text(prescription.custom_formulas), styles['Normal']))
        story.append(Spacer(1, 20))

    # Add supplements if any
    if prescription.supplements_prescribed:
        try:
            supplement_ids = json.loads(prescription.supplements_prescribed)
            from models import Supplement
            supplements_data = Supplement.query.filter(Supplement.id.in_(supplement_ids)).all()
            
            if supplements_data:
                story.append(Paragraph("SUPLEMENTOS PRESCRITOS", styles['Heading2']))
                for sup in supplements_data:
                    story.append(Paragraph(f"<b>{sup.name}</b>", styles['Normal']))
                    story.append(Paragraph(sup.dosage_info or "Conforme orientação médica", styles['Normal']))
                    story.append(Spacer(1, 10))
        except:
            pass
    
    # Add lab tests if any
    if prescription.lab_tests_requested:
        try:
            lab_test_ids = json.loads(prescription.lab_tests_requested)
            from models import LabTest
            lab_tests_data = LabTest.query.filter(LabTest.id.in_(lab_test_ids)).all()
            
            if lab_tests_data:
                story.append(Paragraph("EXAMES SOLICITADOS", styles['Heading2']))
                for test in lab_tests_data:
                    story.append(Paragraph(f"{test.name} - {test.description or ''}", styles['Normal']))
                    story.append(Spacer(1, 10))
        except:
            pass
    
    # Add additional instructions if any
    if prescription.additional_instructions:
        story.append(Paragraph("INSTRUÇÕES ADICIONAIS", styles['Heading2']))
        story.append(Paragraph(prescription.additional_instructions, styles['Normal']))
        story.append(Spacer(1, 20))

    # Add observations if any
    if prescription.observations:
        story.append(Paragraph("OBSERVAÇÕES", styles['Heading2']))
        story.append(Paragraph(prescription.observations, styles['Normal']))
        story.append(Spacer(1, 20))

    # Add signature
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1
    )
    story.append(Paragraph("_" * 40, signature_style))
    story.append(Paragraph(f"Dr. {prescription.doctor.name}", signature_style))
    story.append(Paragraph(f"CRM: {prescription.doctor.crm or 'N/A'}", signature_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_receipt_pdf(payment):
    """Generate PDF receipt for payment"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add clinic name
    clinic_style = ParagraphStyle(
        'ClinicStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#28a745'),
        alignment=1
    )
    story.append(Paragraph("CLÍNICA ORTOMOLECULAR", clinic_style))
    story.append(Paragraph("RECIBO DE PAGAMENTO", clinic_style))
    story.append(Spacer(1, 20))

    # Add receipt info
    payment_methods = {
        'cash': 'Dinheiro',
        'card': 'Cartão',
        'pix': 'PIX',
        'transfer': 'Transferência'
    }

    receipt_data = [
        ["Recibo Nº:", payment.receipt_number],
        ["Data:", payment.payment_date.strftime('%d/%m/%Y %H:%M')],
        ["Paciente:", payment.patient.name],
        ["CPF:", payment.patient.cpf],
        ["Forma de Pagamento:", payment_methods.get(payment.payment_method, payment.payment_method)]
    ]
    
    if payment.description:
        receipt_data.append(["Descrição:", payment.description])

    receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 20))

    # Add amount
    amount_style = ParagraphStyle(
        'AmountStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#28a745'),
        alignment=1
    )
    story.append(Paragraph(f"VALOR: R$ {payment.amount:.2f}", amount_style))
    story.append(Spacer(1, 40))

    # Add signature
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1
    )
    story.append(Paragraph("_" * 40, signature_style))
    story.append(Paragraph("Assinatura", signature_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
