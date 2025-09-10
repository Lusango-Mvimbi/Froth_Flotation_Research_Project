"""
Simple Flask Login Page for Froth Flotation Digital Twin
======================================================

A reliable Flask-based login page with database authentication.
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
import sys
import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database_manager import db

from services.shared_logging import setup_logger

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
log_file = os.path.join(log_dir, 'authentication_service.log')
logger = setup_logger(__name__, log_file, level=logging.WARNING)

# Log service startup (WARNING level for important startup info)
logger.warning("Starting Froth Flotation Authentication Service")
logger.warning(f"Log file: {log_file}")
logger.warning(f"Service: Flask Authentication Server")
logger.warning(f"Port: 8051")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # In production, use a secure secret key

# Enable CORS for React frontend
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# HTML template for the login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Froth Flotation Digital Twin</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #2d3748 100%);
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e2e8f0;
            overflow: hidden;
            position: relative;
        }
        
        /* Animated background particles */
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(96, 165, 250, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(1deg); }
            66% { transform: translateY(10px) rotate(-1deg); }
        }
        
        .login-container {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 24px;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            padding: 3rem;
            width: 100%;
            max-width: 450px;
            backdrop-filter: blur(20px);
            border: 1px solid #475569;
            position: relative;
            z-index: 10;
            animation: slideInUp 0.6s ease-out;
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        .login-header .icon {
            font-size: 3rem;
            background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            display: block;
        }
        
        .login-header h1 {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }
        
        .login-header p {
            color: #94a3b8;
            font-size: 1rem;
            font-weight: 500;
            margin: 0;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .form-label {
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 0.75rem;
            display: block;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .input-group {
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #64748b;
            font-size: 1.1rem;
            z-index: 2;
            transition: color 0.3s ease;
        }
        
        .form-control {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 1rem 1rem 1rem 3rem;
            font-size: 1rem;
            color: #e2e8f0;
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            backdrop-filter: blur(10px);
        }
        
        .form-control::placeholder {
            color: #64748b;
        }
        
        .form-control:focus {
            border-color: #60a5fa;
            box-shadow: 
                0 0 0 3px rgba(96, 165, 250, 0.1),
                0 8px 25px rgba(0, 0, 0, 0.2);
            outline: none;
            background: rgba(15, 23, 42, 0.8);
        }
        
        .form-control:focus + .input-icon {
            color: #60a5fa;
        }
        
        .btn-login {
            background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 8px 25px rgba(96, 165, 250, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .btn-login::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn-login:hover::before {
            left: 100%;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(96, 165, 250, 0.4);
        }
        
        .btn-login:active {
            transform: translateY(0);
        }
        
        .alert {
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            border: none;
            font-weight: 500;
            backdrop-filter: blur(10px);
        }
        
        .alert-danger {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .alert-success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .credentials-info {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
            text-align: center;
        }
        
        .credentials-info h4 {
            color: #60a5fa;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .credentials-info p {
            color: #94a3b8;
            font-size: 0.9rem;
            margin: 0.25rem 0;
        }
        
        .credentials-info .highlight {
            color: #e2e8f0;
            font-weight: 600;
            background: rgba(96, 165, 250, 0.2);
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            margin: 0 0.25rem;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .login-container {
                margin: 1rem;
                padding: 2rem;
                max-width: 100%;
            }
            
            .login-header h1 {
                font-size: 1.8rem;
            }
            
            .login-header .icon {
                font-size: 2.5rem;
            }
        }
        
        /* Loading animation */
        .btn-login.loading {
            pointer-events: none;
        }
        
        .btn-login.loading::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            border: 2px solid transparent;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        }
        .input-group {
            position: relative;
            display: flex;
            align-items: center;
        }
        .input-group-text {
            background: #f8f9fa;
            border: 2px solid #e1e5e9;
            border-right: none;
            border-radius: 10px 0 0 10px;
            padding: 12px 15px;
            color: #666;
            font-size: 1rem;
        }
        .input-group .form-control {
            border-left: none;
            border-radius: 0 10px 10px 0;
        }
        .btn-login {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 12px 30px;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(30, 60, 114, 0.3);
        }
        .btn-login:active {
            transform: translateY(0);
        }
        .footer-text {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9rem;
        }
        .footer-text p {
            margin: 5px 0;
        }
        .alert {
            border-radius: 10px;
            margin-bottom: 20px;
            padding: 15px;
            border: none;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .alert-info {
            background-color: #d1ecf1;
            color: #0c5460;
            border-left: 4px solid #17a2b8;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <i class="fas fa-industry icon"></i>
            <h1>Froth Flotation Digital Twin</h1>
            <p>Industrial Process Monitoring System</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }}">
                        <i class="fas fa-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' if category == 'success' else 'info-circle' }} me-2"></i>
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label for="username" class="form-label">Username</label>
                <div class="input-group">
                    <input type="text" class="form-control" id="username" name="username" placeholder="Enter your username" required>
                    <i class="fas fa-user input-icon"></i>
                </div>
            </div>
            
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                    <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required>
                    <i class="fas fa-lock input-icon"></i>
                </div>
            </div>
            
            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt me-2"></i>Login to System
            </button>
        </form>
        
        <div class="credentials-info">
            <h4><i class="fas fa-info-circle me-2"></i>Default Credentials</h4>
            <p>Contact your system administrator for login credentials</p>
        </div>
    </div>
    
    <script>
        // Add loading animation to login button
        document.querySelector('form').addEventListener('submit', function() {
            const button = document.querySelector('.btn-login');
            button.classList.add('loading');
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests"""
    if request.method == 'POST':
        # Check if request is JSON (from React frontend)
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            # Handle form data (from direct Flask access)
            username = request.form.get('username')
            password = request.form.get('password')
        
        logger.info(f"=== LOGIN ATTEMPT ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request is JSON: {request.is_json}")
        logger.info(f"Username: {username}")
        logger.info(f"Password length: {len(password) if password else 0}")
        
        if not username or not password:
            logger.warning("Missing username or password")
            if request.is_json:
                return jsonify({"success": False, "message": "Please enter both username and password"}), 400
            else:
                flash("Please enter both username and password", "error")
                return render_template_string(LOGIN_TEMPLATE)
        
        try:
            # Authenticate user
            user = db.authenticate_user(username, password)
            
            if user:
                logger.info(f"Authentication successful for user: {user['username']}")
                
                # Create session
                session_token = db.create_session(user['id'])
                logger.info(f"Session created: {session_token[:20]}...")
                
                # Store user info in Flask session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['session_token'] = session_token
                
                if request.is_json:
                    # Return JSON response for React frontend
                    return jsonify({
                        "success": True,
                        "message": f"Login successful! Welcome back, {user['full_name'] or user['username']}!",
                        "token": session_token,
                        "user": {
                            "id": user['id'],
                            "username": user['username'],
                            "full_name": user['full_name'],
                            "role": user['role']
                        }
                    })
                else:
                    # Return HTML response for direct Flask access
                    flash(f"Login successful! Welcome back, {user['full_name'] or user['username']}!", "success")
                    return redirect("http://localhost:3000/dashboard")
            else:
                logger.warning("Authentication failed - invalid credentials")
                if request.is_json:
                    return jsonify({"success": False, "message": "Invalid username or password. Please try again."}), 401
                else:
                    flash("Invalid username or password. Please try again.", "error")
                    return render_template_string(LOGIN_TEMPLATE)
                
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            if request.is_json:
                return jsonify({"success": False, "message": f"Login error: {str(e)}"}), 500
            else:
                flash(f"Login error: {str(e)}", "error")
                return render_template_string(LOGIN_TEMPLATE)
    
    # GET request - clear any existing session and show login form
    session.clear()  # Clear any existing session data
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/verify', methods=['GET'])
def verify_token():
    """Verify authentication token"""
    try:
        logger.info("=== TOKEN VERIFICATION ATTEMPT ===")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        logger.info(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("No valid Authorization header found")
            return jsonify({"success": False, "message": "No valid token provided"}), 401
        
        token = auth_header.split(' ')[1]
        logger.info(f"Token extracted: {token[:20]}...")
        
        # Verify token in database
        user = db.validate_session(token)
        if user:
            logger.info(f"Token verification successful for user: {user['username']}")
            return jsonify({
                "success": True,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            })
        else:
            logger.warning("Token verification failed - invalid or expired token")
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401
            
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({"success": False, "message": "Token verification failed"}), 500

@app.route('/clear-session')
def clear_session():
    """Clear session and redirect to login"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    logger.info("=== STARTING FLASK LOGIN SERVER ===")
    logger.info("Starting Flask Login Server...")
    logger.info("Login page: http://localhost:8051")
    logger.info("Login system ready - contact administrator for credentials")
    
    app.run(
        host="0.0.0.0",
        port=8051,
        debug=False
    )

