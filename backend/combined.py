import csv
import hashlib
import os
import shutil

import PyPDF2
from tkinter import Tk, filedialog


def captcha123():
    from captcha.image import ImageCaptcha
    import random, uuid, os

    # Store captchas in memory {id: text}
    captcha_store = {}

    # Folder to save captcha images
    os.makedirs("captchas", exist_ok=True)

    # Character set (no confusing ones like O/0, I/1, 5/S)
    CHAR_SET = "ABCDEFGHJKLMNPQRSTUVWXYZ2346789"

    def generate_image_captcha():
        """Generate an image captcha"""
        captcha_text = ''.join(random.choices(CHAR_SET, k=4))
        captcha_id = str(uuid.uuid4())

        image = ImageCaptcha(width=200, height=80)
        filename = f"captchas/{captcha_id}.png"
        image.write(captcha_text, filename)

        captcha_store[captcha_id] = captcha_text
        return captcha_id, filename

    def verify_captcha(captcha_id, user_input):
        """Verify user input for captcha"""
        correct_text = captcha_store.get(captcha_id)
        if not correct_text:
            return False, "Captcha not found or expired!"

        # One-time use
        del captcha_store[captcha_id]
        try:
            os.remove(f"captchas/{captcha_id}.png")
        except FileNotFoundError:
            pass

        if user_input.upper() == correct_text:
            return True, "✅ Captcha verified!"
        else:
            return False, f"❌ Incorrect! Correct was {correct_text}"

    def generate_math_captcha():
        """Generate a simple math captcha"""
        a, b = random.randint(1, 9), random.randint(1, 9)
        return f"{a} + {b}", a + b

    # ---------------- MAIN TEST -----------------
    if __name__ == "__main__":
        cid, file = generate_image_captcha()
        print(f"Captcha created! Open the image: {file}")

        user_text = input("Enter captcha text (or type 'skip' if unreadable): ")

        if user_text.lower() == "skip":
            # Fallback to math captcha
            q, ans = generate_math_captcha()
            print("New Captcha:", q)
            try:
                user_ans = int(input("Your answer: "))
                if user_ans == ans:
                    print("✅ Captcha verified via math challenge!")
                else:
                    print(f"❌ Wrong! Correct answer was {ans}")
            except ValueError:
                print("❌ Invalid input!")
        else:
            # Normal image captcha verification
            status, msg = verify_captcha(cid, user_text)
            print(msg)

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
            writer.writerow(["ABHA ID: ", "password", "name", "specialization"])

    if not os.path.exists("documents"):
        os.makedirs("documents/patient_uploads", exist_ok=True)
        os.makedirs("documents/doctor_uploads", exist_ok=True)


# ----------------------------
# Signup Logic
# ----------------------------
def signup(user_type: str, username: str, password: str, **kwargs) -> str:
    filename = "patients.csv" if user_type == "patient" else "doctors.csv"

    # captcha123()

    # Check if user already exists
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ABHA ID"] == username:
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
            
            if row["ABHA ID"] == username and row["password"] == hashed_pw:
                captcha123()
                print(f"✅ {user_type.capitalize()} login successful. Welcome {row['name']}!")
                return row  # Return user details
    print(f"❌ Invalid username or password for {user_type}.")
    return None


# ----------------------------
# Patient Home Page Features
# ----------------------------
def emergency_notify(patient_data):
    """Simulate emergency notification"""
    doctor = patient_data.get("doctor_assigned", "Unknown Doctor")
    family = patient_data.get("family_contact", "Unknown Contact")
    print(f"🚨 Emergency! Notifying Doctor: {doctor} and Family: {family}")


def view_doc1(username):

    # username = input("pateint name: ")
    # FOLDER_INPUT = f"users_data/{data}"
    # # Folders to check
    # PDF_FOLDER = "uploaded_pdfs"
    # FILES_FOLDER = "uploaded_files"

    PDF_FOLDER = f"users_data/{username}"
    FILES_FOLDER = f"users_data/{username}"

    # Allowed image extensions
    IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")

    def list_files_in_folder(folder, exts=None):
        """List files in a folder, optionally filtering by extensions."""
        if not os.path.exists(folder):
            print(f"⚠️ Folder '{folder}' does not exist.")
            return []

        files = os.listdir(folder)
        if exts:
            files = [f for f in files if f.lower().endswith(exts)]

        return files

    def main():
        print("\n📂 Listing files from folders...\n")

        # List PDFs
        pdf_files = list_files_in_folder(PDF_FOLDER, exts=(".pdf",))
        print("📑 PDFs in 'uploaded_pdfs/':")
        if pdf_files:
            for i, f in enumerate(pdf_files, 1):
                print(f"  {i}. {f}")
        else:
            print("  ❌ No PDFs found.")

        # List PDFs + Images in uploaded_files
        print("\n🖼️ PDFs and Images in 'uploaded_files/':")
        files = list_files_in_folder(FILES_FOLDER, exts=(".pdf",) + IMAGE_EXTS)
        if files:
            for i, f in enumerate(files, 1):
                print(f"  {i}. {f}")
        else:
            print("  ❌ No PDFs or images found.")

    if __name__ == "__main__":
            main()


