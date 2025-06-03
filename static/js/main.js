// Main JavaScript functionality for Orthomolecular Clinic System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // CPF formatting
    const cpfInputs = document.querySelectorAll('input[name="cpf"]');
    cpfInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            e.target.value = value;
        });
    });

    // Phone formatting
    const phoneInputs = document.querySelectorAll('input[name="phone"], input[name="emergency_phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 10) {
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{4})(\d)/, '$1-$2');
            } else {
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
            }
            e.target.value = value;
        });
    });

    // Money formatting
    const moneyInputs = document.querySelectorAll('input[name="amount"]');
    moneyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = (value / 100).toFixed(2);
            value = value.replace('.', ',');
            value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
            e.target.value = value;
        });
    });

    // Search functionality with debounce
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function(e) {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                if (e.target.value.length >= 3 || e.target.value.length === 0) {
                    // Auto-submit search form after 500ms delay
                    const form = e.target.closest('form');
                    if (form) {
                        form.submit();
                    }
                }
            }, 500);
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-danger[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Patient quick search in forms
    const patientSelects = document.querySelectorAll('select[name="patient_id"]');
    patientSelects.forEach(function(select) {
        // Add search functionality to patient selects
        select.addEventListener('change', function() {
            const patientId = this.value;
            if (patientId) {
                // Load patient info if available
                loadPatientInfo(patientId);
            }
        });
    });

    // Date picker enhancements
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Set min date to today for future appointments
        if (input.name === 'appointment_date') {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
    });

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Load states and cities for address
    const stateSelects = document.querySelectorAll('select[name="state"]');
    stateSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const state = this.value;
            const citySelect = document.querySelector('select[name="city"]');
            if (citySelect && state) {
                loadCities(state, citySelect);
            }
        });
    });

    // Dynamic form sections
    const roleSelect = document.querySelector('select[name="role"]');
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const doctorFields = document.getElementById('doctor-fields');
            if (doctorFields) {
                if (this.value === 'doctor') {
                    doctorFields.style.display = 'block';
                } else {
                    doctorFields.style.display = 'none';
                }
            }
        });
        
        // Trigger change on load
        roleSelect.dispatchEvent(new Event('change'));
    }

    // Data tables initialization
    const tables = document.querySelectorAll('.table');
    tables.forEach(function(table) {
        // Add sorting functionality
        const headers = table.querySelectorAll('th');
        headers.forEach(function(header, index) {
            if (!header.querySelector('.no-sort')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    sortTable(table, index);
                });
            }
        });
    });

    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Processando...';
            }
        });
    });
});

// Helper functions
function loadPatientInfo(patientId) {
    // In a real application, this would make an AJAX call to get patient info
    console.log('Loading patient info for ID:', patientId);
}

function loadCities(state, citySelect) {
    // In a real application, this would load cities based on state
    citySelect.innerHTML = '<option value="">Carregando cidades...</option>';
    
    // Simulate loading
    setTimeout(function() {
        citySelect.innerHTML = '<option value="">Selecione uma cidade</option>';
    }, 1000);
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = table.dataset.sortDirection !== 'asc';
    table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
    
    rows.sort(function(a, b) {
        const aText = a.children[column].textContent.trim();
        const bText = b.children[column].textContent.trim();
        
        // Try to parse as numbers first
        const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Parse as dates
        const aDate = Date.parse(aText);
        const bDate = Date.parse(bText);
        
        if (!isNaN(aDate) && !isNaN(bDate)) {
            return isAscending ? aDate - bDate : bDate - aDate;
        }
        
        // Default to string comparison
        return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Clear tbody and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    // Update sort indicators
    const headers = table.querySelectorAll('th');
    headers.forEach(function(header, index) {
        header.classList.remove('sort-asc', 'sort-desc');
        if (index === column) {
            header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        }
    });
}

function initializeCharts() {
    // Initialize any charts on the dashboard
    const chartElements = document.querySelectorAll('.chart-container');
    chartElements.forEach(function(element) {
        if (element.id === 'revenueChart') {
            initializeRevenueChart(element);
        } else if (element.id === 'appointmentsChart') {
            initializeAppointmentsChart(element);
        }
    });
}

function initializeRevenueChart(element) {
    const ctx = element.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Receita Mensal',
                data: [12000, 15000, 18000, 16000, 20000, 22000],
                borderColor: 'rgb(0, 123, 255)',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

function initializeAppointmentsChart(element) {
    const ctx = element.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Agendadas', 'Confirmadas', 'Concluídas', 'Canceladas'],
            datasets: [{
                data: [30, 45, 80, 5],
                backgroundColor: [
                    '#ffc107',
                    '#17a2b8',
                    '#28a745',
                    '#dc3545'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Export functions for use in other modules
window.ClinicUtils = {
    formatCurrency,
    formatDate,
    formatDateTime,
    showNotification,
    loadPatientInfo,
    sortTable
};
