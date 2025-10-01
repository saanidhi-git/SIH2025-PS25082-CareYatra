import os
import csv

DOCTOR_FILE = "my_doctor.csv"
APPOINTMENT_FILE = "appointments.csv"

def ensure_doctor_file():
    """Ensure the doctor file exists, if not create it with header."""
    if not os.path.exists(DOCTOR_FILE):
        with open(DOCTOR_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["doctor_name"])  # only header
        print(f"✅ Created {DOCTOR_FILE}, but no doctors assigned yet.")

def load_doctors():
    """Load doctor names from the file."""
    doctors = []
    with open(DOCTOR_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["doctor_name"].strip():
                doctors.append(row["doctor_name"].strip())
    return doctors

def save_appointment(doctor, date, time, for_whom):
    """Save appointment to file."""
    file_exists = os.path.exists(APPOINTMENT_FILE)
    with open(APPOINTMENT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["doctor_name", "date", "time", "for_whom"])
        writer.writerow([doctor, date, time, for_whom])
    print(f"✅ Appointment booked with Dr. {doctor} on {date} at {time} for {for_whom}")

def view_appointments():
    """Display all scheduled appointments."""
    if not os.path.exists(APPOINTMENT_FILE):
        print("⚠️ No appointments scheduled yet.")
        return

    with open(APPOINTMENT_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        appointments = list(reader)

    if not appointments:
        print("⚠️ No appointments scheduled yet.")
    else:
        print("\n📅 Current Appointments:")
        for i, row in enumerate(appointments, 1):
            print(f"{i}. Dr. {row['doctor_name']} | {row['date']} {row['time']} | For: {row['for_whom']}")

def book_appointment():
    """Handle booking flow."""
    ensure_doctor_file()
    doctors = load_doctors()

    if not doctors:
        print("⚠️ No doctor assigned. Please add doctors in 'my_doctor.csv'.")
        return

    print("\nAvailable Doctors:")
    for i, doc in enumerate(doctors, 1):
        print(f"{i}. {doc}")

    # Select doctor
    choice = int(input("\nSelect doctor (enter number): "))
    if choice < 1 or choice > len(doctors):
        print("❌ Invalid choice.")
        return
    doctor = doctors[choice - 1]

    # Input appointment details
    date = input("Enter appointment date (YYYY-MM-DD): ")
    time = input("Enter appointment time (HH:MM): ")
    for_whom = input("Is this for you or a family member? (me/family-member): ")

    # Save appointment
    save_appointment(doctor, date, time, for_whom)

def main():
    while True:
        print("\n===== Appointment System =====")
        print("1. Book new appointment")
        print("2. View scheduled appointments")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            book_appointment()
        elif choice == "2":
            view_appointments()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
