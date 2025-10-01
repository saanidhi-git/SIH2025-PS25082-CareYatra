from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import json
import os


DOCTOR_NAMES = {
    "11133399": "Dr. Raj",
    "111333999": "Dr. Raj ", # Using the ID from your logs
    # Add other doctor IDs/names here as needed
}

# Define the directory where this script resides (the 'backend' folder)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the backend directory
PRESCRIPTION_FILE = os.path.join(BASE_DIR, "prescription.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "prescription.jpg")

# Ensure prescriptions JSON file exists
if not os.path.exists(PRESCRIPTION_FILE):
    with open(PRESCRIPTION_FILE, "w") as f:
        json.dump([], f)

# ---------------- UTILITY FUNCTIONS ----------------
def load_prescriptions():
    """Loads prescription data from the JSON file."""
    # Uses the corrected path PRESCRIPTION_FILE
    with open(PRESCRIPTION_FILE, "r") as f:
        return json.load(f)

def save_prescriptions(data):
    """Saves prescription data to the JSON file."""
    # Uses the corrected path PRESCRIPTION_FILE
    with open(PRESCRIPTION_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- PRESCRIPTION GENERATION ----------------
def generate_prescription(doctor_id: str, patient_id: str, date: str, time: str, medicines: list):
    """Generates the prescription image, saves the file, and updates the JSON record."""
    
    # Flexible: accept any doctor HPR ID and patient ABHA ID
    
  

    doctor_name = DOCTOR_NAMES.get(doctor_id, f"Doctor {doctor_id}")
    patient_name = f"Patient {patient_id}"

    # Load template or create blank
    if os.path.exists(TEMPLATE_PATH):
        img = Image.open(TEMPLATE_PATH)
    else:
        img = Image.new("RGB", (800, 800), "white")

    draw = ImageDraw.Draw(img)
    try:
        header_font = ImageFont.truetype("arial.ttf", 24)
        font = ImageFont.truetype("arial.ttf", 20)
        small_font = ImageFont.truetype("arial.ttf", 18)
        bold_font = ImageFont.truetype("arialbd.ttf", 20)
    except:
        # Fallback to default font
        header_font = font = small_font = bold_font = ImageFont.load_default()

    # Header
    draw.text((40, 40), f"Patient ID: {patient_id}", font=header_font, fill="black")
    draw.text((40, 80), f"Doctor: {doctor_name}", font=font, fill="black")
    draw.text((40, 120), f"Date: {date}  Time: {time}", font=font, fill="black")

    # Medicines
    start_y = 180
    line_height = 50
    sr_x, name_x, desc_x, dosage_x = 40, 80, 300, 650
    for idx, med in enumerate(medicines):
        y = start_y + idx * line_height
        draw.text((sr_x, y), str(idx + 1), font=font, fill="black")
        draw.text((name_x, y), med['name'], font=bold_font, fill="black")
        if med.get('description'):
            draw.text((desc_x, y), med['description'], font=small_font, fill="gray")
        draw.text((dosage_x, y), med['dosage'], font=font, fill="black")

    # Footer
    draw.text((40, 700), f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M %p')}", font=font, fill="black")

    # Save file to the backend directory
    file_name_only = f"{patient_id}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.jpg"
    file_path = os.path.join(BASE_DIR, file_name_only)
    img.save(file_path)

    # Save to prescriptions.json
    all_presc = load_prescriptions()
    all_presc.append({
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "date": date,
        "time": time,
        "medicines": medicines,
        "file": file_name_only # Store just the filename
    })
    save_prescriptions(all_presc)

    return {"success": True, "file": file_name_only}

# ---------------- FETCH PRESCRIPTIONS ----------------
def get_prescriptions(patient_id: str):
    """Filters and returns prescriptions for a specific patient."""
    all_presc = load_prescriptions()
    return [p for p in all_presc if p['patient_id'] == patient_id]

# ---------------- DOWNLOAD FILE ----------------
# ---------------- DOWNLOAD FILE ----------------
'''def download_prescription(file_name: str):
    """Returns the full path to the prescription file for Flask's send_from_directory."""
    
    # 1. Construct the ABSOLUTE path where the file SHOULD be located
    file_path = os.path.join(BASE_DIR, file_name)
    
    # 2. Check if the file physically exists at that path
    if os.path.exists(file_path):
        # If found, return the absolute path
        return file_path
        
    # 3. If not found, return an error dictionary
    print(f"Error: File not found at path: {file_path}") # CHECK YOUR SERVER CONSOLE FOR THIS MESSAGE
    return {"error": "File not found"}'''

def download_prescription(file_name: str):
    """Returns the full path to the prescription file for Flask's send_from_directory."""
    
    # 1. Construct the ABSOLUTE path where the file SHOULD be located
    file_path = os.path.join(BASE_DIR, file_name)
    
    # 2. Normalize the path (Crucial step for Windows/path consistency!)
    normalized_path = os.path.normpath(file_path)
    
    # 3. Print the path being checked for debugging
    print(f"Checking for file at: {normalized_path}") 
    
    # 4. Check if the file physically exists at that normalized path
    if os.path.exists(normalized_path):
        # If found, return the normalized path
        return normalized_path
        
    # 5. If not found, return an error dictionary
    print(f"ERROR: File not found after check at: {normalized_path}")
    return {"error": "File not found"}

# ---------------- EXAMPLE USAGE ----------------
if __name__ == "__main__":
    # Example HPR/ABHA IDs
    doctor_hpr = "11133399"
    patient_abha = "111333444"

    # Generate prescription
    meds = [
        {"name": "Paracetamol", "description": "For fever", "dosage": "1-0-1"},
        {"name": "Cough Syrup", "description": "", "dosage": "10ml twice a day"}
    ]
    # Note: This local test run will likely fail on the "arial.ttf" font file path.
    result = generate_prescription(doctor_hpr, patient_abha, "30-09-2025", "14:00", meds)
    print(result)

    # Fetch prescriptions
    presc = get_prescriptions(patient_abha)
    print(json.dumps(presc, indent=4))

    # Download file
    if "file" in result:
        print("Prescription saved at:", download_prescription(result["file"]))
