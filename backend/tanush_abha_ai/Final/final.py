import os
import PyPDF2
import easyocr
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import ollama
from pdf2image import convert_from_path

# ===============================
# Setup
# ===============================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="CareYatra - Health Data Summarizer + Chatbot")

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'])

# ===============================
# Helpers
# ===============================
def extract_text_from_pdf(path: str) -> str:
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
    try:
        results = reader.readtext(path, detail=0, paragraph=True)
        return "\n".join(results).strip()
    except Exception as e:
        return f"[OCR Error] {str(e)}"

def chat_with_ai(prompt: str) -> str:
    if not prompt.strip():
        return "⚠️ No text provided."
    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are Abha, a highly professional DNA and Healthcare AI assistant. Summarize medical reports, answer queries, and provide accurate information."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.get("message", {}).get("content", "⚠️ Couldn’t generate a response.")
    except Exception as e:
        return f"[!] Error talking to Ollama: {e}"

# ===============================
# HTML / Frontend
# ===============================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CareYatra - Health Data Summarizer + Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin:0; padding:20px; background: linear-gradient(135deg, #add8e6, #ffffe0); text-align:center; }
            h2 { color:#004466; margin-top:20px; }
            form { margin:20px auto; padding:20px; border:2px dashed #004466; width:450px; background:white; border-radius:12px; }
            input[type=file], textarea { margin:15px 0; width:90%; padding:10px; border-radius:6px; border:1px solid #ccc; }
            button { padding:10px 20px; background:#004466; color:white; border:none; border-radius:8px; cursor:pointer; margin:5px; }
            button:hover { background:#006699; }
        </style>
    </head>
    <body>
        <h2>CareYatra - Health Data Summarizer + Chatbot</h2>

        <!-- File Upload -->
        <form action="/upload" method="post" enctype="multipart/form-data">
            <h3>Upload File</h3>
            <input type="file" name="file" required>
            <br>
            <button type="submit">Upload & Summarize</button>
        </form>

        <!-- Text Chat -->
        <form id="text-chat-form">
            <h3>Text Chat / Paste Report</h3>
            <textarea id="user_text" rows="4" placeholder="Type or paste report here..." required></textarea><br>
            <button type="submit">Send</button>
        </form>

        <!-- Live Voice Chat -->
        <div>
            <h3>🎤 Live Voice Chat</h3>
            <button id="start-voice">Start Talking</button>
            <textarea id="voice-text" rows="4" placeholder="Your speech will appear here..."></textarea><br>
            <button id="send-voice">Send Voice</button>
        </div>

        <div id="ai-response" style="margin-top:20px; white-space:pre-wrap; background:#eef; padding:15px; border-radius:10px;"></div>

        <script>
            // -----------------------
            // Text Chat
            // -----------------------
            document.getElementById("text-chat-form").onsubmit = async function(e) {
                e.preventDefault();
                const user_text = document.getElementById("user_text").value;
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({ user_text })
                });
                const html = await response.text();
                document.getElementById("ai-response").innerHTML = html;
            };

            // -----------------------
            // Live Voice Input
            // -----------------------
            let recognition;
            if ("webkitSpeechRecognition" in window) {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = "en-US";

                recognition.onresult = (event) => {
                    let transcript = "";
                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        transcript += event.results[i][0].transcript;
                    }
                    document.getElementById("voice-text").value = transcript;
                };
            } else {
                alert("Your browser does not support live voice recognition.");
            }

            document.getElementById("start-voice").onclick = () => {
                if (recognition) recognition.start();
            };

            document.getElementById("send-voice").onclick = async () => {
                const voice_text = document.getElementById("voice-text").value;
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({ user_text: voice_text })
                });
                const html = await response.text();
                document.getElementById("ai-response").innerHTML = html;

                // Text-to-speech using browser API
                const aiText = html.replace(/<[^>]+>/g, '');
                const utterance = new SpeechSynthesisUtterance(aiText);
                speechSynthesis.speak(utterance);
            };
        </script>
    </body>
    </html>
    """

# ===============================
# File Upload + Summarization
# ===============================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            extracted = extract_text_from_pdf(filepath)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
            extracted = extract_text_from_image(filepath)
        else:
            return HTMLResponse(f"<h3>⚠️ Unsupported format: {filename}</h3>", status_code=400)

        summary = chat_with_ai(f"Please summarize this medical report:\n\n{extracted}")

        return HTMLResponse(f"<pre>{summary}</pre>")
    except Exception as e:
        return HTMLResponse(f"<h3>Internal Error</h3><pre>{str(e)}</pre>", status_code=500)

# ===============================
# Chat Endpoint
# ===============================
@app.post("/chat")
async def chat(user_text: str = Form(...)):
    response = chat_with_ai(user_text)
    return HTMLResponse(f"<pre>{response}</pre>")

# In your final.py, add this line at the very end:

# Add this line to make the file importable without running FastAPI/Ollama logic
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