def upload_doc_coud():
    import cloud_app

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


import os
import shutil
import PyPDF2
from tkinter import Tk, filedialog

# import face_recognition as fr
import os

import shutil

def save_captured_image():
    # Ask user for their name
    user_name = input("Enter your name: ").strip()

    # Define base folder
    base_folder = "users_data"
    user_folder = os.path.join(base_folder, user_name)

    # Create folder if not exists
    os.makedirs(user_folder, exist_ok=True)

    # Source image
    src_image = "captured_img.jpg"

    # Check if source image exists
    if not os.path.exists(src_image):
        print(f"❌ Source image '{src_image}' not found.")
        return

    # Destination path
    dest_path = os.path.join(user_folder, src_image)

    # Copy image into user folder
    shutil.copy(src_image, dest_path)
    print(f"✅ Image saved to {dest_path}")


def capture_image():
    
    import cv2 
    import numpy as np


    cap = cv2.VideoCapture(0)

    if not cap:
        print('Error: could not open camera')
        exit

    ret, frame= cap.read()

    if not ret:
        print('failed to capture image')
        exit()

    cv2.imshow('Captured img: ',frame)

    cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()

    # save the captured image

    cv2.imwrite('captured_img.jpg',frame)
    print('Image captured and save as \'capture_img.jpg')

    # Run function
    save_captured_image()



def capture_image():
    
    import cv2 
    import numpy as np


    cap = cv2.VideoCapture(0)

    if not cap:
        print('Error: could not open camera')
        exit

    ret, frame= cap.read()

    if not ret:
        print('failed to capture image')
        exit()

    cv2.imshow('Captured img: ',frame)

    cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()

    # save the captured image

    cv2.imwrite('captured_img.jpg',frame)
    print('Image captured and save as \'capture_img.jpg')

    # Run function
    save_captured_image()
def option_function():
    name = input("Enter you name: ")
    SAVE_FOLDER = f"user_data/"+f'{name}'
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    Tk().withdraw()
    print("Select the mode of entering the document/ file")
    print("1. Upload PDF/Image from local system"
          "\n2. Capture Image using Webcam")
    a = int(input("Enter 1 or 2: "))

    if a == 1:
        print("You chose to upload a file from your local system.")
        file_path = filedialog.askopenfilename(
            title="Select a PDF or Image file",
            filetypes=[("PDF or Image Files", "*.pdf;*.jpg;*.jpeg;*.png")]
        )

        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(SAVE_FOLDER, filename)
            shutil.copy(file_path, dest_path)
            print(f"✅ File saved as {dest_path}\n")

            # Handle PDFs
            if filename.lower().endswith(".pdf"):
                try:
                    with open(dest_path, "rb") as file:
                        reader = PyPDF2.PdfReader(file)
                        print(f"Opened PDF: {dest_path}")
                        print(f"Pages: {len(reader.pages)}\n")

                        if reader.pages:
                            print("--- Page 1 ---")
                            print(reader.pages[0].extract_text())
                        else:
                            print("⚠️ No text found in this PDF")
                except PyPDF2.errors.PdfReadError as e:
                    print(f"❌ Error reading PDF: {e}")
            # Handle images
            elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
                print(f"🖼️ Image uploaded successfully: {filename}")
                print("⚡ Currently saving image only (no text extraction).")
            else:
                print("❌ Unsupported file type.")
        else:
            print("No file selected.")

    elif a == 2:
        print("You chose to capture an image using the webcam.")
        capture_image()
    else:
        print("❌ Invalid choice. Please enter 1 or 2.")    

           
def upload_new_document(patient_username, file_path):
    """Patient uploads a new document"""
    if not os.path.exists(file_path):
        print("❌ File does not exist on your device.")
        return
    dest_dir = f"documents/patient_uploads/{patient_username}"
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(file_path, dest_dir)
    print(f"✅ Document '{os.path.basename(file_path)}' uploaded successfully.")

import os
import webbrowser

def view1():
    import view

def view_cloud():
    # Run Streamlit app
    os.system("start streamlit run user_cloud_app.py")
    # Auto-open browser
    webbrowser.open("http://localhost:8501")
def open_upload_page():
    # Run Streamlit app
    os.system("start streamlit run user_cloud_app.py")
    # Auto-open browser
    webbrowser.open("http://localhost:8501")

