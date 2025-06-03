// Chatbot functionality for patient assistance

class ChatBot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.messageContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSubmit(e);
                }
            });
            
            // Focus on input
            this.messageInput.focus();
        }
        
        // Show welcome message after a short delay
        setTimeout(() => {
            this.addBotMessage("Olá! Sou o assistente virtual da Clínica Ortomolecular. Como posso ajudá-lo hoje?");
        }, 1000);
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTyping();
        
        try {
            // Send message to backend
            const response = await this.sendMessage(message);
            
            // Hide typing indicator
            this.hideTyping();
            
            // Add bot response
            this.addBotMessage(response.response);
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addBotMessage("Desculpe, estou com dificuldades técnicas no momento. Tente novamente em alguns instantes ou entre em contato diretamente com nossa equipe.");
        }
    }
    
    async sendMessage(message) {
        const response = await fetch('/chatbot/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        return await response.json();
    }
    
    addUserMessage(message) {
        const messageEl = this.createMessageElement('user', message);
        this.appendMessage(messageEl);
    }
    
    addBotMessage(message) {
        const messageEl = this.createMessageElement('bot', message);
        this.appendMessage(messageEl);
    }
    
    createMessageElement(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${type}-avatar`;
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        if (type === 'user') {
            messageDiv.appendChild(messageContent);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
        }
        
        return messageDiv;
    }
    
    formatMessage(message) {
        // Convert line breaks to <br> tags
        message = message.replace(/\n/g, '<br>');
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        message = message.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert email addresses to mailto links
        const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;
        message = message.replace(emailRegex, '<a href="mailto:$1">$1</a>');
        
        // Convert phone numbers to tel links
        const phoneRegex = /(\(\d{2}\)\s\d{4,5}-\d{4})/g;
        message = message.replace(phoneRegex, '<a href="tel:$1">$1</a>');
        
        return message;
    }
    
    appendMessage(messageEl) {
        // Remove welcome message if it exists
        const welcomeMessage = this.messageContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Insert before typing indicator
        this.messageContainer.insertBefore(messageEl, this.typingIndicator.parentElement);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    showTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.typingIndicator.style.display = 'block';
            this.scrollToBottom();
        }
    }
    
    hideTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.typingIndicator.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
        }, 100);
    }
    
    clearChat() {
        const messages = this.messageContainer.querySelectorAll('.message');
        messages.forEach(message => message.remove());
        
        // Reset session
        this.sessionId = this.generateSessionId();
        
        // Show welcome message again
        setTimeout(() => {
            this.addBotMessage("Chat limpo! Como posso ajudá-lo agora?");
        }, 500);
    }
}

// Quick message functionality
function sendQuickMessage(message) {
    if (window.chatBot) {
        window.chatBot.messageInput.value = message;
        window.chatBot.handleSubmit(new Event('submit'));
    }
}

// Predefined responses for common questions
const predefinedResponses = {
    'horarios': 'Nossa clínica funciona de segunda a sexta, das 8h às 18h. Sábados atendemos das 8h às 12h mediante agendamento. Para verificar disponibilidade específica, por favor ligue para (11) 3456-7890.',
    
    'ortomolecular': 'A medicina ortomolecular é uma abordagem terapêutica que busca o equilíbrio do organismo através da correção de deficiências nutricionais e uso de substâncias naturais como vitaminas, minerais e aminoácidos.',
    
    'tratamento': 'Nosso tratamento é personalizado e inclui: avaliação clínica completa, exames laboratoriais específicos, prescrição de suplementos ortomoleculares e acompanhamento médico regular.',
    
    'valores': 'Os valores das consultas variam conforme o tipo de atendimento. Para informações detalhadas sobre valores, entre em contato pelo telefone (11) 3456-7890 ou WhatsApp (11) 99999-9999.',
    
    'agendamento': 'Para agendar sua consulta, você pode ligar para (11) 3456-7890, enviar WhatsApp para (11) 99999-9999 ou usar nosso sistema online.',
    
    'exames': 'Solicitamos exames específicos conforme cada caso, incluindo hemograma, vitaminas, minerais, hormônios e marcadores metabólicos. Os exames podem ser realizados em laboratórios conveniados.',
    
    'contato': 'Você pode entrar em contato conosco pelos seguintes canais:\n📞 Telefone: (11) 3456-7890\n📱 WhatsApp: (11) 99999-9999\n📧 Email: contato@clinicaortomolecular.com.br'
};

// Simple keyword matching for offline responses
function getOfflineResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('horário') || lowerMessage.includes('funciona') || lowerMessage.includes('atendimento')) {
        return predefinedResponses.horarios;
    }
    
    if (lowerMessage.includes('ortomolecular') || lowerMessage.includes('medicina')) {
        return predefinedResponses.ortomolecular;
    }
    
    if (lowerMessage.includes('tratamento') || lowerMessage.includes('consulta')) {
        return predefinedResponses.tratamento;
    }
    
    if (lowerMessage.includes('valor') || lowerMessage.includes('preço') || lowerMessage.includes('custo')) {
        return predefinedResponses.valores;
    }
    
    if (lowerMessage.includes('agendar') || lowerMessage.includes('marcar')) {
        return predefinedResponses.agendamento;
    }
    
    if (lowerMessage.includes('exame') || lowerMessage.includes('laboratorio')) {
        return predefinedResponses.exames;
    }
    
    if (lowerMessage.includes('contato') || lowerMessage.includes('telefone') || lowerMessage.includes('whatsapp')) {
        return predefinedResponses.contato;
    }
    
    // Default response
    return "Obrigado pela sua mensagem! Para informações mais específicas, nossa equipe está disponível pelo telefone (11) 3456-7890 ou WhatsApp (11) 99999-9999. Em que mais posso ajudá-lo?";
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatBot = new ChatBot();
});

// Export for global access
window.sendQuickMessage = sendQuickMessage;
