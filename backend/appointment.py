import json
import datetime
import getpass

# -------------------- FILE HANDLING --------------------
USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"

def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# -------------------- USER MANAGEMENT --------------------
def register_user():
    users = load_data(USERS_FILE)
    username = input("Choose a username: ").strip()
    if username in users:
        print("Username already taken!")
        return None

    password = getpass.getpass("Choose a password: ")
    role = input("Enter role (patient/doctor): ").lower()

    if role not in ["patient", "doctor"]:
        print("Role must be 'patient' or 'doctor'")
        return None

    users[username] = {"password": password, "role": role}
    save_data(USERS_FILE, users)

    print(f"{role.capitalize()} '{username}' registered successfully.")
    return username

def login_user():
    users = load_data(USERS_FILE)
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")

    if username in users and users[username]["password"] == password:
        print(f"Welcome {username} ({users[username]['role']})!")
        return username, users[username]['role']
    else:
        print("Invalid username or password.")
        return None, None

# -------------------- APPOINTMENT SYSTEM --------------------
def send_appointment(sender):
    users = load_data(USERS_FILE)
    receiver = input("Doctor's username: ").strip()

    if receiver not in users or users[receiver]["role"] != "doctor":
        print("Receiver must be a registered doctor.")
        return

    date = input("Enter appointment date (YYYY-MM-DD): ")
    time = input("Enter appointment time (HH:MM): ")
    reason = input("Reason for appointment: ")

    appointment_text = f"""
    ----- Appointment Request -----
    From: {sender}
    To: Dr. {receiver}
    Date: {date}
    Time: {time}
    Reason: {reason}
    Sent At: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    --------------------------------
    """

    messages = load_data(MESSAGES_FILE)
    if receiver not in messages:
        messages[receiver] = []

    messages[receiver].append({
        "from": sender,
        "to": receiver,
        "type": "appointment_request",
        "content": appointment_text,
        "status": "Pending"
    })
    save_data(MESSAGES_FILE, messages)

    print(f"Appointment request sent to Dr. {receiver}.")

def view_messages(username):
    messages = load_data(MESSAGES_FILE)
    if username not in messages or not messages[username]:
        print("📭 No messages found.")
        return

    print(f"\n📬 Messages for {username}:")
    for i, msg in enumerate(messages[username], start=1):
        print(f"\n--- Message {i} ---")
        print(msg["content"])
        print(f"Status: {msg.get('status','-')}")

def doctor_reply(doctor):
    messages = load_data(MESSAGES_FILE)
    if doctor not in messages or not messages[doctor]:
        print("📭 No appointment requests yet.")
        return

    print(f"\n📬 Appointment Requests for Dr. {doctor}:")
    for i, msg in enumerate(messages[doctor], start=1):
        print(f"\n[{i}]")
        print(msg["content"])

    choice = input("\nEnter the request number to reply (or press Enter to skip): ")
    if not choice.isdigit():
        return
    choice = int(choice)

    if choice < 1 or choice > len(messages[doctor]):
        print("Invalid choice.")
        return

    req = messages[doctor][choice - 1]
    patient = req["from"]

    decision = input("Approve (A) / Reject (R): ").strip().upper()
    if decision not in ["A", "R"]:
        print("Invalid option.")
        return

    status = "Approved" if decision == "A" else "Rejected"
    req["status"] = status

    reply_text = f"""
    ----- Appointment Response -----
    From: Dr. {doctor}
    To: {patient}
    Date: {req['content'].split('Date: ')[1].splitlines()[0]}
    Time: {req['content'].split('Time: ')[1].splitlines()[0]}
    Status: {status}
    Replied At: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    --------------------------------
    """

    if patient not in messages:
        messages[patient] = []
    messages[patient].append({
        "from": doctor,
        "to": patient,
        "type": "appointment_reply",
        "content": reply_text,
        "status": status
    })

    save_data(MESSAGES_FILE, messages)
    print(f"✅ Reply sent to {patient}.")

# -------------------- MAIN MENU --------------------
def main():
    print("=== Appointment Scheduler ===")

    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            register_user()

        elif choice == "2":
            username, role = login_user()
            if username:
                while True:
                    print(f"\n--- Logged in as {username} ({role}) ---")
                    if role == "patient":
                        print("1. Send Appointment")
                        print("2. View Messages")
                        print("3. Logout")
                        choice = input("Enter choice: ")
                        if choice == "1":
                            send_appointment(username)
                        elif choice == "2":
                            view_messages(username)
                        elif choice == "3":
                            print("Logged out.")
                            break
                        else:
                            print("Invalid option!")
                    elif role == "doctor":
                        print("1. View Appointment Requests")
                        print("2. Reply to Appointment")
                        print("3. Logout")
                        choice = input("Enter choice: ")
                        if choice == "1":
                            view_messages(username)
                        elif choice == "2":
                            doctor_reply(username)
                        elif choice == "3":
                            print("Logged out.")
                            break
                        else:
                            print("Invalid option!")

        elif choice == "3":
            print("Done")
            break
        else:
            print("Invalid option, try again!")

# Only runs if executed directly, not when imported
if __name__ == "__main__":
    main()
