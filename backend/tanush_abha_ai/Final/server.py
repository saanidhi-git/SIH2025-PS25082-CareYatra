import os
import PyPDF2
import easyocr
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import ollama
from pdf2image import convert_from_path

# ===============================
# Setup
# ===============================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="CareYatra - Healthcare Document Summarizer (EasyOCR + LLaMA 3.2-3B)")

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'])  # You can add multiple langs like ['en','hi'] if needed

# ===============================
# Helpers
# ===============================
def extract_text_from_pdf(path: str) -> str:
    """Extract text from a PDF (tries PyPDF2 first, then OCR with EasyOCR)."""
    text = ""
    try:
        with open(path, "rb") as f:
            reader_pdf = PyPDF2.PdfReader(f)
            for page in reader_pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass

    # If no text, fallback to OCR
    if not text.strip():
        try:
            pages = convert_from_path(path)
            for page_img in pages:
                results = reader.readtext(page_img, detail=0, paragraph=True)
                text += "\n".join(results) + "\n"
        except Exception as e:
            return f"[OCR Error] {str(e)}"
    return text.strip()

def extract_text_from_image(path: str) -> str:
    """Run OCR on an image file using EasyOCR."""
    try:
        results = reader.readtext(path, detail=0, paragraph=True)
        return "\n".join(results).strip()
    except Exception as e:
        return f"[OCR Error] {str(e)}"

def summarize_text_with_ai(text: str) -> str:
    """Send extracted text to Ollama (using llama3.2:3b) for summarization."""
    if not text.strip():
        return "⚠️ No readable text found inside this document."
    if text.lower().startswith("[ocr error]"):
        return f"⚠️ Could not process document: {text}"
    try:
        response = ollama.chat(
            model="llama3.2:3b",  # lightweight, CPU-friendly model
            messages=[
                {"role": "system", "content": "You are Abha, a Healthcare AI assistant. Summarise uploaded medical documents clearly, concisely, and with focus on patient context."},
                {"role": "user", "content": f"Please summarize this medical document:\n\n{text}"}
            ]
        )
        return response.get("message", {}).get("content", "⚠️ Couldn’t generate a summary from the model.")
    except Exception as e:
        return f"[!] Error talking to Ollama: {e}"

# ===============================
# Root HTML form
# ===============================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CareYatra File Upload</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f5f5f5; text-align:center; padding:50px; }
            h2 { color:#008080; }
            form { margin:20px auto; padding:20px; border:2px dashed #008080;
                   width:400px; background:white; border-radius:8px; }
            input[type=file] { margin:15px 0; }
            button { padding:10px 20px; background:#008080; color:white; border:none; border-radius:5px; cursor:pointer; }
        </style>
    </head>
    <body>
        <h2>🌟 CareYatra - Upload Your Medical Document</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br><br>
            <button type="submit">Upload & Summarize</button>
        </form>
    </body>
    </html>
    """

# ===============================
# File upload + summarization
# ===============================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        # Detect extension
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            extracted = extract_text_from_pdf(filepath)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
            extracted = extract_text_from_image(filepath)
        else:
            return HTMLResponse(f"<h3>⚠️ Unsupported format: {filename}</h3>", status_code=400)

        # Summarize
        summary = summarize_text_with_ai(extracted)

        return HTMLResponse(f"""
        <html>
        <body style="font-family:Arial; padding:20px;">
            <h2>📄 Summary of {filename}</h2>
            <div style="white-space:pre-wrap; background:#eef; padding:15px; border-radius:10px;">
                {summary}
            </div>
            <br>
            <a href="/">⬅️ Upload another file</a>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"<h3>🔥 Internal Error</h3><pre>{str(e)}</pre>", status_code=500)