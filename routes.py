from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import *
from forms import *
import json
import requests
import os
from datetime import datetime, timedelta
from utils import generate_prescription_pdf, generate_receipt_pdf, send_appointment_confirmation
import uuid

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'admin':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            role=form.role.data,
            crm=form.crm.data,
            specialty=form.specialty.data,
            password_hash=generate_password_hash(form.password.data or 'temp123')
        )
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html', form=form)

# Dashboard and main routes
@app.route('/')
@login_required
def dashboard():
    # Get statistics for dashboard
    today = datetime.now().date()
    stats = {
        'total_patients': Patient.query.count(),
        'appointments_today': Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today
        ).count(),
        'pending_appointments': Appointment.query.filter_by(status='scheduled').count(),
        'total_revenue_month': db.session.query(db.func.sum(Payment.amount)).filter(
            db.func.extract('month', Payment.payment_date) == datetime.now().month,
            db.func.extract('year', Payment.payment_date) == datetime.now().year
        ).scalar() or 0
    }
    
    # Recent appointments
    recent_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now()
    ).order_by(Appointment.appointment_date).limit(5).all()
    
    return render_template('index.html', stats=stats, recent_appointments=recent_appointments)

# Patient management routes
@app.route('/patients')
@login_required
def patients_list():
    search = request.args.get('search', '')
    query = Patient.query
    if search:
        query = query.filter(Patient.name.contains(search) | Patient.cpf.contains(search))
    patients = query.order_by(Patient.name).all()
    return render_template('patients/list.html', patients=patients, search=search)

@app.route('/patients/new', methods=['GET', 'POST'])
@login_required
def patient_new():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            name=form.name.data,
            cpf=form.cpf.data,
            birth_date=form.birth_date.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            medical_history=form.medical_history.data,
            allergies=form.allergies.data,
            current_medications=form.current_medications.data,
            emergency_contact=form.emergency_contact.data,
            emergency_phone=form.emergency_phone.data
        )
        db.session.add(patient)
        db.session.commit()
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('patients_list'))
    return render_template('patients/form.html', form=form, title='Novo Paciente')

@app.route('/patients/<int:id>')
@login_required
def patient_view(id):
    patient = Patient.query.get_or_404(id)
    appointments = Appointment.query.filter_by(patient_id=id).order_by(Appointment.appointment_date.desc()).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=id).order_by(MedicalRecord.date.desc()).all()
    return render_template('patients/view.html', patient=patient, appointments=appointments, medical_records=medical_records)

@app.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def patient_edit(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        form.populate_obj(patient)
        db.session.commit()
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('patient_view', id=id))
    return render_template('patients/form.html', form=form, title='Editar Paciente')

# Appointment management routes
@app.route('/appointments')
@login_required
def appointments_list():
    date_filter = request.args.get('date')
    query = Appointment.query
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter(db.func.date(Appointment.appointment_date) == filter_date)
    appointments = query.order_by(Appointment.appointment_date).all()
    return render_template('appointments/list.html', appointments=appointments, date_filter=date_filter)

@app.route('/appointments/calendar')
@login_required
def appointments_calendar():
    return render_template('appointments/calendar.html')

@app.route('/appointments/api')
@login_required
def appointments_api():
    appointments = Appointment.query.all()
    events = []
    for apt in appointments:
        events.append({
            'id': apt.id,
            'title': f'{apt.patient.name} - Dr. {apt.doctor.name}',
            'start': apt.appointment_date.isoformat(),
            'end': (apt.appointment_date + timedelta(minutes=apt.duration)).isoformat(),
            'backgroundColor': '#007bff' if apt.status == 'scheduled' else '#28a745'
        })
    return jsonify(events)

@app.route('/appointments/new', methods=['GET', 'POST'])
@login_required
def appointment_new():
    form = AppointmentForm()
    form.patient_id.choices = [(p.id, p.name) for p in Patient.query.order_by(Patient.name).all()]
    form.doctor_id.choices = [(u.id, u.name) for u in User.query.filter_by(role='doctor').order_by(User.name).all()]
    
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            duration=form.duration.data,
            notes=form.notes.data
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Send confirmation via API
        patient = Patient.query.get(form.patient_id.data)
        send_appointment_confirmation(patient, appointment)
        
        flash('Consulta agendada com sucesso!', 'success')
        return redirect(url_for('appointments_list'))
    return render_template('appointments/form.html', form=form, title='Nova Consulta')

