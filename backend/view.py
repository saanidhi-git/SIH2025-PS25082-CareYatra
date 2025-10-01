import os

def list_documents(main_folder):
    # Loop through all subfolders
    for subfolder in os.listdir(main_folder):
        subfolder_path = os.path.join(main_folder, subfolder)

        # Check if it's actually a folder
        if os.path.isdir(subfolder_path):
            print(f"\n📂 Documents for {subfolder}:")
            
            # List all files inside the subfolder
            for file in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, file)

                # Only list documents (pdf, docx, txt, etc.)
                if os.path.isfile(file_path) and file.lower().endswith(('.pdf', '.docx', '.txt')):
                    print("   -", file)


# Example usage
if __name__ == "__main__":
    main_folder = "C:\Users\as\Desktop\care_yatra\CARE_YATRA_SERVER\uploads"   # change this to your main folder name
    list_documents(main_folder)
