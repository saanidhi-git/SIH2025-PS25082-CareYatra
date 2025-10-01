import os
import pandas as pd
import qrcode
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

CSV_FILE = "profiles.csv"
QR_FOLDER = "qrcodes"

# Required headers
HEADERS = [
    "Name","ABHA ID","Date of Birth","Blood Group","Age","Work / Occupation",
    "Allergies","Spoken Languages","Permanent Address","Current Address",
    "Employer Name","Employer Phone","Vaccinations info"
]

# ----------------- Ensure CSV Exists -----------------
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=HEADERS)
        df.to_csv(CSV_FILE, index=False)
        print(f"Created {CSV_FILE} with headers.")

# ----------------- Generate QR Codes -----------------
def generate_qrcodes(df):
    os.makedirs(QR_FOLDER, exist_ok=True)
    for _, row in df.iterrows():
        qr_data = "\n".join([f"{col}: {row[col]}" for col in HEADERS])
        img = qrcode.make(qr_data)
        qr_path = os.path.join(QR_FOLDER, f"{row['Name']}_qr.png")
        img.save(qr_path)

# ----------------- UI for Profile Display -----------------
def show_profile(profile):
    win = Toplevel()
    win.title(f"Profile - {profile['Name']}")

    # Display profile details
    frame = Frame(win, padx=15, pady=15)
    frame.pack()

    Label(frame, text="Profile Details", font=("Arial", 16, "bold")).pack(pady=10)

    details = "\n".join([f"{col}: {profile[col]}" for col in HEADERS])
    Label(frame, text=details, justify=LEFT, font=("Arial", 12)).pack(pady=10)

    # Load and show QR code
    qr_path = os.path.join(QR_FOLDER, f"{profile['Name']}_qr.png")
    if os.path.exists(qr_path):
        img = Image.open(qr_path).resize((200, 200))
        qr_img = ImageTk.PhotoImage(img)
        Label(frame, text="QR Code:", font=("Arial", 14, "bold")).pack(pady=5)
        Label(frame, image=qr_img).pack(pady=5)
        win.qr_img = qr_img

# ----------------- Main App -----------------
def main_app():
    ensure_csv()
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        messagebox.showinfo("Info", f"No profiles in {CSV_FILE}. Please add data manually.")
        return

    generate_qrcodes(df)

    root = Tk()
    root.title("Profile Viewer with QR")

    Label(root, text="Select Profile", font=("Arial", 14, "bold")).pack(pady=10)

    # Dropdown to select profile
    names = df["Name"].tolist()
    selected = StringVar()
    selected.set(names[0])

    dropdown = ttk.Combobox(root, textvariable=selected, values=names, state="readonly")
    dropdown.pack(pady=10)

    def load_profile():
        name = selected.get()
        profile = df[df["Name"] == name].iloc[0]
        show_profile(profile)

    Button(root, text="Show Profile", command=load_profile, font=("Arial", 12), bg="lightblue").pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    main_app()

