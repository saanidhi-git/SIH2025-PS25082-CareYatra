import os


data = input("pateint name: ")
# FOLDER_INPUT = f"users_data/{data}"
# # Folders to check
# PDF_FOLDER = "uploaded_pdfs"
# FILES_FOLDER = "uploaded_files"

PDF_FOLDER = f"users_data/{data}"
FILES_FOLDER = f"users_data/{data}"

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
