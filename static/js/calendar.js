// Calendar functionality for appointment management

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'pt-br',
            height: 'auto',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            buttonText: {
                today: 'Hoje',
                month: 'Mês',
                week: 'Semana',
                day: 'Dia'
            },
            slotLabelFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            },
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            },
            businessHours: {
                daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
                startTime: '08:00',
                endTime: '18:00'
            },
            slotMinTime: '07:00',
            slotMaxTime: '19:00',
            allDaySlot: false,
            weekends: true,
            nowIndicator: true,
            selectable: true,
            selectMirror: true,
            editable: false, // Disable drag & drop for now
            eventResizableFromStart: false,
            eventDurationEditable: false,
            
            // Event sources
            events: {
                url: '/appointments/api',
                method: 'GET',
                failure: function() {
                    alert('Erro ao carregar eventos da agenda.');
                }
            },
            
            // Event handlers
            select: function(info) {
                // Handle date/time selection for new appointments
                const now = new Date();
                const selectedDate = new Date(info.start);
                
                if (selectedDate < now) {
                    alert('Não é possível agendar consultas em datas passadas.');
                    calendar.unselect();
                    return;
                }
                
                // Check if it's outside business hours
                const hour = selectedDate.getHours();
                const day = selectedDate.getDay();
                
                if (day === 0 || day === 6) { // Weekend
                    if (!confirm('Deseja agendar uma consulta no fim de semana?')) {
                        calendar.unselect();
                        return;
                    }
                }
                
                if (hour < 8 || hour >= 18) {
                    if (!confirm('Deseja agendar uma consulta fora do horário comercial?')) {
                        calendar.unselect();
                        return;
                    }
                }
                
                // Format date for the form
                const dateStr = selectedDate.toISOString().slice(0, 16);
                
                // Redirect to new appointment form with pre-filled date
                window.location.href = `/appointments/new?date=${dateStr}`;
            },
            
            eventClick: function(info) {
                // Handle event click - show appointment details
                const event = info.event;
                showAppointmentDetails(event);
            },
            
            eventMouseEnter: function(info) {
                // Show tooltip on hover
                const event = info.event;
                const tooltip = createTooltip(event);
                
                info.el.setAttribute('title', tooltip);
                info.el.style.cursor = 'pointer';
            },
            
            loading: function(bool) {
                // Show/hide loading indicator
                const loadingEl = document.getElementById('calendar-loading');
                if (loadingEl) {
                    loadingEl.style.display = bool ? 'block' : 'none';
                }
            },
            
            eventDidMount: function(info) {
                // Customize event appearance based on status
                const event = info.event;
                const status = event.extendedProps.status;
                
                switch(status) {
            case 'scheduled':
                info.el.style.backgroundColor = '#ffc107';
                info.el.style.borderColor = '#ffc107';
                if (info.view.type === 'dayGridMonth') {
                    info.el.style.color = '#ffffff';  // White text color for Month view
                } else {
                    info.el.style.color = '#000000 !important';  // Black text color for other views
                }
                info.el.style.fontWeight = 'bold'; // Make text bold for better visibility
                break;
            case 'confirmed':
                info.el.style.backgroundColor = '#17a2b8';
                info.el.style.borderColor = '#17a2b8';
                info.el.style.color = '#ffffff';  // Change text color to white for confirmed
                break;
            case 'completed':
                info.el.style.backgroundColor = '#28a745';
                info.el.style.borderColor = '#28a745';
                break;
            case 'cancelled':
                info.el.style.backgroundColor = '#dc3545';
                info.el.style.borderColor = '#dc3545';
                }
            }
        });
        
        calendar.render();
        
        // Refresh calendar every 5 minutes
        setInterval(function() {
            calendar.refetchEvents();
        }, 300000);
    }
});

function createTooltip(event) {
    const start = event.start;
    const end = event.end;
    const duration = end ? Math.round((end - start) / (1000 * 60)) : 60;
    
    return `
        ${event.title}
        Horário: ${formatTime(start)} - ${formatTime(end || new Date(start.getTime() + duration * 60000))}
        Duração: ${duration} minutos
        Status: ${getStatusText(event.extendedProps.status)}
    `.trim();
}

function formatTime(date) {
    return date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusText(status) {
    const statusMap = {
        'scheduled': 'Agendada',
        'confirmed': 'Confirmada',
        'completed': 'Concluída',
        'cancelled': 'Cancelada'
    };
    return statusMap[status] || status;
}

function showAppointmentDetails(event) {
    const appointmentId = event.id;
    const patientName = event.title.split(' - ')[0];
    const doctorName = event.title.split(' - ')[1];
    
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'appointmentModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detalhes da Consulta</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-primary">Paciente</h6>
                            <p>${patientName}</p>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-primary">Médico</h6>
                            <p>${doctorName}</p>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-primary">Data/Hora</h6>
                            <p>${formatDateTime(event.start)}</p>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-primary">Status</h6>
                            <p><span class="badge bg-info">${getStatusText(event.extendedProps.status)}</span></p>
                        </div>
                    </div>
                    ${event.extendedProps.notes ? `
                    <div class="row">
                        <div class="col-12">
                            <h6 class="text-primary">Observações</h6>
                            <p>${event.extendedProps.notes}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    <a href="/patients/${event.extendedProps.patientId}" class="btn btn-info">Ver Paciente</a>
                    ${event.extendedProps.status === 'scheduled' ? `
                    <button type="button" class="btn btn-success" onclick="confirmAppointment(${appointmentId})">Confirmar</button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

function formatDateTime(date) {
    return date.toLocaleString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function confirmAppointment(appointmentId) {
    console.log('confirmAppointment called with id:', appointmentId);
    if (confirm('Deseja confirmar esta consulta?')) {
        fetch(`/appointments/${appointmentId}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ status: 'confirmed' })
        })
        .then(response => {
            console.log('Fetch response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Fetch response data:', data);
            if (data.success) {
                // Refresh the calendar
                const calendarEl = document.getElementById('calendar');
                if (calendarEl) {
                    const calendar = FullCalendar.getApi();
                    calendar.refetchEvents();
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('appointmentModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Show success message
                showNotification('Consulta confirmada com sucesso!', 'success');
                // Reload the page to update the appointments list
                window.location.reload();
            } else {
                alert('Erro ao confirmar consulta: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao confirmar consulta. Tente novamente.');
        });
    }
}

// Calendar view helpers
function goToToday() {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = FullCalendar.getApi();
        calendar.today();
    }
}

function changeView(viewName) {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = FullCalendar.getApi();
        calendar.changeView(viewName);
    }
}

function filterByDoctor(doctorId) {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = FullCalendar.getApi();
        
        if (doctorId) {
            calendar.setOption('events', {
                url: '/appointments/api',
                method: 'GET',
                extraParams: {
                    doctor_id: doctorId
                }
            });
        } else {
            calendar.setOption('events', {
                url: '/appointments/api',
                method: 'GET'
            });
        }
        
        calendar.refetchEvents();
    }
}

function filterByStatus(status) {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = FullCalendar.getApi();
        
        if (status) {
            calendar.setOption('events', {
                url: '/appointments/api',
                method: 'GET',
                extraParams: {
                    status: status
                }
            });
        } else {
            calendar.setOption('events', {
                url: '/appointments/api',
                method: 'GET'
            });
        }
        
        calendar.refetchEvents();
    }
}

// Export functions for global access
window.CalendarUtils = {
    goToToday,
    changeView,
    filterByDoctor,
    filterByStatus,
    confirmAppointment
};
