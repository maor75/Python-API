from flask import Flask, request, jsonify, render_template_string
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from maor.env file
load_dotenv('maor.env')

app = Flask(__name__)

# Secret value - MUST be set via environment variable
SECRET_VALUE = os.environ.get('SECRET_VALUE')
LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/access.log')

# Security check: Fail fast if secret is not configured
if not SECRET_VALUE:
    raise ValueError(
        "SECRET_VALUE environment variable is required! "
        "Make sure maor.env file exists and contains SECRET_VALUE=your-secret"
    )

# Configure Log Rotation
# 1GB = 1024 * 1024 * 1024 bytes
# Keep 10 backup files (total 11 files: access.log + access.log.1 through access.log.10)
def setup_logging():
    """
    Set up rotating file handler for access logs
    - Max file size: 1GB
    - Max files: 10 backups (11 total including current)
    - When access.log reaches 1GB:
      1. Rename access.log -> access.log.1
      2. Create new access.log
      3. If access.log.10 exists, delete it
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    # Create rotating file handler
    # maxBytes = 1GB = 1073741824 bytes
    # backupCount = 10 (keeps 10 old files + 1 current = 11 total)
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024 * 1024,  # 1GB
        backupCount=10,               # Keep 10 backup files
        encoding='utf-8'
    )
    
    # Set log format
    formatter = logging.Formatter('%(asctime)s - IP: %(message)s')
    handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger('access_log')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# Initialize the logger
access_logger = setup_logging()

# HTML Template for the homepage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Validator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        .welcome {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input[type="password"],
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="password"]:focus,
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .result.success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 2px solid #dc3545;
            color: #721c24;
        }
        .result-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .api-info {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
        }
        .api-info code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Secret Validator</h1>
        <p class="welcome">Hello User! Please enter your secret to validate.</p>
        
        <form id="validateForm">
            <div class="form-group">
                <label for="secret">Enter Your Secret:</label>
                <input type="password" id="secret" name="secret" placeholder="Enter secret here..." required>
            </div>
            <button type="submit">Validate Secret</button>
        </form>
        
        <div id="result" class="result"></div>
        
        <div class="api-info">
            <strong>API Endpoints:</strong><br>
            • <code>GET /IsAlive</code> - Health check<br>
            <small>Log rotation: 1GB per file, max 10 backups</small>
        </div>
    </div>

    <script>
        document.getElementById('validateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const secret = document.getElementById('secret').value;
            const resultDiv = document.getElementById('result');
            
            try {
                const response = await fetch('/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ secret: secret })
                });
                
                const data = await response.json();
                
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <div class="result-icon">✅</div>
                        <strong>Success!</strong><br>
                        ${data.message}<br>
                        <small>Your IP (${data.client_ip}) has been logged.</small>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <div class="result-icon">❌</div>
                        <strong>Error!</strong><br>
                        ${data.message}
                    `;
                }
                
                // Clear the input
                document.getElementById('secret').value = '';
                
            } catch (error) {
                resultDiv.style.display = 'block';
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <div class="result-icon">⚠️</div>
                    <strong>Connection Error!</strong><br>
                    Could not connect to the server.
                `;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    """Homepage with web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/IsAlive', methods=['GET'])
def IsAlive():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/validate', methods=['POST'])
def validate():
    """
    Validates user-provided secret against stored secret.
    On success, logs client IP to file with automatic rotation.
    
    Expected JSON body: {"secret": "value"}
    """
    try:
        data = request.get_json()
        
        if not data or 'secret' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'secret' field in request body"
            }), 400
        
        user_secret = data['secret']
        
        # Validate secret
        if user_secret == SECRET_VALUE:
            # Get client IP (handle proxy headers)
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            # Log to rotating file using logger
            # This automatically handles rotation when file reaches 1GB
            access_logger.info(f"{client_ip} - Validation SUCCESS")
            
            return jsonify({
                "success": True,
                "message": "Secret validated successfully",
                "client_ip": client_ip
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid secret"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/log-stats', methods=['GET'])
def log_stats():
    """
    Show information about log files
    """
    try:
        log_dir = os.path.dirname(LOG_FILE)
        log_files = []
        
        # Get all log files
        for i in range(11):  # Current log + 10 backups
            if i == 0:
                log_path = LOG_FILE
            else:
                log_path = f"{LOG_FILE}.{i}"
            
            if os.path.exists(log_path):
                size = os.path.getsize(log_path)
                size_mb = size / (1024 * 1024)  # Convert to MB
                log_files.append({
                    "file": os.path.basename(log_path),
                    "size_mb": round(size_mb, 2),
                    "size_bytes": size
                })
        
        return jsonify({
            "log_directory": log_dir,
            "files": log_files,
            "total_files": len(log_files),
            "max_file_size_gb": 1,
            "max_backup_files": 10
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from outside container
    app.run(host='0.0.0.0', port=5000, debug=False)