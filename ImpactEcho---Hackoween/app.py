from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "impactecho_secret_key_2025"  # Change this to a secure random key in production

# ---------------------------
# Paths for data storage
# ---------------------------
HASH_FILE = "hash_store.json"
DATA_FILE = "causes.json"
USERS_FILE = "users.json"
LOGIN_LOGS_FILE = "login_logs.json"
DONATION_LOGS_FILE = "donation_logs.json"
NGO_REGISTRATIONS_FILE = "ngo_registrations.json"
NGO_CREDENTIALS_FILE = "ngo_credentials.json"
NGO_CAUSE_REQUESTS_FILE = "ngo_cause_requests.json"
UPLOAD_FOLDER = "uploads"

# Admin credentials (in production, use hashed passwords and database)
ADMIN_CREDENTIALS = {
    "admin": "admin123"  # username: password
}

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

# Ensure files exist
if not os.path.exists(HASH_FILE):
    with open(HASH_FILE, "w") as f:
        json.dump({}, f, indent=4)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(LOGIN_LOGS_FILE):
    with open(LOGIN_LOGS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(DONATION_LOGS_FILE):
    with open(DONATION_LOGS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(NGO_REGISTRATIONS_FILE):
    with open(NGO_REGISTRATIONS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(NGO_CREDENTIALS_FILE):
    with open(NGO_CREDENTIALS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(NGO_CAUSE_REQUESTS_FILE):
    with open(NGO_CAUSE_REQUESTS_FILE, "w") as f:
        json.dump([], f, indent=4)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------------------
# Utility functions
# ---------------------------
def load_hashes():
    with open(HASH_FILE, "r") as f:
        return json.load(f)

def save_hashes(data):
    with open(HASH_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_login_logs():
    with open(LOGIN_LOGS_FILE, "r") as f:
        return json.load(f)

def save_login_logs(data):
    with open(LOGIN_LOGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_donation_logs():
    with open(DONATION_LOGS_FILE, "r") as f:
        return json.load(f)

def save_donation_logs(data):
    with open(DONATION_LOGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def log_login(user_type, identifier):
    logs = load_login_logs()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "user_type": user_type,
        "identifier": identifier
    })
    save_login_logs(logs)

def log_donation(address, cause_title, amount):
    logs = load_donation_logs()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "wallet_address": address,
        "cause": cause_title,
        "amount": amount
    })
    save_donation_logs(logs)

def load_ngo_registrations():
    with open(NGO_REGISTRATIONS_FILE, "r") as f:
        return json.load(f)

def save_ngo_registrations(data):
    with open(NGO_REGISTRATIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_ngo_credentials():
    with open(NGO_CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def save_ngo_credentials(data):
    with open(NGO_CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_ngo_cause_requests():
    with open(NGO_CAUSE_REQUESTS_FILE, "r") as f:
        return json.load(f)

def save_ngo_cause_requests(data):
    with open(NGO_CAUSE_REQUESTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_id():
    import random
    import string
    return 'NGO' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ---------------------------
# Routes
# ---------------------------

# Home / Login Selection page
@app.route("/")
def home():
    return render_template("login.html")  # Choose Admin or Donator

# Admin login page
@app.route("/admin-login")
def admin_login_page():
    return render_template("admin_login.html")

# Admin login authentication
@app.route("/admin-auth", methods=["POST"])
def admin_auth():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        session["admin"] = True
        session["username"] = username
        log_login("admin", username)
        return jsonify({"success": True, "redirect": "/admin"})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

# Admin dashboard (protected)
@app.route("/admin")
def admin_page():
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin.html")

# Admin logout
@app.route("/admin-logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

# Get admin data (users, logs)
@app.route("/api/admin/data")
def get_admin_data():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "users": load_users(),
        "login_logs": load_login_logs(),
        "donation_logs": load_donation_logs()
    })

# Donator MetaMask connection page
@app.route("/donator-login")
def donator_login():
    return render_template("metamask_connect.html")

# Dash page (after MetaMask authentication)
@app.route("/dash")
def dash():
    return render_template("dash.html")

# Donator Logout
@app.route("/donator-logout")
def donator_logout():
    session.clear()
    return redirect(url_for("home"))

# API to store hash and user data
@app.route("/api/store-hash", methods=["POST"])
def store_hash():
    data = request.get_json()
    if not data or "hash" not in data:
        return jsonify({"error": "Invalid data"}), 400

    all_hashes = load_hashes()
    hash_key = data["hash"]
    address = data.get("address")
    
    all_hashes[hash_key] = {
        "address": address,
        "timestamp": data.get("timestamp"),
        "nonce": data.get("nonce")
    }
    save_hashes(all_hashes)
    
    # Store user data
    users = load_users()
    user_exists = any(u["wallet_address"] == address for u in users)
    
    if not user_exists:
        users.append({
            "wallet_address": address,
            "joined_date": datetime.now().isoformat(),
            "total_donations": 0,
            "total_amount": 0
        })
        save_users(users)
    
    # Log login
    log_login("donator", address)
    
    return jsonify({"message": "Hash stored successfully!"})

# Get all causes (for dashboard)
@app.route("/causes", methods=["GET"])
def get_causes():
    with open(DATA_FILE, "r") as f:
        causes = json.load(f)
    return jsonify(causes), 200

# Add new cause (admin only)
@app.route("/causes", methods=["POST"])
def add_cause():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    required_fields = ["title", "description", "goal", "image"]

    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    with open(DATA_FILE, "r") as f:
        causes = json.load(f)

    new_cause = {
        "id": len(causes) + 1,
        "title": data["title"],
        "description": data["description"],
        "goal": data["goal"],
        "raised": 0,
        "image": data["image"]
    }

    causes.append(new_cause)

    with open(DATA_FILE, "w") as f:
        json.dump(causes, f, indent=4)

    return jsonify({"message": "Cause added successfully!", "cause": new_cause}), 201

# Log donation (called from frontend)
@app.route("/api/log-donation", methods=["POST"])
def api_log_donation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    address = data.get("wallet_address")
    cause_title = data.get("cause_title")
    amount = data.get("amount")
    
    if not all([address, cause_title, amount]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Log donation
    log_donation(address, cause_title, amount)
    
    # Update user stats
    users = load_users()
    for user in users:
        if user["wallet_address"] == address:
            user["total_donations"] += 1
            user["total_amount"] += amount
            break
    save_users(users)
    
    return jsonify({"message": "Donation logged successfully!"})

# ====================
# NGO ROUTES
# ====================

# NGO Registration Page (redirect to login page with tabs)
@app.route("/ngo-register")
def ngo_register_page():
    return redirect(url_for("ngo_login_page"))

# NGO Registration Submission
@app.route("/ngo-register-submit", methods=["POST"])
def ngo_register_submit():
    try:
        # Get form data
        email = request.form.get("email")
        org_name = request.form.get("org_name")
        person_name = request.form.get("person_name")
        contact = request.form.get("contact")
        terms = request.form.get("terms")
        
        if not all([email, org_name, person_name, contact, terms]):
            return jsonify({"error": "All fields are required"}), 400
        
        # Handle file uploads
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_files.append(filename)
        
        # Create registration entry
        registrations = load_ngo_registrations()
        registration = {
            "id": len(registrations) + 1,
            "email": email,
            "org_name": org_name,
            "person_name": person_name,
            "contact": contact,
            "files": uploaded_files,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "unique_id": None,
            "approved_at": None
        }
        
        registrations.append(registration)
        save_ngo_registrations(registrations)
        
        return jsonify({"success": True, "message": "Registration submitted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NGO Login Page
@app.route("/ngo-login")
def ngo_login_page():
    return render_template("ngo_login.html")

# Check if unique ID exists and has credentials
@app.route("/ngo-check-id", methods=["POST"])
def ngo_check_id():
    data = request.get_json()
    unique_id = data.get("unique_id")
    
    credentials = load_ngo_credentials()
    existing = next((c for c in credentials if c["unique_id"] == unique_id), None)
    
    if existing:
        return jsonify({"has_credentials": True})
    
    # Check if ID exists in approved registrations
    registrations = load_ngo_registrations()
    approved = next((r for r in registrations if r["unique_id"] == unique_id and r["status"] == "approved"), None)
    
    if approved:
        return jsonify({"has_credentials": False, "valid_id": True, "org_name": approved["org_name"]})
    
    return jsonify({"valid_id": False}), 404

# Create NGO credentials (one-time)
@app.route("/ngo-create-credentials", methods=["POST"])
def ngo_create_credentials():
    data = request.get_json()
    unique_id = data.get("unique_id")
    username = data.get("username")
    password = data.get("password")
    
    if not all([unique_id, username, password]):
        return jsonify({"error": "All fields required"}), 400
    
    # Check if credentials already exist
    credentials = load_ngo_credentials()
    if any(c["unique_id"] == unique_id for c in credentials):
        return jsonify({"error": "Credentials already created for this ID"}), 400
    
    # Verify ID is approved
    registrations = load_ngo_registrations()
    approved = next((r for r in registrations if r["unique_id"] == unique_id and r["status"] == "approved"), None)
    
    if not approved:
        return jsonify({"error": "Invalid or unapproved ID"}), 400
    
    # Create credentials
    credentials.append({
        "unique_id": unique_id,
        "username": username,
        "password": password,  # In production, hash this!
        "org_name": approved["org_name"],
        "created_at": datetime.now().isoformat()
    })
    save_ngo_credentials(credentials)
    
    return jsonify({"success": True, "message": "Credentials created successfully"})

# NGO Login Authentication
@app.route("/ngo-auth", methods=["POST"])
def ngo_auth():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    credentials = load_ngo_credentials()
    ngo = next((c for c in credentials if c["username"] == username and c["password"] == password), None)
    
    if ngo:
        session["ngo"] = True
        session["ngo_id"] = ngo["unique_id"]
        session["ngo_name"] = ngo["org_name"]
        log_login("ngo", username)
        return jsonify({"success": True, "redirect": "/ngo-dashboard"})
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

# NGO Dashboard
@app.route("/ngo-dashboard")
def ngo_dashboard():
    if not session.get("ngo"):
        return redirect(url_for("ngo_login_page"))
    return render_template("ngo_dashboard.html")

# NGO Logout
@app.route("/ngo-logout")
def ngo_logout():
    session.clear()
    return redirect(url_for("home"))

# Submit cause request (NGO)
@app.route("/ngo-cause-request", methods=["POST"])
def ngo_cause_request():
    if not session.get("ngo"):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    requests_list = load_ngo_cause_requests()
    
    new_request = {
        "id": len(requests_list) + 1,
        "ngo_id": session["ngo_id"],
        "ngo_name": session["ngo_name"],
        "title": data["title"],
        "description": data["description"],
        "goal": data["goal"],
        "image": data["image"],
        "status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "approved_at": None
    }
    
    requests_list.append(new_request)
    save_ngo_cause_requests(requests_list)
    
    return jsonify({"success": True, "message": "Cause request submitted"})

# Get NGO's cause requests
@app.route("/ngo-my-requests")
def ngo_my_requests():
    if not session.get("ngo"):
        return jsonify({"error": "Unauthorized"}), 401
    
    requests_list = load_ngo_cause_requests()
    my_requests = [r for r in requests_list if r["ngo_id"] == session["ngo_id"]]
    return jsonify(my_requests)

# ====================
# ADMIN - NGO MANAGEMENT
# ====================

# Get all NGO data (admin)
@app.route("/api/admin/ngo-data")
def get_ngo_data():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "registrations": load_ngo_registrations(),
        "cause_requests": load_ngo_cause_requests()
    })

# Approve NGO registration (admin)
@app.route("/admin-approve-ngo/<int:reg_id>", methods=["POST"])
def approve_ngo(reg_id):
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    registrations = load_ngo_registrations()
    registration = next((r for r in registrations if r["id"] == reg_id), None)
    
    if not registration:
        return jsonify({"error": "Registration not found"}), 404
    
    # Generate unique ID
    unique_id = generate_unique_id()
    registration["status"] = "approved"
    registration["unique_id"] = unique_id
    registration["approved_at"] = datetime.now().isoformat()
    
    save_ngo_registrations(registrations)
    
    return jsonify({"success": True, "unique_id": unique_id})

# Approve cause request (admin)
@app.route("/admin-approve-cause/<int:req_id>", methods=["POST"])
def approve_cause(req_id):
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    requests_list = load_ngo_cause_requests()
    cause_request = next((r for r in requests_list if r["id"] == req_id), None)
    
    if not cause_request:
        return jsonify({"error": "Request not found"}), 404
    
    # Update request status
    cause_request["status"] = "approved"
    cause_request["approved_at"] = datetime.now().isoformat()
    save_ngo_cause_requests(requests_list)
    
    # Add to main causes
    causes = []
    with open(DATA_FILE, "r") as f:
        causes = json.load(f)
    
    new_cause = {
        "id": len(causes) + 1,
        "title": cause_request["title"],
        "description": cause_request["description"],
        "goal": cause_request["goal"],
        "raised": 0,
        "image": cause_request["image"],
        "ngo_name": cause_request["ngo_name"]
    }
    
    causes.append(new_cause)
    
    with open(DATA_FILE, "w") as f:
        json.dump(causes, f, indent=4)
    
    return jsonify({"success": True, "message": "Cause approved and added to dashboard"})

# Serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    if not session.get("admin"):
        return "Unauthorized", 401
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve static files (CSS, JS, images)
@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    # Use host='0.0.0.0' to make accessible on local network
    app.run(host='0.0.0.0', debug=True, port=8000)
