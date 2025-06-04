from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import Text

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='receptionist')  # admin, doctor, receptionist, financial
    crm = db.Column(db.String(20))  # For doctors
    specialty = db.Column(db.String(100))  # For doctors
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    medical_history = db.Column(Text)
    allergies = db.Column(Text)
    current_medications = db.Column(Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)
    payments = db.relationship('Payment', backref='patient', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=60)  # Duration in minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled
    notes = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('User', backref='appointments')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    chief_complaint = db.Column(Text)  # Queixa principal
    anamnesis = db.Column(Text)  # Anamnese
    symptoms = db.Column(Text)  # Sintomas
    physical_exam = db.Column(Text)  # Exame físico
    diagnosis = db.Column(Text)  # Diagnóstico
    treatment_plan = db.Column(Text)  # Conduta médica
    observations = db.Column(Text)
    
    # Relationships
    doctor = db.relationship('User', backref='medical_records')
    appointment = db.relationship('Appointment', backref='medical_record')

class Supplement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # vitamin, mineral, amino_acid, herb, etc.
    description = db.Column(Text)
    dosage_info = db.Column(Text)  # Posologia
    observations = db.Column(Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # blood, urine, hormone, etc.
    reference_values = db.Column(Text)  # Valores de referência
    unit = db.Column(db.String(20))  # mg/dL, g/L, etc.
    description = db.Column(Text)
    observations = db.Column(Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hemogram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nome do parâmetro
    parameter_type = db.Column(db.String(50))  # hemaceas, leucocitos, plaquetas, etc.
    reference_values = db.Column(Text)  # Valores de referência
    unit = db.Column(db.String(20))  # milhões/mm³, mil/mm³, %, etc.
    description = db.Column(Text)  # Descrição do parâmetro
    observations = db.Column(Text)  # Observações clínicas
    clinical_significance = db.Column(Text)  # Significado clínico
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_record.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    custom_formulas = db.Column(Text)  # Fórmulas manipuladas
    supplements_prescribed = db.Column(Text)  # JSON with supplement IDs and dosages
    lab_tests_requested = db.Column(Text)  # JSON with lab test IDs
    additional_instructions = db.Column(Text)
    observations = db.Column(Text)
    
    # Relationships
    doctor = db.relationship('User', backref='prescriptions')
    medical_record = db.relationship('MedicalRecord', backref='prescriptions')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, pix, transfer
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    receipt_number = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(20), default='paid')  # paid, pending, cancelled
    
    # Relationships
    appointment = db.relationship('Appointment', backref='payments')
    doctor = db.relationship('User', backref='payments_received')

class ChatConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    message = db.Column(Text, nullable=False)
    response = db.Column(Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.String(20), default='patient')  # patient, staff
