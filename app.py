# Fal Gram Bot - Web Service for Render.com
# Version: 3.1.1

import os
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot instance (will be set by main bot)
bot_instance = None

@app.route('/')
def home():
    """Ana sayfa - Bot durumu"""
    return jsonify({
        'message': 'Fal Gram Bot is running!',
        'version': '3.1.1',
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

@app.route('/health')
def health_check():
    """Render.com health check endpoint"""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'bot_status': 'running' if bot_instance else 'not_initialized',
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
        
        # Check environment variables
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'GEMINI_API_KEY',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            health_status['status'] = 'warning'
            health_status['missing_vars'] = missing_vars
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/metrics')
def metrics():
    """Bot metrikleri"""
    try:
        # Basic metrics (bot instance varsa daha detaylı olabilir)
        metrics_data = {
            'uptime': datetime.now().isoformat(),
            'version': '3.1.1',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'bot_initialized': bot_instance is not None
        }
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Detaylı bot durumu"""
    try:
        status_data = {
            'bot': {
                'status': 'running' if bot_instance else 'not_initialized',
                'version': '3.1.1'
            },
            'database': {
                'status': 'connected' if os.getenv('SUPABASE_URL') else 'not_configured'
            },
            'ai': {
                'status': 'configured' if os.getenv('GEMINI_API_KEY') else 'not_configured'
            },
            'payment': {
                'status': 'configured' if os.getenv('PAYMENT_PROVIDER_TOKEN') else 'not_configured'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint (alternatif)"""
    try:
        # Webhook data processing
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        # Bu endpoint bot instance varsa kullanılabilir
        if bot_instance:
            # Process webhook with bot
            pass
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/health',
            '/metrics',
            '/status',
            '/webhook'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

def set_bot_instance(bot):
    """Bot instance'ını set et (main bot'tan çağrılır)"""
    global bot_instance
    bot_instance = bot
    logger.info("Bot instance set for web service")

def run_flask_app():
    """Flask app'ı çalıştır"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_web_service():
    """Web service'i ayrı thread'de başlat"""
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info(f"Web service started on port {os.environ.get('PORT', 8080)}")

if __name__ == '__main__':
    # Direct run for testing
    start_web_service() 

    