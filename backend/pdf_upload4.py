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





































































def option_function():
    SAVE_FOLDER = "uploaded_pdfs"
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

option_function()

