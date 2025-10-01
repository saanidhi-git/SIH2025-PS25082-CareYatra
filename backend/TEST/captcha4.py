import os
import random
from captcha.image import ImageCaptcha
from PIL import Image

def generate_and_save_captcha(save_folder="captchas", length=5):
    # Allowed characters (avoiding confusing ones like 0/O, 1/I)
    CHAR_SET = "ABCDEFGHJKLMNPQRSTUVWXYZ2346789"
    
    # Generate random captcha text
    captcha_text = ''.join(random.choice(CHAR_SET) for _ in range(length))
    
    # Ensure folder exists
    os.makedirs(save_folder, exist_ok=True)
    
    # File path (store with text in filename)
    filename = os.path.join(save_folder, f"{captcha_text}.png")
    
    # Generate captcha image
    image = ImageCaptcha(width=250, height=100)
    image.write(captcha_text, filename)
    
    print(f"✅ Captcha text generated (hidden from user).")
    print(f"📂 Captcha saved at: {filename}")
    
    # Open the image in the default viewer
    img = Image.open(filename)
    img.show()
    
    return captcha_text

def verify_captcha(captcha_text):
    user_input = input("🔎 Enter the text you see in the captcha: ").strip().upper()
    if user_input == captcha_text:
        print("✅ Verification successful!")
    else:
        print("❌ Verification failed. Correct text was:", captcha_text)

if __name__ == "__main__":
    text = generate_and_save_captcha()
    verify_captcha(text)

