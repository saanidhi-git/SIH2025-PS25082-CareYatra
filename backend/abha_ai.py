import json
import ollama
import random
import os

# -------------------------------
# JSON file path
# -------------------------------
DATA_FILE = "patient_data.json"

# Ensure the JSON file exists with patient structure
if not os.path.exists(DATA_FILE):
    patient_template = {
        "patient_name": "John Doe",
        "dob": "1990-01-01",
        "blood_group": "O+",
        "weight": "70kg",
        "height": "175cm",
        "allergies": ["Penicillin"],
        "current_medications": [
            {"name": "Metformin", "for": "Diabetes", "dosage": "500mg daily"}
        ],
        "medical_history": ["Type 2 Diabetes", "Hypertension"],
        "prescriptions": [
            {
                "date": "2024-01-15",
                "reason": "Regular Checkup",
                "doctor": {"name": "Dr. Smith", "speciality": "Endocrinologist"},
                "injections": ["Insulin - 5 units"],
                "medications": ["Metformin 500mg", "Aspirin 75mg"]
            }
        ],
        "messages": []
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(patient_template, f, indent=4)

# -------------------------------
# Fun Sentrix responses
# -------------------------------
learning_responses = [
    "Looks like I can help you with that! ...but hey, I'm still learning!",
    "I got this! Well, mostly … learning every day!",
    "Sure! Just a heads-up: I'm still learning, so bear with me!",
    "I can try to help! Keep in mind, I’m still growing my knowledge!"
]

bot_greeting = "🌟 Abha: Hello! I’m your CareYatra assistant. Type 'exit' anytime to say goodbye!\n"
exit_message = "Sentrix: Goodbye! Thank you for being at CareYatra 🌍💚"

# -------------------------------
# Exit keywords
# -------------------------------
EXIT_KEYWORDS = [
    "exit", "quit", "bye", "goodbye", "close", "stop", "end"
]

# -------------------------------
# Quick greetings
# -------------------------------
GREETINGS = ["hi", "hello", "hey", "hola", "yo"]

# -------------------------------
# Knowledge lookup function
# -------------------------------
def lookup_patient(query: str):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        patient = json.load(f)

    query = query.lower()

    # General patient info
    if "name" in query:
        return f"👤 Patient Name: {patient['patient_name']}"
    if "dob" in query or "birth" in query:
        return f"🎂 Date of Birth: {patient['dob']}"
    if "blood" in query:
        return f"🩸 Blood Group: {patient['blood_group']}"
    if "weight" in query:
        return f"⚖️ Weight: {patient['weight']}"
    if "height" in query:
        return f"📏 Height: {patient['height']}"
    if "allerg" in query:
        return f"⚠️ Allergies: {', '.join(patient['allergies'])}"

    # Medical history
    if "history" in query:
        return f"📚 Medical History: {', '.join(patient['medical_history'])}"

    # Medications
    if "medication" in query or "medicine" in query:
        meds = ", ".join([f"{m['name']} ({m['for']}, {m['dosage']})" for m in patient.get("current_medications", [])])
        return f"💊 Current Medications: {meds}"

    # Prescriptions
    if "prescription" in query or "visit" in query or "doctor" in query:
        details = []
        for p in patient.get("prescriptions", []):
            details.append(
                f"📅 {p['date']} | Reason: {p['reason']} | Doctor: {p['doctor']['name']} ({p['doctor']['speciality']})\n"
                f"   Injections: {', '.join(p['injections'])}\n"
                f"   Medications: {', '.join(p['medications'])}"
            )
        return "📝 Prescriptions:\n" + "\n".join(details)

    return None

# -------------------------------
# Main chat loop
# -------------------------------
print(bot_greeting)

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in EXIT_KEYWORDS:
        print(exit_message)
        break

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            patient = json.load(f)
        except json.JSONDecodeError:
            patient = {"messages": []}

    if "messages" not in patient:
        patient["messages"] = []

    # 1️⃣ Check Knowledge Base
    entry = lookup_patient(user_input)
    if entry:
        assistant_reply = entry
        patient["messages"].append({"role": "user", "content": user_input})
        patient["messages"].append({"role": "assistant", "content": assistant_reply})

    # 2️⃣ Greeting Handler
    elif user_input.lower() in GREETINGS:
        assistant_reply = random.choice([
            "Hey there! How can I help you?",
            "Hello! How can I serve you today?",
            "Hi! Abha here, ready to assist you."
        ])
        patient["messages"].append({"role": "user", "content": user_input})
        patient["messages"].append({"role": "assistant", "content": assistant_reply})

    # 3️⃣ Otherwise, send to LLM
    else:
        patient["messages"].append({"role": "user", "content": user_input})
        valid_messages = [
            m for m in patient["messages"]
            if isinstance(m, dict) and "role" in m and "content" in m
        ]

        if random.random() < 0.2:
            assistant_reply = random.choice(learning_responses)
        else:
            try:
                messages = [
                    {"role": "system", "content": "You are Abha, a Healthcare AI assistant, Document summariser & expert."}
                ] + valid_messages

                print("[Info] Using model: llama3:8b")
                response = ollama.chat(
                    model="llama3:8b",
                    messages=messages
                )
                assistant_reply = response.get("message", {}).get("content", "Sorry, I couldn’t process that.")
            except Exception as e:
                assistant_reply = f"[!] Error communicating with model: {e}"

        patient["messages"].append({"role": "assistant", "content": assistant_reply})

    # Print and Save
    print(f"Sentrix: {assistant_reply}\n")

    cleaned_messages = [
        m for m in patient["messages"]
        if isinstance(m, dict) and "role" in m and "content" in m
    ]
    patient["messages"] = cleaned_messages

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(patient, f, indent=4)