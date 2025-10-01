import csv
import hashlib
import os

# ----------------------------
# Helper Functions
# ----------------------------
def hash_password(password: str) -> str:
    """Return a SHA256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_files():
    """Initialize CSV files if they don't exist"""
    if not os.path.exists("patients.csv"):
        with open("patients.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "name", "age"])

    if not os.path.exists("doctors.csv"):
        with open("doctors.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "name", "specialization"])


# ----------------------------
# Signup Logic
# ----------------------------
def signup(user_type: str, username: str, password: str, **kwargs) -> str:
    filename = "patients.csv" if user_type == "patient" else "doctors.csv"

    # Check if user already exists
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return f"❌ {user_type.capitalize()} with this username already exists."

    # Store new user
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if user_type == "patient":
            writer.writerow([username, hash_password(password), kwargs.get("name", ""), kwargs.get("age", "")])
        else:  # doctor
            writer.writerow([username, hash_password(password), kwargs.get("name", ""), kwargs.get("specialization", "")])

    return f"✅ {user_type.capitalize()} registered successfully."


# ----------------------------
# Login Logic
# ----------------------------
def login(user_type: str, username: str, password: str) -> str:
    filename = "patients.csv" if user_type == "patient" else "doctors.csv"
    hashed_pw = hash_password(password)

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == hashed_pw:
                return f"✅ {user_type.capitalize()} login successful. Welcome {row['name']}!"
    return f"❌ Invalid username or password for {user_type}."


# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    init_files()

    # Patients
    # print(signup("patient", "john123", "mypassword", name="John Doe", age=30))
    # print(login("patient", "john123", "mypassword"))
    

    name = input("Enter your name: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    print(signup(name,username,password))

    # Doctors
    # print(signup("doctor", "drsmith", "docpass", name="Dr. Smith", specialization="Cardiology"))
    # print(login("doctor", "drsmith", "docpass"))