def insurance():
     os.system("start streamlit run user_cloud_app.py")
    # Auto-open browser
     webbrowser.open("http://localhost:8501")

def my_family():
     FAMILY_FILE = "my_family.csv"
     def ensure_family_file():
        """Ensure the family file exists with proper headers."""
        if not os.path.exists(FAMILY_FILE):
            with open(FAMILY_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ABHA_ID", "Name", "Age", "Assigned_Doctor"])
            print(f"✅ Created {FAMILY_FILE}")

     def add_family_member():
        """Take user input and save family member details."""
        abha_id = input("Enter ABHA ID: ")
        name = input("Enter Name: ")
        age = input("Enter Age: ")
        doctor = input("Enter Assigned Doctor: ")

        # Save to CSV
        with open(FAMILY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([abha_id, name, age, doctor])

        print(f"✅ Family member '{name}' added successfully!")

     def main():
        ensure_family_file()
        add_family_member()

     if __name__ == "__main__":
        main()

def notification():
    from new_notif import app

def patient_home(patient_data):
    """Main menu for patient after login"""
    while True:
        print("\n🏠 Patient Home Page")
        print("1. Emergency notify doctor/family")
        print("2. View new documents (from doctor)")
        print("3. Upload new document")
        print('4. Insurance Section')
        print('5. Family account section')
        print('6. Notification')
        print('7. ABHA AI')
        print("8. Logout")

        choice = input("Select an option (1-4): ")

        if choice == "1":
            emergency_notify(patient_data)
        elif choice == "2":
            # view_doc1(username=patient_data["name"])
            # view_new_documents(patient_data["name"])
            view_cloud()
        elif choice == "3":
            open_upload_page()
            
        elif choice == '4':
            insurance()

        elif choice == '5':
            my_family()

        elif choice == '6':
            import appointment

            appointment.register_user()
            appointment.send_appointment("alice")

        elif choice == '7':
            import abha_ai

        elif choice == "8":
            print("👋 Logged out successfully.")
            break

        
        else:
            print("❌ Invalid choice, try again.")


# -----------------------------------------------------------
        # DOCTOR HOME PAGE

def doctor_homepage():
    """Main menu for patient after login"""
    while True:
        print("\n🏠 Patient Home Page")
        print("1. View Emergency notify ")
        print("2. View  documents (from doctor)")
        print("3. Upload new document for a pateint")
        print('4. Insurance Section')
        print('5. Family account section')
        print('6. Notification')
        print('7. ABHA AI')
        print("8. Logout")

        choice = input("Select an option (1-4): ")

        if choice == "1":
            emergency_notify()
        elif choice == "2":
            # view_doc1(username=patient_data["name"])
            # view_new_documents(patient_data["name"])
            view_cloud()
        elif choice == "3":
            open_upload_page()
            
        elif choice == '4':
            insurance()

        elif choice == '5':
            my_family()

        elif choice == '6':
            import appointment

            appointment.register_user()
            appointment.send_appointment("alice")

        elif choice == '7':
            import abha_ai

        elif choice == "8":
            print("👋 Logged out successfully.")
            break

        
        else:
            print("❌ Invalid choice, try again.")



# ----------------------------
# Main Program
# ----------------------------
if __name__ == "__main__":
    init_files()

    while True:
        print("\n=== Healthcare System ===")
        print("1. Signup as Patient")
        print("2. Signup as Doctor")
        print("3. Login as Patient")
        print("4. Login as Doctor")
        print("5. Exit")

        action = input("Choose option: ")

        if action == "1":
            captcha123()
            uname = input("ABHA ID: ")
            pw = input("Password: ")
            name = input("Name: ")
            age = input("Age: ")
            doctor = input("Assigned Doctor Username: ")
            family = input("Family Contact: ")
            print(signup("patient", uname, pw, name=name, age=age, doctor_assigned=doctor, family_contact=family))

        elif action == "2":
            captcha123()
            uname = input("ABHA ID: ")
            pw = input("Password: ")
            name = input("Name: ")
            spec = input("Specialization: ")
            print(signup("doctor", uname, pw, name=name, specialization=spec))

        elif action == "3":
            uname = input("ABHA ID: ")
            pw = input("Password: ")
            patient = login("patient", uname, pw)
            if patient:
                patient_home(patient)

        elif action == "4":
            uname = input("ABHA ID: ")
            pw = input("Password: ")
            doctor = login("doctor", uname, pw)
            # doctor_home(doctor) could be added later
            # For now, doctor just logs in
            if doctor:
                doctor_homepage()
                

        elif action == "5":
            print("Goodbye 👋")
            break
        else:
            print("❌ Invalid choice, try again.")

