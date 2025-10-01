#integration file.
import os
from flask import Flask, jsonify, send_from_directory, request, session
import hashlib
import csv
import random
import string
import sys 
import json # Ensure json is imported at the top level

# --- START NEW/UPDATED IMPORTS AND CONFIG ---
import requests
import pandas as pd
import qrcode
from PIL import Image

# ==========================================================
# *** CRITICAL BACKEND IMPORTS FIX ***
BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Import prescription core logic
from pure_backend_prescription import generate_prescription, get_prescriptions, download_prescription
# Import new appointment core logic
from pure_appointment import send_application, get_applications_by_recipient 
# ==========================================================


# --- FILE PATHS (Adjusted for backend/QR_code location) ---
QR_CODE_ROOT = os.path.join(os.path.dirname(__file__), 'QR_code')
QR_IMAGES_FOLDER = os.path.join(QR_CODE_ROOT, 'qrcodes') 
CSV_FILE_PATH = os.path.join(QR_CODE_ROOT, 'profiles.csv') 
PRESCRIPTIONS_JSON_PATH = os.path.join(BACKEND_DIR, 'prescription.json') # Define the full path for Flask access

# --- CHATBOT CONFIG ---
CHATBOT_URL = "http://127.0.0.1:8000/chat" 

# --- QR CODE HEADERS ---
QR_HEADERS = [
    "Name","ABHA ID","Date of Birth","Blood Group","Age","Work / Occupation",
    "Allergies","Spoken Languages","Permanent Address","Current Address",
    "Employer Name","Employer Phone","Vaccinations info"
]

# --- HELPER FUNCTIONS (Defined FIRST) ---

def get_profile_data_row(abha_id):
    """Reads profile data from CSV and returns a single row dictionary."""
    if not os.path.exists(CSV_FILE_PATH):
        return None 
    try:
        # Use pandas as originally intended
        df = pd.read_csv(CSV_FILE_PATH)
        profile_row = df[df["ABHA ID"] == abha_id]
        if not profile_row.empty:
            return profile_row.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"Error reading profiles CSV: {e}")
        return None

def generate_qr_for_profile(profile_data):
    """Generates and saves the QR code image for a single profile."""
    
    os.makedirs(QR_IMAGES_FOLDER, exist_ok=True)
    
    name = profile_data.get('Name', profile_data.get('ABHA ID', 'unknown'))
    qr_filename = f"{name}_qr.png"
    qr_path = os.path.join(QR_IMAGES_FOLDER, qr_filename)

    # Use QR_HEADERS to define content structure
    qr_data = "\n".join([f"{col}: {profile_data.get(col, 'N/A')}" for col in QR_HEADERS])
    
    img = qrcode.make(qr_data)
    img.save(qr_path)
    
    # URL path for the browser to fetch the image via the serve_qr_code_image route
    return f"/qrcodes-data/{qr_filename}"

# --- CAPTCHA Data Definition ---
CAPTCHA_DATA = {
    "c1.png": "PNDQ",
    "W45F.png": "W45F",
    "WPJZ.png": "WPJZ"
}

# Define a function to hash passwords.
def hash_password(password: str) -> str:
    """Return a SHA256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

# Create the Flask application instance.
app = Flask(__name__, template_folder='../frontend')
app.secret_key = 'your_super_secret_key' 

# -------------------------------------------------------------------------
# --- FLASK ROUTES ---
# -------------------------------------------------------------------------

# QR Code Routes
@app.route('/qrcodes-data/<path:filename>')
def serve_qr_code_image(filename):
    """Serves generated QR code image files from the QR_code/qrcodes folder."""
    return send_from_directory(QR_IMAGES_FOLDER, filename)

@app.route('/api/generate-qr/<abha_id>', methods=['GET'])
def api_generate_qr(abha_id):
    """Generates the QR code, saves it, and returns the image URL."""
    profile_data = get_profile_data_row(abha_id)

    if profile_data is None:
        return jsonify({"status": "error", "message": "Profile data not found. Please save profile."}), 404

    qr_url = generate_qr_for_profile(profile_data)
    return jsonify({"status": "success", "qr_url": qr_url})

# Static Page Routes
@app.route('/')
def serve_intro():
    """Serves the intro page HTML file."""
    print("Serving intro.html...")
    return send_from_directory(app.template_folder, 'intro.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serves files from the assets folder."""
    return send_from_directory(os.path.join(app.template_folder, 'assets'), filename)

@app.route('/homepage')
@app.route('/homepage.html')
def serve_homepage():
    print("Serving homepage.html...")
    return send_from_directory(app.template_folder, 'homepage.html')

@app.route('/login')
@app.route('/login.html')
@app.route('/loginpage.html')
def serve_login():
    print("Serving loginpage.html...")
    return send_from_directory(app.template_folder, 'loginpage.html')

@app.route('/patientdash.html')
def serve_patient_dashboard():
    return send_from_directory(app.template_folder, 'patientdash.html')

@app.route('/doctordash.html')
def serve_doctor_dashboard():
    return send_from_directory(app.template_folder, 'doctordash.html')

