#!/usr/bin/env python3
"""
WhatsApp Chatbot for Clínica Ortomolecular
Uses OpenRouter API for intelligent responses
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WhatsAppBot:
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.database_url = os.environ.get('DATABASE_URL')
        
    def get_ai_response(self, message, phone_number):
        """Get AI response using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é o assistente virtual da Clínica Ortomolecular via WhatsApp.

Suas responsabilidades:
- Responder perguntas sobre medicina ortomolecular, suplementos e saúde
- Fornecer informações sobre horários, agendamentos e serviços
- Orientar sobre tratamentos ortomoleculares de forma educativa
- Ser empático, profissional e conciso (WhatsApp)

Informações da clínica:
- Horário: Segunda a sexta 8h-18h, sábados 8h-12h
- Telefone: (11) 3456-7890
- WhatsApp: (11) 99999-9999
- Email: contato@clinicaortomolecular.com.br
- Especialistas: Dr. João Silva (CRM-SP 123456), Dra. Maria Santos (CRM-SP 789012)

Tratamentos oferecidos:
- Medicina Ortomolecular
- Nutrologia
- Prescrição de suplementos personalizados
- Análise de exames laboratoriais específicos
- Acompanhamento nutricional

IMPORTANTE: 
- Respostas devem ser concisas para WhatsApp
- Sempre recomende consulta médica para diagnósticos
- Para agendamentos, direcione para o telefone da clínica
- Seja educativo sobre medicina ortomolecular"""
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=300  # Shorter responses for WhatsApp
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self.get_fallback_response(message)
    
    def get_fallback_response(self, message):
        """Fallback responses when AI is unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
            return """Olá! 👋 
Bem-vindo à Clínica Ortomolecular!

Sou seu assistente virtual. Posso ajudar com:
• Informações sobre tratamentos
• Horários de atendimento  
• Orientações sobre medicina ortomolecular

Como posso ajudá-lo hoje?"""

        elif any(word in message_lower for word in ['horário', 'horario', 'atendimento', 'funciona']):
            return """🕐 *Horários de Atendimento:*

Segunda a Sexta: 8h às 18h
Sábados: 8h às 12h

📞 Para agendamentos: (11) 3456-7890
💬 WhatsApp: (11) 99999-9999"""

        elif any(word in message_lower for word in ['agendar', 'consulta', 'marcar', 'agendamento']):
            return """📅 *Agendamento de Consultas:*

Para agendar sua consulta:
📞 Ligue: (11) 3456-7890  
💬 WhatsApp: (11) 99999-9999

⏰ Horários disponíveis:
• Segunda a sexta: 8h às 18h
• Sábados: 8h às 12h

Nossa equipe terá prazer em atendê-lo!"""

        elif any(word in message_lower for word in ['ortomolecular', 'medicina', 'tratamento']):
            return """🧬 *Medicina Ortomolecular:*

A medicina ortomolecular busca o equilíbrio do organismo através de:

✅ Correção de deficiências nutricionais
✅ Suplementação personalizada
✅ Vitaminas, minerais e aminoácidos
✅ Análise de exames específicos

👨‍⚕️ Nossos especialistas:
• Dr. João Silva - Medicina Ortomolecular
• Dra. Maria Santos - Nutrologia

Agende sua consulta: (11) 3456-7890"""

        elif any(word in message_lower for word in ['contato', 'telefone', 'email']):
            return """📞 *Nossos Contatos:*

🏥 Clínica Ortomolecular
📞 Telefone: (11) 3456-7890
💬 WhatsApp: (11) 99999-9999  
📧 Email: contato@clinicaortomolecular.com.br

⏰ Atendimento:
Segunda a sexta: 8h-18h
Sábados: 8h-12h"""

        elif any(word in message_lower for word in ['preço', 'valor', 'custo', 'quanto custa']):
            return """💰 *Valores de Consultas:*

Os valores variam conforme o tipo de atendimento e tratamento.

📞 Para informações detalhadas sobre valores:
Ligue: (11) 3456-7890
💬 WhatsApp: (11) 99999-9999

Nossa equipe fornecerá todas as informações sobre investimento em sua saúde! 🌟"""

        elif any(word in message_lower for word in ['exame', 'laboratorio', 'análise']):
            return """🔬 *Exames Laboratoriais:*

Solicitamos exames específicos conforme cada caso:

🩸 Exames de sangue completos
🧪 Vitaminas e minerais  
🧬 Marcadores metabólicos
⚖️ Perfil hormonal
🛡️ Sistema imunológico

Os exames podem ser realizados em laboratórios conveniados.

Agende sua consulta: (11) 3456-7890"""

        else:
            return """Obrigado por entrar em contato! 🙏

Sou o assistente virtual da Clínica Ortomolecular. 

Posso ajudar com:
• Informações sobre tratamentos
• Horários e agendamentos  
• Dúvidas sobre medicina ortomolecular
• Contatos da clínica

Digite sua dúvida que terei prazer em ajudar! 😊"""

    def save_conversation(self, phone_number, message, response):
        """Save conversation to database"""
        try:
            # Here you would save to your database
            # For now, we'll log it
            logger.info(f"Conversation saved - Phone: {phone_number}, Message: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")

# Initialize bot
bot = WhatsAppBot()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp"""
    verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'clinic_verify_token')
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            logger.info("Webhook verified successfully!")
            return challenge
        else:
            logger.warning("Webhook verification failed!")
            return 'Verification failed', 403
    
    return 'Invalid request', 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
        # Extract message data (format depends on WhatsApp API provider)
        if 'messages' in data and data['messages']:
            for message_data in data['messages']:
                phone_number = message_data.get('from', '')
                message_text = message_data.get('text', {}).get('body', '')
                message_id = message_data.get('id', '')
                
                if message_text and phone_number:
                    # Get AI response
                    response = bot.get_ai_response(message_text, phone_number)
                    
                    # Save conversation
                    bot.save_conversation(phone_number, message_text, response)
                    
                    # Send response back
                    send_whatsapp_message(phone_number, response)
                    
                    logger.info(f"Processed message from {phone_number}: {message_text[:50]}...")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_whatsapp_message(phone_number, message):
    """Send message via WhatsApp API"""
    try:
        # This would integrate with your WhatsApp API provider
        # (Twilio, Meta Business API, etc.)
        
        # Example for generic WhatsApp API:
        api_url = os.environ.get('WHATSAPP_API_URL', 'http://localhost:8001/api/send')
        
        payload = {
            'phone': phone_number,
            'message': message,
            'type': 'text'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {os.environ.get('WHATSAPP_API_TOKEN', '')}"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.ok:
            logger.info(f"Message sent successfully to {phone_number}")
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")

@app.route('/send', methods=['POST'])
def send_message():
    """Manual endpoint to send messages"""
    try:
        data = request.get_json()
        phone_number = data.get('phone')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'error': 'Phone number and message required'}), 400
        
        send_whatsapp_message(phone_number, message)
        return jsonify({'status': 'success', 'message': 'Message sent'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Direct chat endpoint for testing"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        phone = data.get('phone', '5511999999999')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        response = bot.get_ai_response(message, phone)
        
        return jsonify({
            'response': response,
            'phone': phone,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Chatbot',
        'timestamp': datetime.now().isoformat(),
        'openai_configured': bool(os.environ.get('OPENAI_API_KEY'))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)