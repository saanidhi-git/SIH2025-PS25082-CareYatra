from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import json
import os

# ---------------- DATA ----------------
users = {
    "d1": {"name": "Doctor Sharma", "role": "Doctor"},
    "p1": {"name": "Patient Rohan", "role": "Patient"},
}

PRESCRIPTION_FILE = "prescriptions.json"

if not os.path.exists(PRESCRIPTION_FILE):
    with open(PRESCRIPTION_FILE, "w") as f:
        json.dump([], f)

def load_prescriptions():
    with open(PRESCRIPTION_FILE, "r") as f:
        return json.load(f)

def save_prescriptions(data):
    with open(PRESCRIPTION_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- FASTAPI ----------------
app = FastAPI(title="Doctor-Patient Prescription System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------- HTML FRONTEND ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doctor-Patient Prescription System</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f4f7fb; color:#333; margin:0; padding:0; }
            header { background:#007acc; color:white; padding:20px; text-align:center; }
            .container { padding:20px; max-width:800px; margin:auto; }
            input, select { width:100%; padding:8px; margin:5px 0; border:1px solid #ccc; border-radius:4px; }
            button { background:#007acc; color:white; padding:10px 15px; border:none; border-radius:4px; cursor:pointer; }
            button:hover { background:#005fa3; }
            h2 { color:#007acc; }
            .presc { border-bottom:1px solid #ccc; padding:10px 0; }
        </style>
    </head>
    <body>
        <header><h1>Doctor-Patient Prescription System</h1></header>

        <div class="container" id="login_container">
            <h2>Login</h2>
            <label>Select Role:</label>
            <select id="role_select">
                <option value="Doctor">Doctor</option>
                <option value="Patient">Patient</option>
            </select>
            <label>Your ID:</label>
            <input type="text" id="user_id" placeholder="Enter your ID">
            <button onclick="login()">Login</button>
        </div>

        <div class="container" id="doctor_container" style="display:none;">
            <h2>Generate Prescription</h2>
            <form id="presc_form">
                <label>Patient ID:</label>
                <input type="text" id="patient_id" required>
                <label>Date (DD-MM-YYYY):</label>
                <input type="text" id="date" value="" required>
                <label>Time (HH:MM):</label>
                <input type="text" id="time" value="" required>
                <div id="medicines_container">
                    <h3>Medicines</h3>
                </div>
                <button type="button" onclick="addMedicine()">Add Medicine</button><br><br>
                <button type="submit">Generate & Send Prescription</button>
            </form>
            <button onclick="logout()">Logout</button>
        </div>

        <div class="container" id="patient_container" style="display:none;">
            <h2>Received Prescriptions</h2>
            <div id="prescriptions"></div>
            <button onclick="logout()">Logout</button>
        </div>

        <script>
            let currentUser = null;
            let currentRole = null;
            let medCount = 0;

            function login(){
                const uid = document.getElementById("user_id").value.trim();
                const role = document.getElementById("role_select").value;
                if(!uid){ alert("Enter ID"); return; }
                if(role === "Doctor" && uid !== "d1"){ alert("Invalid Doctor ID"); return; }
                if(role === "Patient" && uid !== "p1"){ alert("Invalid Patient ID"); return; }
                currentUser = uid; currentRole = role;
                document.getElementById("login_container").style.display="none";
                if(role==="Doctor"){ document.getElementById("doctor_container").style.display="block"; }
                else{ document.getElementById("patient_container").style.display="block"; fetchPrescriptions(); }
            }

            function logout(){
                currentUser = null; currentRole = null;
                document.getElementById("login_container").style.display="block";
                document.getElementById("doctor_container").style.display="none";
                document.getElementById("patient_container").style.display="none";
            }

            function addMedicine(){
                medCount++;
                const container = document.getElementById("medicines_container");
                const div = document.createElement("div");
                div.innerHTML = `
                    <label>Medicine ${medCount} Name:</label>
                    <input type="text" class="med_name" required>
                    <label>Description (optional):</label>
                    <input type="text" class="med_desc">
                    <label>Dosage:</label>
                    <input type="text" class="med_dosage" required>
                    <hr>`;
                container.appendChild(div);
            }

            document.getElementById("presc_form").onsubmit = async function(e){
                e.preventDefault();
                const patient_id = document.getElementById("patient_id").value.trim();
                const date = document.getElementById("date").value.trim();
                const time = document.getElementById("time").value.trim();
                const med_names = Array.from(document.getElementsByClassName("med_name")).map(e=>e.value.trim());
                const med_descs = Array.from(document.getElementsByClassName("med_desc")).map(e=>e.value.trim());
                const med_dosages = Array.from(document.getElementsByClassName("med_dosage")).map(e=>e.value.trim());

                let medicines = [];
                for(let i=0;i<med_names.length;i++){
                    medicines.push({name:med_names[i],description:med_descs[i],dosage:med_dosages[i]});
                }

                const payload = new FormData();
                payload.append("doctor_id", currentUser);
                payload.append("patient_id", patient_id);
                payload.append("date", date);
                payload.append("time", time);
                payload.append("medicines", JSON.stringify(medicines));

                const res = await fetch("/generate_prescription",{method:"POST",body:payload});
                const data = await res.json();
                if(data.success){ alert("Prescription sent!"); document.getElementById("presc_form").reset(); }
                else{ alert(data.error || "Error generating prescription"); }
            }

            async function fetchPrescriptions(){
                const res = await fetch(`/prescriptions/${currentUser}`);
                const data = await res.json();
                const container = document.getElementById("prescriptions");
                container.innerHTML="";
                data.forEach(p=>{
                    container.innerHTML += `<div class="presc">
                        <strong>From:</strong> ${p.doctor_name}<br>
                        <strong>Date:</strong> ${p.date} <strong>Time:</strong> ${p.time}<br>
                        <strong>Medicines:</strong><br>
                        ${p.medicines.map(m=>`- ${m.name} ${m.description? '('+m.description+')':''} : ${m.dosage}`).join('<br>')}<br>
                        <a href="/download/${p.file}" target="_blank">Download Prescription</a>
                    </div>`;
                });
            }

        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

# ---------------- GENERATE PRESCRIPTION ----------------
@app.post("/generate_prescription")
def generate_prescription(
    doctor_id: str = Form(...),
    patient_id: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    medicines: str = Form(...)
):
    if doctor_id not in users: return {"error":"Doctor ID not found"}
    if patient_id not in users: return {"error":"Patient ID not found"}

    medicines_list = json.loads(medicines)

    # Load template
    template_path = "prescription.jpg"
    if not os.path.exists(template_path):
        img = Image.new("RGB",(800,800),"white")
    else:
        img = Image.open(template_path)

    draw = ImageDraw.Draw(img)
    try:
        header_font = ImageFont.truetype("arial.ttf",24)
        font = ImageFont.truetype("arial.ttf",20)
        small_font = ImageFont.truetype("arial.ttf",18)
        bold_font = ImageFont.truetype("arialbd.ttf",20)
    except:
        header_font = font = small_font = bold_font = ImageFont.load_default()

    draw.text((40,40), f"Patient ID: {patient_id}", font=header_font, fill="black")
    draw.text((40,80), f"Doctor: {users[doctor_id]['name']}", font=font, fill="black")
    draw.text((40,120), f"Date: {date}  Time: {time}", font=font, fill="black")

    start_y = 180
    line_height = 50
    sr_x, name_x, desc_x, dosage_x = 40, 80, 300, 650

    for idx, med in enumerate(medicines_list):
        y = start_y + idx*line_height
        draw.text((sr_x,y), str(idx+1), font=font, fill="black")
        draw.text((name_x,y), med['name'], font=bold_font, fill="black")
        if med['description']: draw.text((desc_x,y), med['description'], font=small_font, fill="gray")
        draw.text((dosage_x,y), med['dosage'], font=font, fill="black")

    # Footer
    draw.text((40,700), f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M %p')}", font=font, fill="black")

    # Save
    file_name = f"{patient_id}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.jpg"
    img.save(file_name)

    # Save to prescriptions.json
    all_presc = load_prescriptions()
    all_presc.append({
        "doctor_id": doctor_id,
        "doctor_name": users[doctor_id]['name'],
        "patient_id": patient_id,
        "date": date,
        "time": time,
        "medicines": medicines_list,
        "file": file_name
    })
    save_prescriptions(all_presc)

    return {"success": True}

# ---------------- PATIENT FETCH ----------------
@app.get("/prescriptions/{patient_id}")
def get_prescriptions(patient_id: str):
    all_presc = load_prescriptions()
    patient_presc = [p for p in all_presc if p['patient_id']==patient_id]
    return patient_presc

# ---------------- DOWNLOAD ----------------
@app.get("/download/{file_name}")
def download_prescription(file_name: str):
    if os.path.exists(file_name):
        return FileResponse(file_name, media_type="image/jpeg", filename=file_name)
    return {"error":"File not found"}
