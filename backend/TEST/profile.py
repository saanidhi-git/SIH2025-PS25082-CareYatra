import os
import csv

PROFILE_FILE = "profile_info_my_family.csv"

def ensure_profile_file():
    """Ensure the profile file exists with proper headers."""
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Profile_Type", "ABHA_ID", "Name", "Age", "Height", "Blood_Group", "Weight"])
        print(f"✅ Created {PROFILE_FILE}")

def add_profile(profile_type):
    """Add a new profile (me/family)."""
    abha_id = input("Enter ABHA ID: ")
    name = input("Enter Name: ")
    age = input("Enter Age: ")
    height = input("Enter Height (cm): ")
    blood_group = input("Enter Blood Group: ")
    weight = input("Enter Weight (kg): ")

    with open(PROFILE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([profile_type, abha_id, name, age, height, blood_group, weight])

    print(f"✅ {profile_type.capitalize()} profile for '{name}' added successfully!")

def view_profiles():
    """Display all saved profiles."""
    if not os.path.exists(PROFILE_FILE):
        print("⚠️ No profiles found.")
        return

    with open(PROFILE_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        profiles = list(reader)

    if not profiles:
        print("⚠️ No profiles saved yet.")
    else:
        print("\n📋 Saved Profiles:")
        for i, row in enumerate(profiles, 1):
            print(f"{i}. [{row['Profile_Type']}] {row['Name']} | ABHA: {row['ABHA_ID']} | Age: {row['Age']} | Height: {row['Height']} cm | Weight: {row['Weight']} kg | Blood Group: {row['Blood_Group']}")

def edit_profile():
    """Edit an existing profile."""
    if not os.path.exists(PROFILE_FILE):
        print("⚠️ No profiles found.")
        return

    with open(PROFILE_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        profiles = list(reader)

    if not profiles:
        print("⚠️ No profiles saved yet.")
        return

    # Show existing profiles
    print("\nSelect profile to edit:")
    for i, row in enumerate(profiles, 1):
        print(f"{i}. [{row['Profile_Type']}] {row['Name']} (ABHA: {row['ABHA_ID']})")

    choice = int(input("\nEnter profile number: "))
    if choice < 1 or choice > len(profiles):
        print("❌ Invalid choice.")
        return

    profile = profiles[choice - 1]
    print(f"\nEditing profile for {profile['Name']}")

    # Ask new values (press enter to keep old one)
    for field in ["ABHA_ID", "Name", "Age", "Height", "Blood_Group", "Weight"]:
        new_value = input(f"{field} [{profile[field]}]: ")
        if new_value.strip():
            profile[field] = new_value

    # Update in list
    profiles[choice - 1] = profile

    # Save back to file
    with open(PROFILE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Profile_Type", "ABHA_ID", "Name", "Age", "Height", "Blood_Group", "Weight"])
        writer.writeheader()
        writer.writerows(profiles)

    print("✅ Profile updated successfully!")

def main():
    ensure_profile_file()

    while True:
        print("\n===== Profile Management System =====")
        print("1. Create 'Me' profile")
        print("2. Create Family Member profile")
        print("3. View Profiles")
        print("4. Edit Profile")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_profile("Me")
        elif choice == "2":
            add_profile("Family")
        elif choice == "3":
            view_profiles()
        elif choice == "4":
            edit_profile()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
