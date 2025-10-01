import os
import PyPDF2
from PIL import Image
import pytesseract

# Folders
UPLOAD_FOLDER = "uploaded_pdfs"

# Clinic categories with keywords
CATEGORIES = {
    "Dentist": ["tooth", "teeth", "dental", "cavity", "braces", "root canal"],
    "Ophthalmologist": ["eye", "vision", "ophthalmology", "cataract", "lens", "glasses",
                        "retina", "macula",'optical'],
    "Dermatologist": ["skin", "acne", "eczema", "dermatology", "allergy", "psoriasis"],
    "Orthopedic": ["bone", "joint", "orthopedic", "fracture", "arthritis", "spine"],
    "General": ["fever", "cough", "cold", "general", "checkup", "health", "medicine"]
}

# Extract text from PDF
def extract_text_from_pdf(filepath):
    try:
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.lower()
    except Exception as e:
        return ""

# Extract text from Image
def extract_text_from_image(filepath):
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return text.lower()
    except Exception as e:
        return ""

# Categorize based on text
def categorize_text(text):
    for category, keywords in CATEGORIES.items():
        if any(word in text for word in keywords):
            return category
    return "Uncategorized"

def main():
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"⚠️ Folder '{UPLOAD_FOLDER}' not found.")
        return

    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        print("⚠️ No files found in uploaded_files/")
        return

    print("\n📂 Categorizing uploaded files...\n")
    for f in files:
        filepath = os.path.join(UPLOAD_FOLDER, f)
        text = ""

        if f.lower().endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
        elif f.lower().endswith((".jpg", ".jpeg", ".png")):
            text = extract_text_from_image(filepath)

        if text:
            category = categorize_text(text)
        else:
            category = "Uncategorized"

        print(f"📄 {f}  →  🏥 {category}")

if __name__ == "__main__":
    main()



