@app.route('/doctordash.css')
def serve_doctordash_css():
    return send_from_directory(app.template_folder, 'doctordash.css')

@app.route('/script.js')
def serve_doctordash_js():
    return send_from_directory(app.template_folder, 'script.js')


# --- API ENDPOINT FOR CAPTCHA ---
@app.route('/api/captcha')
def get_captcha():
    captcha_filename, captcha_answer = random.choice(list(CAPTCHA_DATA.items()))
    session['captcha'] = captcha_answer.upper() 
    print(f"CAPTCHA set to: {captcha_answer}")
    captcha_dir = os.path.join(os.path.dirname(__file__), 'captchas')
    return send_from_directory(captcha_dir, captcha_filename)


# --- API ENDPOINT FOR LOGIN ---
@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('userType')
    captcha_input = data.get('captcha')
    print(f"Login attempt for user: {username} as {user_type}")

    if 'captcha' not in session or captcha_input.upper() != session['captcha'].upper():
        print("CAPTCHA validation failed.")
        get_captcha() 
        return jsonify({"status": "error", "message": "Invalid CAPTCHA."})
    
    filename = "patients.csv" if user_type == "Patient" else "doctors.csv"
    hashed_pw = hash_password(password)

    try:
        csv_file_path = os.path.join(os.path.dirname(__file__), filename)
        
        if not os.path.exists(csv_file_path):
             return jsonify({"status": "error", "message": f"User database file ({filename}) not found."})

        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row.get("ABHA ID")
                stored_hash = row.get("password")
                
                if user_id == username and stored_hash == hashed_pw:
                    if user_type == "Patient":
                        return jsonify({"status": "success", "redirect_url": f"/patientdash.html?user={username}"})
                    else: 
                        return jsonify({"status": "success", "redirect_url": f"/doctordash.html?user={username}"})
            
            return jsonify({"status": "error", "message": "Invalid ABHA ID or password."})

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"status": "error", "message": "An error occurred on the server."})

# --- MOCK API ENDPOINTS FOR DASHBOARD DATA ---
@app.route('/api/patient-data/<username>', methods=['GET'])
def get_patient_data(username):
    """Returns mock data for the patient dashboard."""
    mock_user_data = {
        'name': 'Amit',
        'username': username,
        'user_type': 'Worker'
    }
    return jsonify(mock_user_data)

# --- API ENDPOINTS FOR PROFILE PERSISTENCE (SAVES TO CSV) ---
@app.route('/api/save-profile', methods=['POST'])
def save_user_profile():
    """Receives profile data from the worker dashboard and saves/overwrites it in profiles.csv."""
    data = request.json
    
    username = data.get('abhaId')
    
    # Use the QR_HEADERS definition for consistency
    fieldnames = QR_HEADERS
    
    # Reconstruct vaccination and language strings
    vaccinations_info = "; ".join([f"{v['type']} on {v['date']}" for v in data.get('vaccinations', [])])
    languages = data.get('languages', '')
    
    new_row = {
        "Name": data.get('name'), 
        "ABHA ID": username,
        "Date of Birth": data.get('dob'),
        "Blood Group": data.get('bloodGroup'),
        "Age": data.get('age'), 
        "Work / Occupation": data.get('occupation'),
        "Allergies": data.get('allergies'),
        "Spoken Languages": languages,
        "Permanent Address": data.get('permanentAddress'),
        "Current Address": data.get('currentAddress'),
        "Employer Name": data.get('employerName'),
        "Employer Phone": data.get('employerPhone'),
        "Vaccinations info": vaccinations_info
    }

    # Use the defined CSV_FILE_PATH variable
    csv_file_path = CSV_FILE_PATH 

    try:
        file_exists = os.path.exists(csv_file_path)
        
        # Read existing data
        rows = []
        is_user_found = False
        if file_exists:
            with open(csv_file_path, 'r', newline='') as infile:
                reader = csv.DictReader(infile, fieldnames=fieldnames)
                header = next(reader, None)
                if header and header.get("Name") == "Name":
                    pass
                else:
                    infile.seek(0)
                
                for row in reader:
                    if row.get('ABHA ID') == username:
                        rows.append(new_row) # Replace existing row
                        is_user_found = True
                    elif row.get('ABHA ID'):
                        rows.append(row) # Keep other users' rows
        
        if not is_user_found:
            rows.append(new_row) # Append new user if not found

        # Write all data back to the CSV
        with open(csv_file_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return jsonify({"status": "success", "message": "Profile saved successfully!"})

    except Exception as e:
        print(f"Error saving profile data: {e}")
        return jsonify({"status": "error", "message": "Failed to save profile on the server."}), 500


# --- MOCK API ENDPOINTS (Continued) ---
@app.route('/api/patient-family/<username>', methods=['GET'])
def get_patient_family(username):
    """Returns mock data for the patient's family/emergency contacts."""
    mock_family_data = [
        {'Name': 'Priya Sneghal', 'Profile_Type': 'Wife'},
        {'Name': 'Emergency Contact', 'Profile_Type': 'Friend'}
    ]
    return jsonify(mock_family_data) 

# ==========================================================
# *** APPOINTMENT ROUTE (REPLACING PLACEHOLDER) ***
@app.route('/api/schedule-appointment', methods=['POST'])
def schedule_appointment():
    """Handles appointment scheduling request from the Patient dashboard."""
    data = request.json

    from_id = data.get('patientID')
    to_id = data.get('doctorID')
    date = data.get('date')
    time = data.get('time')
    reason = data.get('reason')
    priority = data.get('priority')

    if not all([from_id, to_id, date, time, reason]):
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    # Call the core appointment function
    result = send_application(from_id, to_id, date, time, reason, priority)

    if result.get('success'):
        return jsonify({"status": "success", "message": result['message']}), 200
    else:
        return jsonify({"status": "error", "message": result['error']}), 400
# ==========================================================


@app.route('/api/abha-chat', methods=['POST'])
def abha_chat():
    """Proxies the request to the dedicated FastAPI chatbot service running on port 8000."""
    
    data = request.json
    user_message = data.get('query') 

    if not user_message:
        return jsonify({"status": "error", "reply": "No message provided. Please type a query."}), 400

    try:
        response = requests.post(
            CHATBOT_URL, 
            data={'user_text': user_message}
        )

        if response.status_code == 200:
            ai_response_html = response.text
            start_tag = "<pre>"
            end_tag = "</pre>"
            
            if start_tag in ai_response_html and end_tag in ai_response_html:
                start_index = ai_response_html.find(start_tag) + len(start_tag)
                end_index = ai_response_html.find(end_tag)
                ai_response_text = ai_response_html[start_index:end_index].strip()
            else:
                ai_response_text = "Error: Could not parse AI response from FastAPI."

            return jsonify({"status": "success", "reply": ai_response_text})
        else:
            return jsonify({"status": "error", "reply": f"ABHA AI (FastAPI) error: Status {response.status_code}"}), 502
            
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "reply": "⚠️ Connection Failed: Start final.py service on port 8000."}), 503
    
    except Exception as e:
        print(f"Error during API call: {e}")
        return jsonify({"status": "error", "reply": f"An unexpected error in Flask: {str(e)}"}), 500

