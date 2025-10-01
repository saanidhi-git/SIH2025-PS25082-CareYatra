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

# Run function
save_captured_image()
