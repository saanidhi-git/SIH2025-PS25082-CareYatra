import os
import csv

FAMILY_FILE = "my_family.csv"

def  app():

    def ensure_family_file():
        """Ensure the family file exists with proper headers."""
        if not os.path.exists(FAMILY_FILE):
            with open(FAMILY_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ABHA_ID", "Name", "Age", "Assigned_Doctor"])
            print(f"✅ Created {FAMILY_FILE}")

    def add_family_member():
        """Take user input and save family member details."""
        abha_id = input("Enter ABHA ID: ")
        name = input("Enter Name: ")
        age = input("Enter Age: ")
        doctor = input("Enter Assigned Doctor: ")

        # Save to CSV
        with open(FAMILY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([abha_id, name, age, doctor])

        print(f"✅ Family member '{name}' added successfully!")

    def main():
        ensure_family_file()
        add_family_member()

    if __name__ == "__main__":
        main()


app()
