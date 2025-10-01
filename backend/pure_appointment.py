'''import json
import os
import datetime

APP_FILE = "applications.json"

# ----------------- DATA -----------------
users = {
    "d1": {"name": "Doctor Sharma", "role": "Doctor"},
    "p1": {"name": "Patient Rohan", "role": "Patient"},
}

# Ensure applications file exists
if not os.path.exists(APP_FILE):
    with open(APP_FILE, "w") as f:
        json.dump([], f)


# ----------------- HELPERS -----------------
def load_apps():
    """Load all applications from the file."""
    with open(APP_FILE, "r") as f:
        return json.load(f)


def save_apps(apps):
    """Save all applications to the file."""
    with open(APP_FILE, "w") as f:
        json.dump(apps, f, indent=4)


# ----------------- CORE FUNCTIONS -----------------
def get_applications():
    """Return all applications."""
    return load_apps()


def send_application(from_id, to_id, date, time, reason, priority=None):
    """Send an application from one user to another."""
    if from_id not in users:
        return {"error": "Your ID not found!"}
    if to_id not in users:
        return {"error": "Recipient ID not found!"}

    app_entry = {
        "from_id": from_id,
        "from": users[from_id]["name"],
        "to": to_id,
        "date": date,
        "time": time,
        "reason": reason,
        "received_at": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

    if users[from_id]["role"] == "Patient" and priority:
        app_entry["priority"] = priority

    apps = load_apps()
    apps.append(app_entry)
    save_apps(apps)

    return {"success": True, "message": "Application sent successfully."}


# ----------------- USER INPUT LOOP -----------------
while True:
    print("\n--- Doctor-Patient Application System ---")
    print("1. Send Application")
    print("2. View All Applications")
    print("3. Exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        from_id = input("Enter your ID: ").strip()
        to_id = input("Enter recipient ID: ").strip()
        date = input("Enter date (DD-MM-YYYY): ").strip()
        time = input("Enter time (HH:MM): ").strip()
        reason = input("Enter reason: ").strip()

        priority = None
        if users.get(from_id, {}).get("role") == "Patient":
            priority = input("Enter priority (Urgent / Not So Urgent / As soon as possible): ").strip()

        result = send_application(from_id, to_id, date, time, reason, priority)
        print(result)

    elif choice == "2":
        apps = get_applications()
        if not apps:
            print("No applications found.")
        else:
            for i, app in enumerate(apps, 1):
                print(f"\nApplication {i}:")
                for k, v in app.items():
                    print(f"  {k}: {v}")

    elif choice == "3":
        print("Exiting... Goodbye!")
        break

    else:
        print("Invalid choice. Try again.")'''


import json
import os
import datetime

# --- IMPORTANT: USER ID MAPPING ---
# Replace the placeholder IDs (d1, p1) with your system's IDs
USER_MAPPING = {
    # Patient ABHA ID (used for 'from_id' in send_application)
    "111333444": {"name": "Patient Worker", "role": "Patient"},
    # Doctor HPR ID (used for 'to_id' in send_application)
    "111333999": {"name": "Dr. Raj", "role": "Doctor"},
    # Add other IDs as placeholders if necessary
}

# Define the directory where this script resides (the 'backend' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(BASE_DIR, "applications.json")


# Ensure applications file exists
if not os.path.exists(APP_FILE):
    with open(APP_FILE, "w") as f:
        json.dump([], f)


# ----------------- HELPERS -----------------
def load_apps():
    """Load all applications from the file."""
    # Handle empty file case safely
    if os.path.getsize(APP_FILE) == 0:
        return []
    with open(APP_FILE, "r") as f:
        return json.load(f)


def save_apps(apps):
    """Save all applications to the file."""
    with open(APP_FILE, "w") as f:
        json.dump(apps, f, indent=4)


# ----------------- CORE FUNCTIONS -----------------
def send_application(from_id, to_id, date, time, reason, priority=None):
    """Send an application (appointment request) from one user to another."""
    
    # Check if IDs exist (use the local mapping for internal consistency)
    if from_id not in USER_MAPPING:
        return {"error": "Your ID not found in system map."}
    if to_id not in USER_MAPPING:
        return {"error": "Recipient ID not found in system map."}

    app_entry = {
        "from_id": from_id,
        "from_name": USER_MAPPING[from_id]["name"],
        "to_id": to_id,
        "to_name": USER_MAPPING[to_id]["name"],
        "date": date,
        "time": time,
        "reason": reason,
        "received_at": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

    if USER_MAPPING[from_id]["role"] == "Patient" and priority:
        app_entry["priority"] = priority

    apps = load_apps()
    apps.append(app_entry)
    save_apps(apps)

    return {"success": True, "message": "Appointment application sent successfully."}

# Function for the Doctor Dashboard to potentially view all sent applications (optional)
def get_applications_by_recipient(recipient_id):
    """Filter applications destined for a specific recipient (Doctor)."""
    all_apps = load_apps()
    return [app for app in all_apps if app.get('to_id') == recipient_id]

# The original command-line loop is removed to make this script importable.

