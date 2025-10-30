

config = {
    'headers': [],
    'specs': [{'endpoint': 'apispec', 'route': '/apispec.json'}],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/api/doc'
}

# Initialize Flasgger/Swagger with pure OpenAPI 3 template (no 'swagger' field)
template = {
    'openapi': '3.0.3',
    'info': {
        'title': 'Flask Session Auth API',
        'description': 'A simple Flask API with Redis-backed session authentication.',
        'version': '1.0.0',
        'contact': {
            'name': 'Your Name', 
            'email': 'your@email.com'
        }
    },
    'security': [
        {
            'cookieAuth': []
        }
    ],  # Global cookie auth scheme
    'components': {
        'securitySchemes': {
            'cookieAuth': {  # Defines session cookie auth
                'type': 'apiKey',
                'in': 'cookie',
                'name': 'session'
            }
        }
    },
    'servers': [
        {
            'url': 'http://localhost:5000', 
            'description': 'Local'
        }
    ],    
    'consumes': ['application/json'],  # Enforce JSON for all endpoints
    'produces': ['application/json'],
}


class schemas:
    login_schema = {
        'summary': 'Authenticate user and create session',
        'description': 'Logs in a user and sets a session cookie.',
        'parameters': [
            {
                'name': 'body', 
                'in': 'body', 
                'required': True, 
                'schema': {
                    'type': 'object', 
                    'properties': {
                        'username': {
                            'type': 'string', 
                            'example': 'admin'
                        },
                        'password': {
                            'type': 'string', 
                            'example': 'password123', 
                            'format': 'password'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Login successful', 
                'schema': {
                    'type': 'object', 
                    'properties': {
                        'message': {
                            'type': 'string'
                        }
                    }
                }
            },
            401: {
                'description': 'Invalid credentials'
            }
        }
    }