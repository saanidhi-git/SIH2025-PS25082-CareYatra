function showMessage(message, isSuccess = true) {
    // Replaces the browser's blocking alert() function with console logging 
    // for a smoother user experience in an embedded environment.
    console.log(`[Message: ${isSuccess ? 'SUCCESS' : 'ERROR'}] ${message}`);
}

function handlePrescription() {
    closePopup(); // Closes the action selection modal
    showOnlyView("prescriptionView"); // Switches to the new Prescription View
    showMessage("Loading E-Prescription interface.", true);
}

// Function to dynamically add a medication row to the prescription form
function addMedicationRow() {
    const container = document.getElementById('medicationContainer');
    const newRow = document.createElement('div');
    newRow.className = 'med-row';
    newRow.style.cssText = 'display:flex; gap:10px; margin-bottom:10px; align-items:flex-end;';

    newRow.innerHTML = `
        <div class="form-group" style="flex: 2;">
            <label>Name:</label>
            <input type="text" name="medName[]" placeholder="e.g., Amoxicillin 250mg" required/>
        </div>
        <div class="form-group" style="flex: 1;">
            <label>Dosage:</label>
            <input type="text" name="dosage[]" placeholder="e.g., 1-1-1" required/>
        </div>
        <div class="form-group" style="flex: 2;">
            <label>Details (if any):</label>
            <input type="text" name="details[]" placeholder="e.g., After Meal" required/>
        </div>
        <button type="button" class="remove-med-btn" style="background:#d97452; color:white; border:none; padding:10px 14px; border-radius:6px; font-weight:bold; cursor:pointer;" onclick="removeMedicationRow(this)">X</button>
    `;
    container.appendChild(newRow);
    container.scrollTop = container.scrollHeight; // Scroll to the bottom to show the new row
}

// Function to remove a medication row
function removeMedicationRow(button) {
    const row = button.closest('.med-row');
    if (row) {
        row.remove();
    }
}

// Event listener for prescription form submission
document.addEventListener('DOMContentLoaded', () => {
    const prescriptionForm = document.getElementById('prescriptionForm');
    if (prescriptionForm) {
        prescriptionForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            
            const patientAbhaId = document.getElementById('prescribePatient').value.trim() || '111333444';

            const diagnosis = document.getElementById('diagnosis').value.trim();
            const doctorId = new URLSearchParams(window.location.search).get('user') || '11133399';


            // --- Collect dynamic data and format to match FastAPI backend requirements ---
            const medicationRows = document.querySelectorAll('#medicationContainer .med-row');
            const medicines = [];

            medicationRows.forEach(row => {
                // Find inputs by their NAME attribute
                const nameInput = row.querySelector('input[name="medName[]"]');
                const dosageInput = row.querySelector('input[name="dosage[]"]');
                const detailsInput = row.querySelector('input[name="details[]"]');
                
                // Only push if the main fields are filled
                if (nameInput.value.trim() && dosageInput.value.trim()) {
                    medicines.push({
                        // Map to backend fields: name, description (for details), dosage
                        name: nameInput.value.trim(), 
                        dosage: dosageInput.value.trim(),
                        description: detailsInput.value.trim() || "" 
                    });
                }
            });

            // 1. Validation Check
            if (!patientAbhaId || !diagnosis) {
                showMessage("Please select a patient and enter a diagnosis/instructions.", false);
                return;
            }
            if (medicines.length === 0) {
                showMessage("Please add at least one medication.", false);
                return;
            }

            // 2. Format Payload as FormData (FastAPI requirement)
            const now = new Date();
            const payload = new FormData();
            payload.append("doctor_id", doctorId);
            payload.append("patient_id", patientAbhaId);
            // Format Date/Time to match FastAPI's expectations (DD-MM-YYYY, HH:MM)
            payload.append("date", now.toLocaleDateString('en-IN', {day: '2-digit', month: '2-digit', year: 'numeric'}));
            payload.append("time", now.toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit', hour12: false}));
            payload.append("medicines", JSON.stringify(medicines)); // Must be JSON stringified

            
            // 3. API Call
            try {
                // IMPORTANT: Direct call to FastAPI on port 8000
                const response = await fetch('/api/generate-prescription', {
                    method: 'POST',
                    body: payload // Send as FormData directly
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    // SUCCESS MESSAGE: Displaying the target ID
                    showMessage(`Prescription finalized and sent to ID: ${patientAbhaId}`, true);
                    prescriptionForm.reset();
                    // Optional: Re-add a single empty row after submission if you want the form ready for the next one.
                    document.getElementById('medicationContainer').innerHTML = ''; 
                } else {
                    showMessage(`Failed to send prescription. Error: ${result.error || response.statusText}`, false);
                }

            } catch (error) {
                console.error("Prescription API call failed:", error);
                showMessage("A network error occurred. Ensure the FastAPI backend is running on port 8000.", false);
            }
        });
    }
});


