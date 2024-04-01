"""
Title: Triage
Author: Charles Bostwick
Website: www.CharlesCBostwick.com
GitHub: https://github.com/AwaywithCharles
License: MIT
Note: This is still a work in progress!!!
Goals: Add functions to add disabilitys and integrate with the 38 CFR to calculate estimated ratings
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import os
import json
import pandas
import matplotlib

# Main Application Class.
# Setting up the main window and functionalities.
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.user_data = {"dod_id": "", "preferences": {}, "data": {}}
        self.configure_application()
        self.create_menus()
        self.initialize_ui()
        self.user_info_frame = None

    # Configure main application window properties such as title, background, and size.
    def configure_application(self):
        self.title("Triage - a VA Disability Claim assistant")
        self.configure(bg="black")
        self.geometry("800x600")  # Width x Height

    # Create the application menu bar and items, adding functionality for user interaction.
    def create_menus(self):
        self.menu_bar = tk.Menu(self, bg="black", fg="gold")
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="black", fg="gold")
        file_menu.add_command(label="New Person", command=self.create_new_user_dialog)
        file_menu.add_command(label="Load Person", command=self.load_user_dialog)  # Add Load Person
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # User Profile (If you have other options to add, keep this section)
        profile_menu = tk.Menu(self.menu_bar, tearoff=0, bg="black", fg="gold")
        profile_menu.add_command(label="Edit Profile", command=self.edit_profile)
        self.menu_bar.add_cascade(label="Profile", menu=profile_menu)
        
        # Resources (If you have other options to add, keep this section)
        resources_menu = tk.Menu(self.menu_bar, tearoff=0, bg="black", fg="gold")
        resources_menu.add_command(label="38 CFR Regulations", command=self.open_regulations)
        self.menu_bar.add_cascade(label="Resources", menu=resources_menu)
        
        self.config(menu=self.menu_bar)
    
    # Helper function to add individual menu items to the menu bar.
    def add_menu_item(self, menu_title, commands):
        menu = tk.Menu(self.menu_bar, tearoff=0, bg="black", fg="gold")
        for label, command in commands:
            menu.add_command(label=label, command=command)
        self.menu_bar.add_cascade(label=menu_title, menu=menu)

    # Initialize the main UI frame and call the widget creation function.
    def initialize_ui(self):
        self.main_frame = tk.Frame(self, bg="black")
        self.main_frame.pack(fill="both", expand=True)
        self.create_widgets()

    # Create the initial widgets displayed in the main frame.
    def create_widgets(self):
        welcome_label = tk.Label(self.main_frame, text="Welcome to Triage!", bg="black", fg="gold")
        welcome_label.pack(pady=10)

    # Function to handle the application exit command.
    def on_exit(self):
        if messagebox.askokcancel("Exit", "Do you really wish to exit?", icon='warning'):
            self.destroy()

    # Load user profile dialog: Asks for dod_id and attempts to load the corresponding profile.
    def ask_user_action(self):
        action = messagebox.askquestion("User Action", "Load existing user?")
        if action == 'yes':
            self.load_user_dialog()
        else:
            self.new_user_dialog()

    # Load an existing user profile from a JSON file, if it exists.
    def load_user_dialog(self):
        dod_id = simpledialog.askstring("Load User", "Enter DoD ID # to load:")
        if dod_id:
            self.load_user(dod_id)

    # Create a new user profile, initializing with default data and saving to a JSON file.
    def create_new_user(self, dod_id):
        print("Creating new user with DoD ID:", dod_id)
        user_profile = UserProfile(dod_id=dod_id)
        self.show_user_info_frame(user_profile)

        user_data = {
            "dod_id": dod_id,
            "preferences": {},
            "data": {},
            "disabilities": []  # Placeholder for disability information
        }
        # Save user data to a file
        file_path = os.path.join(os.getcwd(), f"{dod_id}.json")
        with open(file_path, 'w') as file:
            json.dump(user_data, file)
        print(f"User {dod_id} created successfully.")

        return user_profile
    
    def create_new_user_dialog(self):
        self.new_user_window = tk.Toplevel(self)
        self.new_user_window.title("New User")
        self.new_user_window.geometry("400x600")  # Adjust size as necessary
        
        # Define user details fields
        fields = ['DoD ID', 'Name', 'Date of Birth', 'Marital Status', 'Disability Rating', 'Spouse', 'Dependents']
        self.new_user_entries = {}
        
        for idx, field in enumerate(fields):
            tk.Label(self.new_user_window, text=f"{field}:").grid(row=idx, column=0, padx=10, pady=5, sticky='w')
            entry = tk.Entry(self.new_user_window)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.new_user_entries[field] = entry
        
        # Save Profile Button
        save_button = tk.Button(self.new_user_window, text="Save Profile", command=self.save_new_user_data)
        save_button.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

    # This method saves the new user data from the dialog/form.
    def save_new_user_data(self):
        # Gather data from form fields
        data = {field: entry.get() for field, entry in self.new_user_entries.items()}
        dod_id = data.get('DoD ID', '')

        # Validate the DoD ID
        if not dod_id.isdigit() or len(dod_id) != 10:
            messagebox.showerror("Error", "DoD ID must be exactly 10 digits.")
            return

        try:
            user_profile = UserProfile(
                dod_id=dod_id,  # Use dod_id here consistently
                name=data.get('Name', ''),
                date_of_birth=data.get('Date of Birth', ''),
                marital_status=data.get('Marital Status', ''),
                disability_rating=int(data.get('Disability Rating', '0')),
                spouse=data.get('Spouse', None),
                dependents=[dep.strip() for dep in data.get('Dependents', '').split(',') if dep.strip()],
            )
            filepath = os.path.join(os.getcwd(), f"{dod_id}.json")  # Filename is now correctly based on dod_id
            with open(filepath, 'w') as file:
                # Assuming your UserProfile class has a method to_dict() to convert the object into a dictionary
                json.dump(user_profile.to_dict(), file)
            
            messagebox.showinfo("Success", "Profile saved successfully.")
            self.new_user_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    # Load an existing user profile from a JSON file, if it exists.
    def load_user(self, dod_id):
        file_path = os.path.join(os.getcwd(), f"{dod_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            user_profile = UserProfile(**data)
            self.show_user_info_frame(user_profile)
        else:
            tk.messagebox.showerror("Error", f"No such user: {dod_id}")
            return None

    def show_user_info_frame(self, user_profile):
        if self.user_info_frame is not None:
            self.user_info_frame.destroy()

        self.user_info_frame = UserInfoFrame(self, user_profile)  # Correctly initializes the UserInfoFrame with the user profile
        self.user_info_frame.pack(fill="both", expand=True)

    # Placeholder functions for editing profiles. To be implemented.
    def edit_profile(self):
        messagebox.showinfo("Edit Profile", "Profile editing functionality not implemented yet.")
    
    def edit_personal_data(self, user_profile):
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Personal Data")
        edit_window.geometry("400x500")  # Adjust size as necessary

        # Create and layout the edit fields
        fields = ['Name', 'Date of Birth', 'Marital Status', 'DoD ID']
        entries = {}
        for idx, field in enumerate(fields, start=1):
            # Use the correct attribute from user_profile for the initial value
            initial_value = getattr(user_profile, field.lower().replace(" ", "_"), "") if field != 'DoD ID' else user_profile.dod_id
            tk.Label(edit_window, text=f"{field}:").grid(row=idx, column=0, sticky="e", padx=10, pady=5)
            entry_var = tk.StringVar(value=initial_value)
            entry = tk.Entry(edit_window, textvariable=entry_var)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry_var

        # Special handling for dependents (simplified for now)
        tk.Label(edit_window, text="Dependents:").grid(row=len(fields)+1, column=0, sticky="e", padx=10, pady=5)
        dependents_var = tk.StringVar(value=','.join(user_profile.dependents))
        dependents_entry = tk.Entry(edit_window, textvariable=dependents_var)
        dependents_entry.grid(row=len(fields)+1, column=1, padx=10, pady=5)
        entries['Dependents'] = dependents_var

        # Correctly refer to the user_profile.dod_id in the print statement if needed
        print("Editing profile for DoD ID:", user_profile.dod_id)

        # Adjust save button command to correctly pass user_profile and entry data
        save_button = tk.Button(edit_window, text="Save", command=lambda: self.save_user_data(user_profile, entries))
        save_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

        
    def save_user_data(self, user_profile, entries):
        # Example: Update the user profile with new data
        user_profile.name = entries['Name'].get()
        user_profile.date_of_birth = entries['Date of Birth'].get()
        user_profile.marital_status = entries['Marital Status'].get()
        user_profile.dod_id = entries['DoD ID'].get()
        user_profile.dependents = entries['Dependents'].get().split(',')
        messagebox.showinfo("Success", "Profile updated successfully.")

    # Placeholder functions for opening regulations. To be implemented.
    def open_regulations(self):
        messagebox.showinfo("38 CFR Regulations", "Regulations viewing functionality not implemented yet.")

    # 
    def load_user(self, dod_id):
        file_path = os.path.join(os.getcwd(), f"{dod_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            user_profile = UserProfile(**data)
            self.show_user_info_frame(user_profile)
        else:
            tk.messagebox.showerror("Error", f"No such user: {dod_id}")
            return None

# UserProfile class: Represents a user/veteran profile, including personal and disability-related information.
class UserProfile:
    # Ensure there's only one dod_id parameter in the method signature.
    def __init__(self, dod_id, name="", disability_rating=0, spouse=None, children=None, 
                 spouse_aid_attendance=False, date_of_birth="", 
                 marital_status="", dependents=[]):
        self.dod_id = dod_id
        self.name = name
        self.disability_rating = disability_rating
        self.spouse = spouse
        self.children = children if children is not None else []
        self.spouse_aid_attendance = spouse_aid_attendance
        self.date_of_birth = date_of_birth
        self.marital_status = marital_status
        self.dependents = dependents

      # Method to calculate benefits based on the user's profile. Utilizes a placeholder class `CalculateBenefits`.
    def calculate_benefits(self):
        """
        Calculate the benefits using the CalculateBenefits class.
        :return: The monthly payment based on the veteran's profile.
        Need to get correct math from 38CFR Audit doc?
        """
        benefits_calculator = CalculateBenefits(
            disability_rating=self.disability_rating,
            spouse=bool(self.spouse),
            children=self.children,
            spouse_a_and_a=self.spouse_aid_attendance
        )
        return benefits_calculator.get_monthly_payment()

# UserInfoFrame class: A frame to display and edit information about the user profile. Includes functionality to add dependents.
# update to modify the first instead of replacing it
class UserInfoFrame(tk.Frame):
    def __init__(self, parent, user_profile, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.user_profile = user_profile
        self.init_ui()

    def init_ui(self):

        tk.Label(self, text="Disability Rating:").grid(row=6, column=0, sticky="w")
        self.disability_rating_var = tk.StringVar()
        disability_options = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
        self.disability_rating_dropdown = ttk.Combobox(self, textvariable=self.disability_rating_var, values=disability_options, state="readonly")
        self.disability_rating_dropdown.grid(row=6, column=1, sticky="w")
        self.disability_rating_dropdown.set("0")  # Default to 0%
        
        tk.Button(self, text="Calculate Benefits", command=self.calculate_benefits).grid(row=7, column=0, columnspan=2)

    # CalculateBenefits class: Calculates the estimated monthly benefits based on disability rating, marital status, and dependents.
    def calculate_benefits(self):
        children_info = []
        for entry in self.children_entries:
            child_name = entry.get()
            if child_name:  # Assuming additional child info could be managed here
                children_info.append({'name': child_name, 'age': 18, 'in_school': False})  # Example structure

        # Initialize CalculateBenefits with current user info
        benefits_calculator = CalculateBenefits(
            disability_rating=int(self.disability_rating_var.get()),
            spouse=bool(self.spouse_name_var.get()),
            children=children_info,
            spouse_a_and_a=self.user_profile.spouse_aid_attendance
        )

        monthly_payment = benefits_calculator.get_monthly_payment()

        # Display the calculated benefits
        messagebox.showinfo("Benefits Calculation", f"Estimated Monthly Payment: ${monthly_payment}")

class UserInfoFrame(tk.Frame):
    def __init__(self, parent, user_profile, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.user_profile = user_profile
        self.children_entries = []  # To keep track of children/dependents entries
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text=f"Profile: {self.user_profile.dod_id}").grid(row=0, columnspan=3, pady=(10, 10))

        # Checkbox for spouse
        self.has_spouse_var = tk.BooleanVar(value=bool(self.user_profile.spouse))
        tk.Checkbutton(self, text="Has Spouse?", variable=self.has_spouse_var, command=self.toggle_spouse_fields).grid(row=1, column=0, sticky="w")
        self.spouse_name_var = tk.StringVar(value=self.user_profile.spouse)
        self.spouse_name_entry = tk.Entry(self, textvariable=self.spouse_name_var)
        self.spouse_name_entry.grid(row=1, column=1, sticky="ew")
        tk.Button(self, text="Remove", command=self.remove_spouse).grid(row=1, column=2)

        # Checkbox for children
        self.has_children_var = tk.BooleanVar(value=bool(self.user_profile.children))
        tk.Checkbutton(self, text="Has Children/Dependents?", variable=self.has_children_var, command=self.toggle_children_fields).grid(row=2, column=0, sticky="w")
        self.add_child_button = tk.Button(self, text="+ Add Child/Dependent", command=self.add_child_entry)
        self.add_child_button.grid(row=3, column=0, sticky="ew", pady=5)

        self.save_button = tk.Button(self, text="Save Profile", command=self.save_profile)
        self.save_button.grid(row=100, column=0, columnspan=3, pady=10)

        # Initial toggle to match profile state
        self.toggle_spouse_fields()
        self.toggle_children_fields()

    def toggle_spouse_fields(self):
        if self.has_spouse_var.get():
            self.spouse_name_entry.grid()
        else:
            self.spouse_name_entry.grid_remove()

    def remove_spouse(self):
        self.has_spouse_var.set(False)
        self.toggle_spouse_fields()

    def toggle_children_fields(self):
        if not self.has_children_var.get():
            for entry, delete_button in self.children_entries:
                entry.grid_remove()
                delete_button.grid_remove()
            self.children_entries = []
            self.add_child_button.grid_remove()
        else:
            self.add_child_button.grid()

    def add_child_entry(self):
        row = 4 + len(self.children_entries)
        child_name_var = tk.StringVar()
        child_entry = tk.Entry(self, textvariable=child_name_var)
        child_entry.grid(row=row, column=1, sticky="ew")
        
        delete_button = tk.Button(self, text="Remove", command=lambda: self.remove_child_entry(child_entry, delete_button))
        delete_button.grid(row=row, column=2)
        
        self.children_entries.append((child_entry, delete_button))

    def remove_child_entry(self, child_entry, delete_button):
        child_entry.destroy()
        delete_button.destroy()
        self.children_entries = [(e, b) for e, b in self.children_entries if e != child_entry]
        self.reposition_child_entries()

    def reposition_child_entries(self):
        for index, (entry, button) in enumerate(self.children_entries, start=4):
            entry.grid(row=index, column=1, sticky="ew")
            button.grid(row=index, column=2)

    def save_profile(self):
        self.user_profile.spouse = self.spouse_name_var.get() if self.has_spouse_var.get() else None
        self.user_profile.children = [entry.get() for entry, _ in self.children_entries]
        messagebox.showinfo("Success", "Profile updated successfully.")

class DisabilitySelectionFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.lbl = tk.Label(self, text="Select Disability Category:")
        self.lbl.pack(pady=10)

        # Example categories, replace with dynamic API call results
        self.categories = ["Category 1", "Category 2", "Category 3"]
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self, textvariable=self.category_var, values=self.categories)
        self.category_dropdown.pack()
        self.category_dropdown.bind("<<ComboboxSelected>>", self.on_category_selected)

        # Placeholder for the next level of dropdowns, e.g., specific disabilities
        self.specific_var = tk.StringVar()
        self.specific_dropdown = ttk.Combobox(self, textvariable=self.specific_var)
        self.specific_dropdown.pack()

    def on_category_selected(self, event):
        # Dynamically fetch and update the next dropdown based on the selection
        # Placeholder values, replace with dynamic API call results based on the selected category
        specifics = ["Specific 1", "Specific 2", "Specific 3"]
        self.specific_dropdown['values'] = specifics

class CalculateBenefits:
    def __init__(self, disability_rating, spouse=False, children=[], spouse_a_and_a=False):
        self.disability_rating = disability_rating
        self.spouse = spouse
        self.children = children
        self.spouse_a_and_a = spouse_a_and_a

    def get_monthly_payment(self):
        # Base rates for disability
        base_rates = {
            10: 171.23,
            20: 338.49,
            30: 524.31,
            40: 755.28,
            50: 1075.16,
            60: 1361.88,
            70: 1716.28,
            80: 1995.01,
            90: 2241.91,
            100: 3737.85,
        }

        # Ensure disability rating is within the expected range
        if self.disability_rating not in base_rates:
            return 0

        base_payment = base_rates[self.disability_rating]

        # For disability ratings less than 30%
        if self.disability_rating < 30:
            return base_payment

        # Adjustments for spouse and children
        if self.disability_rating >= 30:
            spouse_payment = 0
            child_payment = 0

            if self.spouse:
                spouse_payment += 150.25  # Example rate, adjust based on tables
                if self.spouse_a_and_a:
                    spouse_payment += 134.00  # Spouse Aid and Attendance

            for child in self.children:
                if child['age'] < 18:
                    child_payment += 72.00
                elif child['in_school']:
                    child_payment += 234.00

            return base_payment + spouse_payment + child_payment

        return base_payment

class Disability:
    def __init__(self, name, diagnostic_code, rating, notes=None):
        self.name = name
        self.diagnostic_code = diagnostic_code
        self.rating = rating
        self.notes = notes


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