# --- API ENDPOINT FOR DOCTOR DATA ---
@app.route('/api/doctor-data/<username>', methods=['GET'])
def get_doctor_data(username):
    # ... (Your existing doctor data logic) ...
    csv_file_path = os.path.join(os.path.dirname(__file__), 'doctors.csv')
    try:
        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("ABHA ID") == username:
                    return jsonify({
                        'name': row.get('name', 'Doctor'),
                        'username': username,
                        'user_type': 'Doctor',
                        'specialization': row.get('specialization', 'General')
                    })
        return jsonify({
            'name': 'Not Found', 
            'username': username, 
            'user_type': 'Doctor', 
            'specialization': 'Unknown'
        })
    except Exception:
        return jsonify({'error': 'CSV read failed'}), 500

# ==========================================================
# --- PRESCRIPTION ROUTES ---
# ==========================================================

@app.route("/api/generate-prescription", methods=["POST"])
def api_generate_prescription():
    # 'generate_prescription' is already imported at the top of main.py
    import json
    
    doctor_id = request.form.get("doctor_id")
    patient_id = request.form.get("patient_id")
    medicines_json = request.form.get("medicines")
    date = request.form.get("date")
    time = request.form.get("time")

    try:
        medicines = json.loads(medicines_json)
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid medicines format"}), 400

    # Call the prescription logic
    result = generate_prescription(doctor_id, patient_id, date, time, medicines)

    # --- CRITICAL REDIRECTION LOGIC ADDED HERE ---
    if result.get("success") == True:
        # Construct the URL for the Patient Dashboard
        redirect_path = f"/patientdash.html?user={patient_id}"
        
        return jsonify({
            "success": True, 
            "message": "Prescription finalized and sent.",
            "redirect_url": redirect_path 
        })
    else:
        # Return error result from the prescription function
        return jsonify(result), 400


@app.route("/api/get-prescriptions/<patient_id>", methods=["GET"])
def api_get_prescriptions(patient_id):
    # 'get_prescriptions' is imported at the top
    return jsonify(get_prescriptions(patient_id))

@app.route("/api/download-prescription/<file_name>", methods=["GET"])
def api_download_prescription(file_name):
    # 'download_prescription' is imported at the top
    path = download_prescription(file_name) 
    
    if isinstance(path, dict):  # error returned from download_prescription
        return jsonify(path), 400
        
    # Serve the file from the correct absolute directory
    return send_from_directory(BACKEND_DIR, os.path.basename(path), as_attachment=True)


@app.route('/api/patient-prescriptions/<abha_id>', methods=['GET'])
def api_get_patient_prescriptions(abha_id):
    # This route uses the 'get_prescriptions' function imported from the backend file.
    return jsonify(get_prescriptions(abha_id))


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')


