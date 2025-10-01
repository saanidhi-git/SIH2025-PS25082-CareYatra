import os
import shutil

def upload_file(username):
    # Step 1: Ask for username
    # username = input("Enter your username: ").strip()
    
    if not username:
        print("⚠️ Username cannot be empty!")
        return

    # Step 2: Create folder for that username
    user_folder = os.path.join("users_data", username)
    os.makedirs(user_folder, exist_ok=True)
    print(f"📂 Folder created/verified: {user_folder}")

    # Step 3: Ask user for file path
    file_path = input("Enter full path to your file (PDF or Image): ").strip()

    if not os.path.isfile(file_path):
        print("❌ Invalid file path! Please provide a valid file.")
        return

    # Step 4: Check file type (PDF or Image)
    allowed_extensions = (".pdf", ".jpg", ".jpeg", ".png")
    if not file_path.lower().endswith(allowed_extensions):
        print("❌ Unsupported file type! Only PDF, JPG, JPEG, PNG allowed.")
        print('try again with a valid file.')
        file_path = input("Enter full path to your file (PDF or Image): ").strip()
        return

    # Step 5: Save file inside the user folder
    filename = os.path.basename(file_path)
    dest_path = os.path.join(user_folder, filename)
    shutil.copy(file_path, dest_path)

    print(f"✅ File uploaded successfully!\nSaved at: {dest_path}")

if __name__ == "__main__":
    upload_file()