// --- DYNAMIC DATA AND VIEW SWITCHING LOGIC (Rest of the code remains the same) ---
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const username = urlParams.get('user');

    const welcomeNameElement = document.getElementById('welcomeName');
    const userTypeElement = document.getElementById('userType');
    
    const profileSpecialtyEl = document.getElementById('profileSpecialty');
    const profileAbhaIdEl = document.getElementById('profileAbhaId');


    if (username) {
        try {
            const response = await fetch(`/api/doctor-data/${username}`);
            if (response.ok) {
                const userData = await response.json();
                
                welcomeNameElement.textContent = userData.name || userData.username;
                userTypeElement.textContent = userData.user_type;

                
                if (profileSpecialtyEl) profileSpecialtyEl.textContent = userData.specialization;
                if (profileAbhaIdEl) profileAbhaIdEl.textContent = userData.username;

                console.log('Doctor Data for My Patients tab:', userData);

            } else {
                console.error('Failed to fetch doctor data');
                welcomeNameElement.textContent = 'Doctor not found';
            }
        } catch (error) {
            console.error('An error occurred while fetching doctor data:', error);
            welcomeNameElement.textContent = 'Error fetching data';
        }
    } else {
        welcomeNameElement.textContent = 'Guest Doctor';
    }
});

const actionCards = document.querySelectorAll('.sidebar-grid .action-card');
const mainViews = document.querySelectorAll('.main-area .content-card > div');

function showOnlyView(viewId) {
    mainViews.forEach(view => {
        if (view.id === viewId) {
            view.style.display = 'block';
        } else {
            view.style.display = 'none';
        }
    });
}

actionCards.forEach(button => {
    button.addEventListener('click', () => {
        const viewId = button.dataset.view + 'View';
        showOnlyView(viewId);
    });
});

showOnlyView('addPatientsView');

const patientListEl = document.getElementById("patientList"); 
const form = document.getElementById("addPatientForm");
const popupModal = document.getElementById("popupModal");
const fileInput = document.getElementById("fileInput");

function renderPatients(list) {
    const patientListEl = document.getElementById('patientList');
    if (!patientListEl) return;
    patientListEl.innerHTML = "";
    list.forEach((p, i) => {
        const li = document.createElement("li");
        li.innerHTML = `<span>${i + 1}.</span> <span>${p.name}</span>`;
        li.style.opacity = 0;
        patientListEl.appendChild(li);
        setTimeout(() => {
            li.style.opacity = 1;
        }, 100);
    });
}

form.addEventListener("submit", function (e) {
    e.preventDefault();
    const abha = document.getElementById("abha").value.trim();
    const name = document.getElementById("name").value.trim();
    const dob = document.getElementById("dob").value.trim();
    if (!abha || !name || !dob) {
        showMessage("Please fill in all fields for the new patient.", false);
        return;
    }
    const newPatient = { name };
    const currentPatients = Array.from(patientListEl.children).map((li) => ({
        name: li.textContent.split(". ")[1] || "Unnamed",
    }));
    renderPatients([...currentPatients, newPatient]);
    form.reset();
});

