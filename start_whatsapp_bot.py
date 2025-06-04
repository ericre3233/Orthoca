#!/usr/bin/env python3
"""
Startup script for WhatsApp Bot
"""

import subprocess
import sys
import os

def start_whatsapp_bot():
    """Start the WhatsApp bot service"""
    try:
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_APP'] = 'whatsapp_bot.py'
        env['FLASK_ENV'] = 'production'
        
        # Start the WhatsApp bot on port 8001
        cmd = [sys.executable, 'whatsapp_bot.py']
        
        print("Starting WhatsApp Bot service on port 8001...")
        process = subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\nWhatsApp Bot service stopped.")
    except Exception as e:
        print(f"Error starting WhatsApp Bot: {str(e)}")

if __name__ == '__main__':
    start_whatsapp_bot()