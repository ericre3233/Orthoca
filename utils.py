import requests
from io import BytesIO
from weasyprint import HTML, CSS
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
    
    # Parse supplements and lab tests
    supplements_data = []
    if prescription.supplements_prescribed:
        try:
            supplement_ids = json.loads(prescription.supplements_prescribed)
            from models import Supplement
            supplements_data = Supplement.query.filter(Supplement.id.in_(supplement_ids)).all()
        except:
            pass
    
    lab_tests_data = []
    if prescription.lab_tests_requested:
        try:
            lab_test_ids = json.loads(prescription.lab_tests_requested)
            from models import LabTest
            lab_tests_data = LabTest.query.filter(LabTest.id.in_(lab_test_ids)).all()
        except:
            pass
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Prescrição Médica</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
            .clinic-name {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .doctor-info {{ margin-top: 10px; }}
            .patient-info {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 20px; }}
            .section {{ margin-bottom: 20px; }}
            .section-title {{ font-weight: bold; color: #007bff; border-bottom: 1px solid #dee2e6; padding-bottom: 5px; }}
            .prescription-item {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; }}
            .footer {{ margin-top: 50px; text-align: center; }}
            .signature {{ border-top: 1px solid #000; width: 300px; margin: 20px auto 0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="clinic-name">CLÍNICA ORTOMOLECULAR</div>
            <div class="doctor-info">
                <div>Dr. {prescription.doctor.name}</div>
                <div>CRM: {prescription.doctor.crm or 'N/A'}</div>
                <div>Especialidade: {prescription.doctor.specialty or 'Medicina Ortomolecular'}</div>
            </div>
        </div>
        
        <div class="patient-info">
            <strong>Paciente:</strong> {prescription.patient.name}<br>
            <strong>Data de Nascimento:</strong> {prescription.patient.birth_date.strftime('%d/%m/%Y')}<br>
            <strong>CPF:</strong> {prescription.patient.cpf}<br>
            <strong>Data da Prescrição:</strong> {prescription.date.strftime('%d/%m/%Y')}
        </div>
        
        {f'''
        <div class="section">
            <div class="section-title">FÓRMULAS MANIPULADAS</div>
            <div style="white-space: pre-line;">{clean_prescription_text(prescription.custom_formulas)}</div>
        </div>
        ''' if prescription.custom_formulas else ''}
        
        {f'''
        <div class="section">
            <div class="section-title">SUPLEMENTOS PRESCRITOS</div>
            {''.join([f'<div class="prescription-item"><strong>{sup.name}</strong><br>{sup.dosage_info or "Conforme orientação médica"}</div>' for sup in supplements_data])}
        </div>
        ''' if supplements_data else ''}
        
        {f'''
        <div class="section">
            <div class="section-title">EXAMES SOLICITADOS</div>
            {''.join([f'<div class="prescription-item">{test.name} - {test.description or ""}</div>' for test in lab_tests_data])}
        </div>
        ''' if lab_tests_data else ''}
        
        {f'''
        <div class="section">
            <div class="section-title">INSTRUÇÕES ADICIONAIS</div>
            <div style="white-space: pre-line;">{prescription.additional_instructions}</div>
        </div>
        ''' if prescription.additional_instructions else ''}
        
        {f'''
        <div class="section">
            <div class="section-title">OBSERVAÇÕES</div>
            <div style="white-space: pre-line;">{prescription.observations}</div>
        </div>
        ''' if prescription.observations else ''}
        
        <div class="footer">
            <div class="signature">
                Dr. {prescription.doctor.name}<br>
                CRM: {prescription.doctor.crm or 'N/A'}
            </div>
        </div>
    </body>
    </html>
    """
    
    html_doc = HTML(string=html_content)
    pdf_buffer = BytesIO()
    html_doc.write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def generate_receipt_pdf(payment):
    """Generate PDF receipt for payment"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Recibo de Pagamento</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; border-bottom: 2px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; }}
            .clinic-name {{ font-size: 24px; font-weight: bold; color: #28a745; }}
            .receipt-info {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 20px; }}
            .amount {{ font-size: 24px; font-weight: bold; color: #28a745; text-align: center; margin: 20px 0; }}
            .footer {{ margin-top: 50px; text-align: center; }}
            .signature {{ border-top: 1px solid #000; width: 300px; margin: 20px auto 0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="clinic-name">CLÍNICA ORTOMOLECULAR</div>
            <div>RECIBO DE PAGAMENTO</div>
        </div>
        
        <div class="receipt-info">
            <strong>Recibo Nº:</strong> {payment.receipt_number}<br>
            <strong>Data:</strong> {payment.payment_date.strftime('%d/%m/%Y %H:%M')}<br>
            <strong>Paciente:</strong> {payment.patient.name}<br>
            <strong>CPF:</strong> {payment.patient.cpf}<br>
            {f'<strong>Descrição:</strong> {payment.description}<br>' if payment.description else ''}
            <strong>Forma de Pagamento:</strong> {dict([
                ('cash', 'Dinheiro'),
                ('card', 'Cartão'),
                ('pix', 'PIX'),
                ('transfer', 'Transferência')
            ]).get(payment.payment_method, payment.payment_method)}
        </div>
        
        <div class="amount">
            VALOR: R$ {payment.amount:.2f}
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            Recebi a quantia acima referente aos serviços prestados.
        </div>
        
        <div class="footer">
            <div class="signature">
                Clínica Ortomolecular<br>
                Assinatura do Responsável
            </div>
        </div>
    </body>
    </html>
    """
    
    html_doc = HTML(string=html_content)
    pdf_buffer = BytesIO()
    html_doc.write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
