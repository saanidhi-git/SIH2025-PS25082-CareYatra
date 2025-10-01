import csv
import hashlib
import os
import shutil

# ----------------------------
# Helper Functions
# ----------------------------
def hash_password(password: str) -> str:
    """Return a SHA256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_files():
    """Initialize CSV files if they don't exist"""
    if not os.path.exists("patients.csv"):
        with open("patients.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "name", "age", "doctor_assigned", "family_contact"])

    if not os.path.exists("doctors.csv"):
        with open("doctors.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "name", "specialization"])

    if not os.path.exists("documents"):
        os.makedirs("documents/patient_uploads", exist_ok=True)
        os.makedirs("documents/doctor_uploads", exist_ok=True)


# ----------------------------
# Signup Logic
# ----------------------------
def signup(user_type: str, username: str, password: str, **kwargs) -> str:
    filename = "patients.csv" if user_type == "patient" else "doctors.csv"

    # Check if user already exists
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return f"❌ {user_type.capitalize()} with this username already exists."

    # Store new user
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if user_type == "patient":
            writer.writerow([
                username, hash_password(password),
                kwargs.get("name", ""), kwargs.get("age", ""),
                kwargs.get("doctor_assigned", ""), kwargs.get("family_contact", "")
            ])
        else:  # doctor
            writer.writerow([
                username, hash_password(password),
                kwargs.get("name", ""), kwargs.get("specialization", "")
            ])

    return f"✅ {user_type.capitalize()} registered successfully."


# ----------------------------
# Login Logic
# ----------------------------
def login(user_type: str, username: str, password: str):
    filename = "patients.csv" if user_type == "patient" else "doctors.csv"
    hashed_pw = hash_password(password)

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == hashed_pw:
                print(f"✅ {user_type.capitalize()} login successful. Welcome {row['name']}!")
                return row  # Return user details
    print(f"❌ Invalid username or password for {user_type}.")
    return None


# ----------------------------
# Patient Home Page Features
# ----------------------------
def emergency_notify(patient_data):
    """Simulate emergency notification"""
    print(f"🚨 Emergency! Notifying Doctor: {patient_data['doctor_assigned']} and Family: {patient_data['family_contact']}")

def view_new_documents(patient_username):
    """View doctor-uploaded documents for the patient"""
    doc_dir = f"documents/doctor_uploads/{patient_username}"
    if not os.path.exists(doc_dir):
        print("📂 No documents uploaded by doctor yet.")
        return
    docs = os.listdir(doc_dir)
    if not docs:
        print("📂 No new documents available.")
    else:
        print("📑 Documents from Doctor:")
        for d in docs:
            print("   -", d)

def upload_new_document(patient_username, file_path):
    """Patient uploads a new document"""
    if not os.path.exists(file_path):
        print("❌ File does not exist on your device.")
        return
    dest_dir = f"documents/patient_uploads/{patient_username}"
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(file_path, dest_dir)
    print(f"✅ Document '{os.path.basename(file_path)}' uploaded successfully.")


def patient_home(patient_data):
    """Main menu for patient after login"""
    while True:
        print("\n🏠 Patient Home Page")
        print("1. Emergency notify doctor/family")
        print("2. View new documents (from doctor)")
        print("3. Upload new document")
        print("4. Logout")

        choice = input("Select an option (1-4): ")

        if choice == "1":
            emergency_notify(patient_data)
        elif choice == "2":
            view_new_documents(patient_data["username"])
        elif choice == "3":
            file_path = input("Enter full file path to upload: ")
            upload_new_document(patient_data["username"], file_path)
        elif choice == "4":
            print("👋 Logged out successfully.")
            break
        else:
            print("❌ Invalid choice, try again.")


# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    init_files()

    # Register patient & doctor (only first time)
    # print(signup("doctor", "drsmith", "docpass", name="Dr. Smith", specialization="Cardiology"))
    # print(signup("patient", "john123", "mypassword", name="John Doe", age=30, doctor_assigned="drsmith", family_contact="9998887777"))

    # Login as patient
    patient = login("patient", "john123", "mypassword")
    if patient:
        patient_home(patient)
