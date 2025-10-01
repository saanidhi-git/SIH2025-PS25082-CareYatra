import os
import shutil
import PyPDF2
from tkinter import Tk, filedialog



    # Open file dialog to select PDF or Image

def option_function():

        # Folder to store uploaded files
    SAVE_FOLDER = "uploaded_pdfs"

    # Create folder if it doesn't exist
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    # Hide the root Tkinter window
    Tk().withdraw()
    print("Select the mode of entering the document/ file")
    print("1. Upload PDF/Image from local system"
          "\n2. Capture Image using Webcam")
    a = int(input("Enter 1 or 2: "))
    if a == 1:
        print("You chose to upload a file from your local system.")


        # Open file dialog to select PDF or Image
        file_path = filedialog.askopenfilename(
        title="Select a PDF or Image file",
        filetypes=[("PDF or Image Files", "*.pdf;*.jpg;*.jpeg;*.png")]
)
        if file_path:
            # Extract original filename
            filename = os.path.basename(file_path)

            # Define destination path
            dest_path = os.path.join(SAVE_FOLDER, filename)

            # Save a copy in the folder
            shutil.copy(file_path, dest_path)
            print(f"✅ File saved as {dest_path}\n")

            # Check file type
            if filename.lower().endswith(".pdf"):
                # Open and read the PDF
                with open(dest_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    print(f"Opened PDF: {dest_path}")
                    print(f"Pages: {len(reader.pages)}\n")

                    # Print first page text
                    if reader.pages:
                        print("--- Page 1 ---")

                        print(reader.pages[0].extract_text())
                    else:
                        print("⚠️ No text found in this PDF")
            elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
                print(f"🖼️ Image uploaded successfully: {filename}")
                print("⚡ Currently saving image only (no text extraction).")
            else:
                print("❌ Unsupported file type.")
        else:
            print("No file selected.")
    elif a == 2:
        print("You chose to capture an image using the webcam.")
        print("⚡ Feature coming soon!")

    else:
        print("❌ Invalid choice. Please enter 1 or 2.")    

option_function()
import os