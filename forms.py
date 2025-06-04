from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DateTimeField, FloatField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Perfil', choices=[
        ('admin', 'Administrador'),
        ('doctor', 'Médico'),
        ('receptionist', 'Recepcionista'),
        ('financial', 'Financeiro')
    ], validators=[DataRequired()])
    crm = StringField('CRM', validators=[Optional(), Length(max=20)])
    specialty = StringField('Especialidade', validators=[Optional(), Length(max=100)])
    password = PasswordField('Senha', validators=[Optional()])

class PatientForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired()])
    phone = StringField('Telefone', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Endereço', validators=[Optional(), Length(max=200)])
    medical_history = TextAreaField('Histórico Médico', validators=[Optional()])
    allergies = TextAreaField('Alergias', validators=[Optional()])
    current_medications = TextAreaField('Medicamentos Atuais', validators=[Optional()])
    emergency_contact = StringField('Contato de Emergência', validators=[Optional(), Length(max=100)])
    emergency_phone = StringField('Telefone de Emergência', validators=[Optional(), Length(max=20)])

class AppointmentForm(FlaskForm):
    patient_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Médico', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeField('Data e Hora', validators=[DataRequired()], 
                                   default=datetime.now, format='%Y-%m-%dT%H:%M')
    duration = SelectField('Duração', choices=[
        (30, '30 minutos'),
        (60, '60 minutos'),
        (90, '90 minutos'),
        (120, '120 minutos')
    ], coerce=int, default=60)
    notes = TextAreaField('Observações', validators=[Optional()])

class MedicalRecordForm(FlaskForm):
    chief_complaint = TextAreaField('Queixa Principal', validators=[Optional()])
    anamnesis = TextAreaField('Anamnese', validators=[Optional()])
    symptoms = TextAreaField('Sintomas', validators=[Optional()])
    physical_exam = TextAreaField('Exame Físico', validators=[Optional()])
    diagnosis = TextAreaField('Diagnóstico', validators=[Optional()])
    treatment_plan = TextAreaField('Conduta Médica', validators=[Optional()])
    observations = TextAreaField('Observações', validators=[Optional()])

class SupplementForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Categoria', choices=[
        ('vitamin', 'Vitamina'),
        ('mineral', 'Mineral'),
        ('amino_acid', 'Aminoácido'),
        ('herb', 'Fitoterápico'),
        ('probiotic', 'Probiótico'),
        ('enzyme', 'Enzima'),
        ('other', 'Outros')
    ], validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional()])
    dosage_info = TextAreaField('Posologia', validators=[Optional()])
    observations = TextAreaField('Observações', validators=[Optional()])
    is_active = BooleanField('Ativo', default=True)

class LabTestForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Categoria', choices=[
        ('blood', 'Sangue'),
        ('urine', 'Urina'),
        ('hormone', 'Hormonal'),
        ('metabolic', 'Metabólico'),
        ('immune', 'Imunológico'),
        ('other', 'Outros')
    ], validators=[DataRequired()])
    reference_values = TextAreaField('Valores de Referência', validators=[Optional()])
    unit = StringField('Unidade', validators=[Optional(), Length(max=20)])
    description = TextAreaField('Descrição', validators=[Optional()])
    observations = TextAreaField('Observações', validators=[Optional()])
    is_active = BooleanField('Ativo', default=True)

class HemogramForm(FlaskForm):
    name = StringField('Nome do Parâmetro', validators=[DataRequired(), Length(max=100)])
    parameter_type = SelectField('Tipo de Parâmetro', choices=[
        ('hemaceas', 'Hemácias'),
        ('hemoglobina', 'Hemoglobina'),
        ('hematocrito', 'Hematócrito'),
        ('vcm', 'VCM (Volume Corpuscular Médio)'),
        ('hcm', 'HCM (Hemoglobina Corpuscular Média)'),
        ('chcm', 'CHCM (Concentração de Hemoglobina Corpuscular Média)'),
        ('rdw', 'RDW (Red Cell Distribution Width)'),
        ('leucocitos', 'Leucócitos'),
        ('neutrofilos', 'Neutrófilos'),
        ('linfocitos', 'Linfócitos'),
        ('monocitos', 'Monócitos'),
        ('eosinofilos', 'Eosinófilos'),
        ('basofilos', 'Basófilos'),
        ('plaquetas', 'Plaquetas'),
        ('vpm', 'VPM (Volume Plaquetário Médio)'),
        ('other', 'Outros')
    ], validators=[DataRequired()])
    reference_values = TextAreaField('Valores de Referência', validators=[Optional()])
    unit = StringField('Unidade', validators=[Optional(), Length(max=20)])
    description = TextAreaField('Descrição', validators=[Optional()])
    observations = TextAreaField('Observações Clínicas', validators=[Optional()])
    clinical_significance = TextAreaField('Significado Clínico', validators=[Optional()])
    is_active = BooleanField('Ativo', default=True)

class PrescriptionForm(FlaskForm):
    patient_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    custom_formulas = TextAreaField('Fórmulas Manipuladas', validators=[Optional()])
    additional_instructions = TextAreaField('Instruções Adicionais', validators=[Optional()])
    observations = TextAreaField('Observações', validators=[Optional()])

class PaymentForm(FlaskForm):
    patient_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    appointment_id = SelectField('Consulta', coerce=int, validators=[Optional()])
    amount = FloatField('Valor', validators=[DataRequired()])
    payment_method = SelectField('Forma de Pagamento', choices=[
        ('cash', 'Dinheiro'),
        ('card', 'Cartão'),
        ('pix', 'PIX'),
        ('transfer', 'Transferência')
    ], validators=[DataRequired()])
    description = StringField('Descrição', validators=[Optional(), Length(max=200)])
