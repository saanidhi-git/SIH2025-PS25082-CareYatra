import os
import shutil
from tkinter import Tk, filedialog

def upload_pdf():
    # Step 1: Ask for username
    username = input("Enter your username: ").strip()
    
    if not username:
        print("⚠️ Username cannot be empty!")
        return

    # Step 2: Create folder for that username
    user_folder = os.path.join("users_data", username)
    os.makedirs(user_folder, exist_ok=True)
    print(f"📂 Folder created/verified: {user_folder}")

    # Step 3: Open file dialog to pick PDF
    Tk().withdraw()  # Hide Tkinter root window
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not pdf_path:
        print("❌ No file selected.")
        return

    # Step 4: Save PDF inside the user folder
    filename = os.path.basename(pdf_path)
    dest_path = os.path.join(user_folder, filename)
    shutil.copy(pdf_path, dest_path)

    print(f"✅ PDF uploaded successfully!\nSaved at: {dest_path}")

if __name__ == "__main__":
    upload_pdf()
