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


capture_image()


