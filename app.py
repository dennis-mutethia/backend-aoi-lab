
import logging 
import os 

from dotenv import load_dotenv

from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify, session
from flask_session import Session
import redis
from werkzeug.security import generate_password_hash, check_password_hash

from utils.swagger import ( 
    config as swagger_config, 
    template as swagger_template, 
    schemas
)


# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = app.secret_key = os.environ.get('SECRET_KEY')

# Configure Redis for sessions (replace with your Redis connection details)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host=os.getenv('REDIS_HOSTNAME'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
    ssl=True,          # Set to True for secure connections (e.g., Upstash)
    decode_responses=True  # Ensures string responses
)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'

# Initialize Session
Session(app)

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(app.name)


# Initialize Flasgger/Swagger
# Configure Flasgger for OpenAPI 3.0 to avoid conflicts
app.config['SWAGGER'] = {
    'openapi': '3.0.3',
    'uiversion': 3  # Use Swagger UI v3 for OAS3 support
}


swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Simple in-memory user database (use a real database in production)
users = {
    'admin': generate_password_hash('password123')
}


@app.route('/api/login', methods=['POST'])
@swag_from(schemas.login_schema)
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    session['user'] = username
    return jsonify({'message': 'Login successful'}), 200

@app.route('/api/logout', methods=['POST'])
@swag_from({
    'summary': 'Clear session',
    'description': 'Logs out the user by clearing the session.',
    'responses': {
        200: {'description': 'Logout successful', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
    },
    'security': [{'cookieAuth': []}]
})
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/protected', methods=['GET'])
@swag_from({
    'summary': 'Protected endpoint',
    'description': 'Access requires a valid session (cookie).',
    'responses': {
        200: {'description': 'Success', 'schema': {'type': 'object', 'properties': {
            'message': {'type': 'string'}, 'user': {'type': 'string'}
        }}},
        401: {'description': 'Authentication required'}
    },
    'security': [{'cookieAuth': []}]
})
def protected():
    if 'user' not in session:
        return jsonify({'message': 'Authentication required'}), 401
    
    current_user = session['user']
    return jsonify({
        'message': f'Hello, {current_user}! This is a protected endpoint.',
        'user': current_user
    }), 200

@app.route('/api/public', methods=['GET'])
@swag_from({
    'summary': 'Public endpoint',
    'description': 'No authentication required.',
    'responses': {
        200: {'description': 'Public message', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
    }
})
def public():
    return jsonify({'message': 'This is a public endpoint.'}), 200


if __name__ == '__main__':
    debug_mode = os.getenv('IS_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