# Medical records routes
@app.route('/medical-records')
@login_required
def medical_records_list():
    if current_user.role == 'doctor':
        records = MedicalRecord.query.filter_by(doctor_id=current_user.id).order_by(MedicalRecord.date.desc()).all()
    else:
        records = MedicalRecord.query.order_by(MedicalRecord.date.desc()).all()
    return render_template('medical_records/list.html', records=records)

@app.route('/medical-records/new/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def medical_record_new(patient_id):
    if current_user.role not in ['doctor', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    form = MedicalRecordForm()
    
    if form.validate_on_submit():
        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=current_user.id,
            chief_complaint=form.chief_complaint.data,
            anamnesis=form.anamnesis.data,
            symptoms=form.symptoms.data,
            physical_exam=form.physical_exam.data,
            diagnosis=form.diagnosis.data,
            treatment_plan=form.treatment_plan.data,
            observations=form.observations.data
        )
        db.session.add(record)
        db.session.commit()
        flash('Prontuário criado com sucesso!', 'success')
        return redirect(url_for('patient_view', id=patient_id))
    
    return render_template('medical_records/form.html', form=form, patient=patient, title='Novo Prontuário')

@app.route('/medical-records/<int:id>')
@login_required
def medical_record_view(id):
    record = MedicalRecord.query.get_or_404(id)
    return render_template('medical_records/view.html', record=record)

# Prescription routes
@app.route('/prescriptions')
@login_required
def prescriptions_list():
    if current_user.role == 'doctor':
        prescriptions = Prescription.query.filter_by(doctor_id=current_user.id).order_by(Prescription.date.desc()).all()
    else:
        prescriptions = Prescription.query.order_by(Prescription.date.desc()).all()
    return render_template('prescriptions/list.html', prescriptions=prescriptions)

@app.route('/prescriptions/new/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def prescription_new(patient_id):
    if current_user.role not in ['doctor', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    form = PrescriptionForm()
    
    # Populate choices for SelectField
    form.patient_id.choices = [(patient.id, patient.name)]
    form.patient_id.data = patient_id
    
    supplements = Supplement.query.filter_by(is_active=True).all()
    lab_tests = LabTest.query.filter_by(is_active=True).all()
    
    if form.validate_on_submit():
        # Get selected supplements and lab tests from form
        selected_supplements = request.form.getlist('supplements')
        selected_lab_tests = request.form.getlist('lab_tests')
        
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=current_user.id,
            custom_formulas=form.custom_formulas.data,
            supplements_prescribed=json.dumps(selected_supplements),
            lab_tests_requested=json.dumps(selected_lab_tests),
            additional_instructions=form.additional_instructions.data,
            observations=form.observations.data
        )
        db.session.add(prescription)
        db.session.commit()
        flash('Prescrição criada com sucesso!', 'success')
        return redirect(url_for('prescription_view', id=prescription.id))
    
    return render_template('prescriptions/form.html', form=form, patient=patient, 
                         supplements=supplements, lab_tests=lab_tests, title='Nova Prescrição')

@app.route('/prescriptions/<int:id>')
@login_required
def prescription_view(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescriptions/view.html', prescription=prescription)

@app.route('/prescriptions/<int:id>/pdf')
@login_required
def prescription_pdf(id):
    prescription = Prescription.query.get_or_404(id)
    pdf_content = generate_prescription_pdf(prescription)
    
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=prescription_{id}.pdf'
    return response

# Supplement management routes
@app.route('/supplements')
@login_required
def supplements_list():
    supplements = Supplement.query.filter_by(is_active=True).order_by(Supplement.name).all()
    return render_template('supplements/list.html', supplements=supplements)

@app.route('/supplements/new', methods=['GET', 'POST'])
@login_required
def supplement_new():
    if current_user.role not in ['doctor', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    form = SupplementForm()
    if form.validate_on_submit():
        supplement = Supplement(
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            dosage_info=form.dosage_info.data,
            observations=form.observations.data,
            is_active=form.is_active.data
        )
        db.session.add(supplement)
        db.session.commit()
        flash('Suplemento cadastrado com sucesso!', 'success')
        return redirect(url_for('supplements_list'))
    return render_template('supplements/form.html', form=form, title='Novo Suplemento')

@app.route('/supplements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def supplement_edit(id):
    if current_user.role not in ['doctor', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    supplement = Supplement.query.get_or_404(id)
    form = SupplementForm(obj=supplement)
    if form.validate_on_submit():
        form.populate_obj(supplement)
        db.session.commit()
        flash('Suplemento atualizado com sucesso!', 'success')
        return redirect(url_for('supplements_list'))
    return render_template('supplements/form.html', form=form, title='Editar Suplemento')

# Lab test management routes
@app.route('/lab-tests')
@login_required
def lab_tests_list():
    lab_tests = LabTest.query.filter_by(is_active=True).order_by(LabTest.name).all()
    return render_template('lab_tests/list.html', lab_tests=lab_tests)

@app.route('/lab-tests/new', methods=['GET', 'POST'])
@login_required
def lab_test_new():
    if current_user.role not in ['doctor', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    form = LabTestForm()
    if form.validate_on_submit():
        lab_test = LabTest(
            name=form.name.data,
            category=form.category.data,
            reference_values=form.reference_values.data,
            unit=form.unit.data,
            description=form.description.data,
            observations=form.observations.data,
            is_active=form.is_active.data
        )
        db.session.add(lab_test)
        db.session.commit()
        flash('Exame cadastrado com sucesso!', 'success')
        return redirect(url_for('lab_tests_list'))
    return render_template('lab_tests/form.html', form=form, title='Novo Exame')

# Hemogram Management
@app.route('/hemograms')
@login_required
def hemograms_list():
    hemograms = Hemogram.query.filter_by(is_active=True).all()
    return render_template('hemograms/list.html', hemograms=hemograms)

@app.route('/hemograms/new', methods=['GET', 'POST'])
@login_required
def hemogram_new():
    if current_user.role not in ['admin', 'doctor']:
        flash('Acesso negado. Apenas administradores e médicos podem cadastrar hemogramas.', 'error')
        return redirect(url_for('dashboard'))
    
    form = HemogramForm()
    if form.validate_on_submit():
        hemogram = Hemogram(
            name=form.name.data,
            parameter_type=form.parameter_type.data,
            reference_values=form.reference_values.data,
            unit=form.unit.data,
            description=form.description.data,
            observations=form.observations.data,
            clinical_significance=form.clinical_significance.data,
            is_active=form.is_active.data
        )
        db.session.add(hemogram)
        db.session.commit()
        flash('Parâmetro de hemograma cadastrado com sucesso!', 'success')
        return redirect(url_for('hemograms_list'))
    
    return render_template('hemograms/form.html', form=form, title='Novo Parâmetro de Hemograma')

@app.route('/hemograms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def hemogram_edit(id):
    if current_user.role not in ['admin', 'doctor']:
        flash('Acesso negado. Apenas administradores e médicos podem editar hemogramas.', 'error')
        return redirect(url_for('dashboard'))
    
    hemogram = Hemogram.query.get_or_404(id)
    form = HemogramForm(obj=hemogram)
    
    if form.validate_on_submit():
        form.populate_obj(hemogram)
        db.session.commit()
        flash('Parâmetro de hemograma atualizado com sucesso!', 'success')
        return redirect(url_for('hemograms_list'))
    
    return render_template('hemograms/form.html', form=form, title='Editar Parâmetro de Hemograma')

# Financial routes
@app.route('/financial')
@login_required
def financial_dashboard():
    if current_user.role not in ['financial', 'admin']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    # Financial statistics
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    stats = {
        'total_today': db.session.query(db.func.sum(Payment.amount)).filter(
            db.func.date(Payment.payment_date) == today.date()
        ).scalar() or 0,
        'total_month': db.session.query(db.func.sum(Payment.amount)).filter(
            db.func.extract('month', Payment.payment_date) == current_month,
            db.func.extract('year', Payment.payment_date) == current_year
        ).scalar() or 0,
        'total_year': db.session.query(db.func.sum(Payment.amount)).filter(
            db.func.extract('year', Payment.payment_date) == current_year
        ).scalar() or 0,
        'pending_count': Appointment.query.filter_by(status='scheduled').count()
    }
    
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(10).all()
    
    return render_template('financial/dashboard.html', stats=stats, recent_payments=recent_payments)

@app.route('/financial/payment/new', methods=['GET', 'POST'])
@login_required
def payment_new():
    if current_user.role not in ['financial', 'admin', 'receptionist']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    form = PaymentForm()
    form.patient_id.choices = [(p.id, p.name) for p in Patient.query.order_by(Patient.name).all()]
    form.appointment_id.choices = [(0, 'Nenhuma')] + [(a.id, f'{a.patient.name} - {a.appointment_date.strftime("%d/%m/%Y %H:%M")}') 
                                                      for a in Appointment.query.order_by(Appointment.appointment_date.desc()).all()]
    
    if form.validate_on_submit():
        receipt_number = f"REC{datetime.now().strftime('%Y%m%d')}{Payment.query.count() + 1:04d}"
        
        payment = Payment(
            patient_id=form.patient_id.data,
            appointment_id=form.appointment_id.data if form.appointment_id.data != 0 else None,
            doctor_id=current_user.id if current_user.role == 'doctor' else None,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            description=form.description.data,
            receipt_number=receipt_number
        )
        db.session.add(payment)
        db.session.commit()
        flash('Pagamento registrado com sucesso!', 'success')
        return redirect(url_for('financial_dashboard'))
    
    return render_template('financial/payment_form.html', form=form)

@app.route('/financial/receipt/<int:id>/pdf')
@login_required
def receipt_pdf(id):
    payment = Payment.query.get_or_404(id)
    pdf_content = generate_receipt_pdf(payment)
    
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=receipt_{payment.receipt_number}.pdf'
    return response

# Chatbot routes
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot/chat.html')

@app.route('/chatbot/send', methods=['POST'])
def chatbot_send():
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Save user message
    conversation = ChatConversation(
        session_id=session_id,
        message=message,
        user_type='patient'
    )
    db.session.add(conversation)
    
    # Generate AI response using OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Get conversation history for context
        recent_conversations = ChatConversation.query.filter_by(
            session_id=session_id
        ).order_by(ChatConversation.timestamp.desc()).limit(10).all()
        
        messages = [
            {
                'role': 'system',
                'content': '''Você é um assistente virtual inteligente da Clínica Ortomolecular. 
                
Suas responsabilidades:
- Responder perguntas sobre medicina ortomolecular, suplementos e saúde
- Fornecer informações sobre horários, agendamentos e serviços da clínica
- Orientar sobre tratamentos ortomoleculares de forma educativa
- Ser empático, profissional e prestativo

Informações da clínica:
- Horário: Segunda a sexta 8h-18h, sábados 8h-12h
- Telefone: (11) 3456-7890
- WhatsApp: (11) 99999-9999
- Email: contato@clinicaortomolecular.com.br
- Especialidade: Medicina Ortomolecular, Nutrologia

IMPORTANTE: Sempre recomende consulta médica para diagnósticos específicos. Não substitua orientação médica profissional.'''
            }
        ]
        
        # Add recent conversation history
        for conv in reversed(recent_conversations[-5:]):  # Last 5 exchanges
            if conv.message:
                messages.append({'role': 'user', 'content': conv.message})
            if conv.response:
                messages.append({'role': 'assistant', 'content': conv.response})
        
        # Add current message
        messages.append({'role': 'user', 'content': message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the latest model
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to predefined responses
        response_text = get_fallback_response(message)
    
    # Save AI response
    conversation.response = response_text
    db.session.commit()
    
    return jsonify({
        'response': response_text,
        'session_id': session_id
    })

def get_fallback_response(message):
    """Fallback responses when AI is unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['horário', 'horario', 'atendimento', 'funciona']):
        return "Nossa clínica funciona de segunda a sexta das 8h às 18h, e sábados das 8h às 12h. Para agendamentos, ligue (11) 3456-7890 ou WhatsApp (11) 99999-9999."
    
    elif any(word in message_lower for word in ['agendar', 'consulta', 'marcar']):
        return "Para agendar sua consulta, você pode ligar para (11) 3456-7890, enviar WhatsApp para (11) 99999-9999 ou usar nosso sistema online."
    
    elif any(word in message_lower for word in ['ortomolecular', 'medicina']):
        return "A medicina ortomolecular busca o equilíbrio do organismo através da correção de deficiências nutricionais com vitaminas, minerais e aminoácidos. Nossa equipe está preparada para orientá-lo."
    
    elif any(word in message_lower for word in ['contato', 'telefone', 'whatsapp']):
        return "Você pode nos contatar pelos seguintes canais:\n📞 Telefone: (11) 3456-7890\n📱 WhatsApp: (11) 99999-9999\n📧 Email: contato@clinicaortomolecular.com.br"
    
    else:
        return "Obrigado por entrar em contato! Sou o assistente virtual da Clínica Ortomolecular. Posso ajudá-lo com informações sobre nossos tratamentos, horários e agendamentos. Em que posso ajudá-lo?"

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
