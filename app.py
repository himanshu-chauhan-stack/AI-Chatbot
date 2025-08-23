"""
AI Chat Assistant - Flask Backend
A production-ready ChatGPT-like interface using Google's Gemini API
"""

from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import logging
import traceback
from datetime import datetime
import uuid
from config import GEMINI_API_KEY, SECRET_KEY, DEBUG, MAX_CHAT_HISTORY, AI_ROLES, DEFAULT_AI_ROLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

class ChatAssistant:
    """Main chat assistant class handling AI interactions"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("ChatAssistant initialized with Gemini 1.5 Flash model")
    
    def generate_response(self, prompt, chat_history=None, ai_role="helpful_assistant"):
        """
        Generate AI response using Gemini API
        
        Args:
            prompt (str): User's message
            chat_history (list): Previous conversation messages
            ai_role (str): AI personality role
            
        Returns:
            str: AI response
        """
        try:
            # Get role configuration
            role_config = AI_ROLES.get(ai_role, AI_ROLES[DEFAULT_AI_ROLE])
            system_prompt = role_config["system_prompt"]
            
            # Build conversation context
            conversation = f"System: {system_prompt}\n\n"
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    role = "Human" if msg['role'] == 'user' else "Assistant"
                    conversation += f"{role}: {msg['content']}\n"
            
            # Add current prompt
            conversation += f"Human: {prompt}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(conversation)
            
            if response.text:
                logger.info(f"Generated response for role '{ai_role}': {len(response.text)} characters")
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini API")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}\n{traceback.format_exc()}")
            return "I'm experiencing technical difficulties. Please try again in a moment."

    def stream_response(self, prompt, ai_role="helpful_assistant"):
        """Yield chunks for streaming (SSE)."""
        role_config = AI_ROLES.get(ai_role, AI_ROLES[DEFAULT_AI_ROLE])
        system_prompt = role_config["system_prompt"]
        conversation = f"System: {system_prompt}\n\nHuman: {prompt}\nAssistant:"
        try:
            stream = self.model.generate_content(conversation, stream=True)
            accumulated = []
            for chunk in stream:
                if not hasattr(chunk, 'text'):
                    continue
                text = chunk.text
                if not text:
                    continue
                accumulated.append(text)
                yield {'delta': text}
            full = ''.join(accumulated)
            yield {'done': True, 'response': full, 'ai_role': ai_role, 'role_name': role_config['name']}
        except Exception as e:
            yield {'error': str(e)}

# Initialize chat assistant
chat_assistant = ChatAssistant()

def get_session_id():
    """Get or create a unique session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def init_chat_session():
    """Initialize chat session data"""
    session_id = get_session_id()
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'ai_role' not in session:
        session['ai_role'] = DEFAULT_AI_ROLE
    return session_id

@app.route('/')
def index():
    """Main chat interface route"""
    init_chat_session()
    return render_template('index.html', ai_roles=AI_ROLES)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages via AJAX"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        ai_role = data.get('ai_role', session.get('ai_role', DEFAULT_AI_ROLE))
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Initialize session
        session_id = init_chat_session()
        logger.info(f"Processing chat for session {session_id}")
        
        # Update AI role if changed
        session['ai_role'] = ai_role
        
        # Quick intent overrides (model / developer questions)
        lm = user_message.lower()
        override_response = None
        if ("model" in lm) and ("which" in lm or "what" in lm or "use" in lm or "using" in lm):
            override_response = "gemini 1.5 flash"
        elif ("who" in lm) and ("developed" in lm or "made" in lm or "created" in lm) and ("you" in lm or "assistant" in lm):
            override_response = "Ritesh and Himanshu"

        # Add user message to chat history
        user_msg = {
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        }
        session['chat_history'].append(user_msg)
        logger.info(f"Added user message to session. Total messages: {len(session['chat_history'])}")
        
        if override_response is not None:
            ai_response = override_response
            logger.info("Using override response: %s", ai_response)
        else:
            # Generate AI response
            ai_response = chat_assistant.generate_response(
                user_message, 
                session['chat_history'], 
                ai_role
            )
        
        # Add AI response to chat history
        ai_msg = {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        session['chat_history'].append(ai_msg)
        logger.info(f"Added AI response to session. Total messages: {len(session['chat_history'])}")
        
        # Limit chat history size
        if len(session['chat_history']) > MAX_CHAT_HISTORY:
            session['chat_history'] = session['chat_history'][-MAX_CHAT_HISTORY:]
            logger.info(f"Trimmed chat history to {MAX_CHAT_HISTORY} messages")
        
        # Save session
        session.modified = True
        logger.info("Session marked as modified")
        
        return jsonify({
            'response': ai_response,
            'ai_role': ai_role,
            'role_name': AI_ROLES[ai_role]['name']
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint (Server-Sent Events)."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        user_message = data['message'].strip()
        ai_role = data.get('ai_role', DEFAULT_AI_ROLE)
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        lm = user_message.lower()
        override_response = None
        if ("model" in lm) and ("which" in lm or "what" in lm or "use" in lm or "using" in lm):
            override_response = "gemini 1.5 flash"
        elif ("who" in lm) and ("developed" in lm or "made" in lm or "created" in lm) and ("you" in lm or "assistant" in lm):
            override_response = "Ritesh and Himanshu"

        def event_stream():
            if override_response is not None:
                yield f"data: {{\"delta\": \"{override_response}\"}}\n\n"
                yield f"data: {{\"done\": true, \"response\": \"{override_response}\", \"ai_role\": \"{ai_role}\", \"role_name\": \"{AI_ROLES.get(ai_role, AI_ROLES[DEFAULT_AI_ROLE])['name']}\"}}\n\n"
            else:
                for part in chat_assistant.stream_response(user_message, ai_role):
                    yield f"data: {part}\n\n" if isinstance(part, str) else f"data: {__import__('json').dumps(part)}\n\n"
        return app.response_class(event_stream(), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}")
        return jsonify({'error': 'Streaming failed'}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        session['chat_history'] = []
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing chat: {str(e)}")
        return jsonify({'error': 'Failed to clear chat'}), 500

@app.route('/get_history')
def get_history():
    """Get chat history for current session"""
    try:
        session_id = get_session_id()
        chat_history = session.get('chat_history', [])
        ai_role = session.get('ai_role', DEFAULT_AI_ROLE)
        
        logger.info(f"Retrieved chat history for session {session_id}: {len(chat_history)} messages")
        
        return jsonify({
            'history': chat_history,
            'ai_role': ai_role,
            'session_id': session_id
        })
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Failed to get chat history'}), 500

@app.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({'message': 'Server is working!', 'timestamp': datetime.now().isoformat()})

@app.route('/test-page')
def test_page():
    """Test page for API"""
    return render_template('test.html')

@app.route('/debug')
def debug_page():
    """Simple debug page for chat"""
    return render_template('debug.html')

@app.route('/debug_session')
def debug_session():
    """Debug endpoint to check session data"""
    if not DEBUG:
        return jsonify({'error': 'Debug mode only'}), 403
    
    session_id = get_session_id()
    return jsonify({
        'session_id': session_id,
        'chat_history_count': len(session.get('chat_history', [])),
        'ai_role': session.get('ai_role', 'none'),
        'session_data': dict(session)
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_model': 'gemini-1.5-flash'
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info("Starting AI Chat Assistant Flask application")
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
