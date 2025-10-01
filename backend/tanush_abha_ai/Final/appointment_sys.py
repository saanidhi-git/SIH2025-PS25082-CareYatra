from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import datetime

APP_FILE = "applications.json"

# ----------------- DATA -----------------
users = {
    "d1": {"name": "Doctor Sharma", "role": "Doctor"},
    "p1": {"name": "Patient Rohan", "role": "Patient"},
}

if not os.path.exists(APP_FILE):
    with open(APP_FILE, "w") as f:
        json.dump([], f)

def load_apps():
    with open(APP_FILE, "r") as f:
        return json.load(f)

def save_apps(apps):
    with open(APP_FILE, "w") as f:
        json.dump(apps, f, indent=4)

# ----------------- FASTAPI -----------------
app = FastAPI(title="Doctor-Patient Application System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------------- HTML FRONTEND -----------------
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doctor-Patient Scheduler</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f4f7fb; color:#333; margin:0; padding:0; }
            header { background:#007acc; color:white; padding:20px; text-align:center; }
            .container { padding:20px; max-width:700px; margin:auto; }
            input, select { width:100%; padding:8px; margin:5px 0; border:1px solid #ccc; border-radius:4px; }
            button { background:#007acc; color:white; padding:10px 15px; border:none; border-radius:4px; cursor:pointer; }
            button:hover { background:#005fa3; }
            .app { border-bottom:1px solid #ccc; padding:10px 0; }
            h2 { color:#007acc; }
        </style>
    </head>
    <body>
        <header>
            <h1>Doctor-Patient Scheduler</h1>
        </header>
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

        <div class="container" id="app_container" style="display:none;">
            <h2>Send Application</h2>
            <form id="app_form">
                <label>Recipient ID:</label>
                <input type="text" id="to_id" required>
                <label>Date (DD-MM-YYYY):</label>
                <input type="text" id="date" required>
                <label>Time (HH:MM):</label>
                <input type="text" id="time" required>
                <label>Reason:</label>
                <input type="text" id="reason" required>
                <div id="priority_div">
                    <label>Priority:</label>
                    <select id="priority">
                        <option value="Urgent">Urgent</option>
                        <option value="Not So Urgent">Not So Urgent</option>
                        <option value="As soon as possible">As soon as possible</option>
                    </select>
                </div>
                <button type="submit">Send Application</button>
            </form>

            <h2>Existing Applications</h2>
            <div id="applications"></div>
            <button onclick="logout()">Logout</button>
        </div>

        <script>
            let currentUser = null;
            let currentRole = null;

            function login(){
                const uid = document.getElementById("user_id").value.trim();
                const role = document.getElementById("role_select").value;
                if(!uid){ alert("Enter your ID"); return; }
                // Simple client-side validation
                if(role === "Doctor" && uid !== "d1"){ alert("Invalid Doctor ID"); return; }
                if(role === "Patient" && uid !== "p1"){ alert("Invalid Patient ID"); return; }
                currentUser = uid;
                currentRole = role;
                document.getElementById("login_container").style.display="none";
                document.getElementById("app_container").style.display="block";

                // Hide priority if doctor
                if(role === "Doctor"){ document.getElementById("priority_div").style.display="none"; }

                fetchApps();
            }

            function logout(){
                currentUser = null;
                currentRole = null;
                document.getElementById("login_container").style.display="block";
                document.getElementById("app_container").style.display="none";
            }

            document.getElementById("app_form").onsubmit = async function(e){
                e.preventDefault();
                const to_id = document.getElementById("to_id").value.trim();
                const date = document.getElementById("date").value.trim();
                const time = document.getElementById("time").value.trim();
                const reason = document.getElementById("reason").value.trim();
                const priority = document.getElementById("priority").value;

                let formData = new FormData();
                formData.append("from_id", currentUser);
                formData.append("to_id", to_id);
                formData.append("date", date);
                formData.append("time", time);
                formData.append("reason", reason);
                if(currentRole === "Patient"){ formData.append("priority", priority); }

                const res = await fetch("/send_application", {method:"POST", body:formData});
                const data = await res.json();
                if(data.success){ alert("Application sent!"); fetchApps(); }
                else{ alert(data.error || "Error sending application"); }
            }

            async function fetchApps(){
                if(!currentUser) return;
                const res = await fetch("/applications");
                const apps = await res.json();
                const container = document.getElementById("applications");
                container.innerHTML = "";
                apps.forEach(app=>{
                    if(app.from_id === currentUser || app.to === currentUser){
                        container.innerHTML += `<div class="app">
                            <strong>From:</strong> ${app.from_id} (${app.from}) → <strong>To:</strong> ${app.to}<br>
                            <strong>Date:</strong> ${app.date} <strong>Time:</strong> ${app.time}<br>
                            <strong>Reason:</strong> ${app.reason}<br>
                            ${app.priority ? '<strong>Priority:</strong> '+app.priority+'<br>':''}
                            <small>Received: ${app.received_at}</small>
                        </div>`;
                    }
                });
            }

            setInterval(fetchApps,5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

# ----------------- GET APPLICATIONS -----------------
@app.get("/applications")
def get_applications():
    return load_apps()

# ----------------- POST APPLICATION -----------------
@app.post("/send_application")
def send_application(
    from_id: str = Form(...),
    to_id: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    reason: str = Form(...),
    priority: str = Form(None)
):
    if from_id not in users: return {"error":"Your ID not found!"}
    if to_id not in users: return {"error":"Recipient ID not found!"}

    app_entry = {
        "from_id": from_id,
        "from": users[from_id]["name"],
        "to": to_id,
        "date": date,
        "time": time,
        "reason": reason,
        "received_at": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    if users[from_id]["role"]=="Patient" and priority: app_entry["priority"]=priority

    apps = load_apps()
    apps.append(app_entry)
    save_apps(apps)
    return {"success": True, "message":"Application sent successfully."}

# ----------------- RUN -----------------
if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
