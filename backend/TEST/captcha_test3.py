import os
import random
from captcha.image import ImageCaptcha

def generate_and_save_captcha(save_folder="captchas", length=5):
    # Characters to use for captcha
    CHAR_SET = "ABCDEFGHJKLMNPQRSTUVWXYZ2346789"
    
    # Generate random captcha text
    captcha_text = ''.join(random.choice(CHAR_SET) for _ in range(length))
    
    # Make sure folder exists
    os.makedirs(save_folder, exist_ok=True)
    
    # File name with captcha text
    filename = os.path.join(save_folder, f"CAPTCHA.png")
    
    # Generate captcha image
    image = ImageCaptcha(width=250, height=100)
    image.write(captcha_text, filename)
    
    print(f"✅ Captcha text: {captcha_text}")
    print(f"📂 Saved at: {filename}")

if __name__ == "__main__":
    generate_and_save_captcha()