document.querySelector('[title="Upload Documents"]').addEventListener("click", () => {
    popupModal.style.display = "flex";
});

function closePopup() {
    if (popupModal) popupModal.style.display = "none";
}

function triggerFileUpload() {
    if (fileInput) fileInput.click();
    if (fileInput) {
        fileInput.onchange = function () {
            const file = fileInput.files[0];
            if (file) {
                console.log("Selected file:", file.name);
            }
        };
    }
}

function handleHistory() {
    showOnlyView("historyView");
    closePopup();
}

document.querySelector('[title="Notifications"]').addEventListener("click", () => {
    showOnlyView("notificationsView");
});

function renderNotifications(list) {
    const notificationList = document.getElementById("notificationList");
    if (!notificationList) return;
    notificationList.innerHTML = "";
    if (list.length === 0) {
        const first = document.createElement("li");
        first.textContent = "No new notifications";
        notificationList.appendChild(first);
        for (let i = 1; i < 4; i++) {
            const li = document.createElement("li");
            notificationList.appendChild(li);
        }
    } else {
        list.forEach((note, i) => {
            const li = document.createElement("li");
            li.textContent = `${i + 1}. ${note}`;
            notificationList.appendChild(li);
        });
    }
}

document.querySelector('[title="Appointments"]').addEventListener("click", () => {
    showOnlyView("appointmentsView");
});

document.getElementById("appointmentForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const name = document.getElementById("patientName").value.trim();
    const date = document.getElementById("appointmentDate").value.trim();
    const time = document.getElementById("appointmentTime").value.trim();
    const reason = document.getElementById("reason").value.trim();
    if (!name || !date || !time || !reason) {
        showMessage("Please fill in all fields for the appointment.", false);
        return;
    }
    const appointmentData = { name, date, time, reason };
    console.log("Appointment scheduled:", appointmentData);
    showMessage("Appointment scheduled successfully!", true);
    this.reset();
});

document.querySelector('[title="Graphical Insights"]').addEventListener("click", () => {
    showOnlyView("graphicalInsightsView");
});

function goBackToAddPatients() {
    showOnlyView("addPatientsView");
}

let hasGreeted = false;
document.querySelector(".abha-logo").addEventListener("click", () => {
    document.getElementById("abhaChatWindow").style.display = "flex";
    const username = document.getElementById('welcomeName').textContent;
    const greetingEl = document.getElementById("chatGreeting");
    greetingEl.innerHTML = `Hi ${username} 👋<br>How can I assist you today?`;
    hasGreeted = false;
});

function closeAbhaChat() {
    document.getElementById("abhaChatWindow").style.display = "none";
}

// --- UPDATED sendMessage() FOR BACKEND INTEGRATION ---
async function sendMessage() {
    const chatInput = document.getElementById("chatInput");
    const message = chatInput.value.trim();
    if (!message) return;

    const chatBody = document.getElementById("chatBody");
    
    const urlParams = new URLSearchParams(window.location.search);
    const username = urlParams.get('user');

    // User message
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.textContent = message;
    chatBody.appendChild(userMsg);
    
    // Clear input
    chatInput.value = "";
    chatBody.scrollTop = chatBody.scrollHeight;
    
    // Placeholder for AI's message while we wait for the response
    const botMsg = document.createElement("div");
    botMsg.className = "bot-message";
    botMsg.textContent = "ABHA AI is thinking...";
    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;
    
    try {
        const response = await fetch(`/api/abha-chat/${username}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        const data = await response.json();
        
        // Update the placeholder with the real response
        botMsg.textContent = data.reply;

    } catch (error) {
        console.error('ABHA AI chat failed:', error);
        botMsg.textContent = "An error occurred. Please try again.";
    }
    
    chatBody.scrollTop = chatBody.scrollHeight;
}
