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

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.user_data = {"username": "", "preferences": {}, "data": {}}
        self.configure_application()
        self.create_menus()
        self.initialize_ui()

    def configure_application(self):
        self.title("Triage - a VA Disability Claim assistant")
        self.configure(bg="black")
        self.geometry("800x600")  # Width x Height

    def create_menus(self):
        self.menu_bar = tk.Menu(self, bg="black", fg="gold")
        
        # File menu
        self.add_menu_item("File", [("Exit", self.on_exit)])
        
        # User Profile
        self.add_menu_item("Profile", [("Edit Profile", self.edit_profile)])
        
        # Resources
        self.add_menu_item("Resources", [("38 CFR Regulations", self.open_regulations)])
        
        self.config(menu=self.menu_bar)

    def add_menu_item(self, menu_title, commands):
        menu = tk.Menu(self.menu_bar, tearoff=0, bg="black", fg="gold")
        for label, command in commands:
            menu.add_command(label=label, command=command)
        self.menu_bar.add_cascade(label=menu_title, menu=menu)

    def initialize_ui(self):
        self.main_frame = tk.Frame(self, bg="black")
        self.main_frame.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        welcome_label = tk.Label(self.main_frame, text="Welcome to Triage!", bg="black", fg="gold")
        welcome_label.pack(pady=10)

        # New Person Button
        new_person_button = tk.Button(self.main_frame, text="New Person", command=self.new_user_dialog, bg="black", fg="gold")
        new_person_button.pack(side="left", padx=(100, 20), pady=20)

        # Load Person Button
        load_person_button = tk.Button(self.main_frame, text="Load Person", command=self.load_user_dialog, bg="black", fg="gold")
        load_person_button.pack(side="right", padx=(20, 100), pady=20)

    def on_exit(self):
        if messagebox.askokcancel("Exit", "Do you really wish to exit?", icon='warning'):
            self.destroy()

    def ask_user_action(self):
        action = messagebox.askquestion("User Action", "Load existing user?")
        if action == 'yes':
            self.load_user_dialog()
        else:
            self.new_user_dialog()

    def load_user_dialog(self):
        username = simpledialog.askstring("Load User", "Enter username to load:")
        if username:
            self.load_user(username)

    def create_new_user(self, username):
        user_profile = UserProfile(username=username)
        self.show_user_info_frame(user_profile)

        user_data = {
            "username": username,
            "preferences": {},
            "data": {},
            "disabilities": []  # Placeholder for disability information
        }
        # Save user data to a file
        file_path = os.path.join(os.getcwd(), f"{username}.json")
        with open(file_path, 'w') as file:
            json.dump(user_data, file)
        print(f"User {username} created successfully.")

    def load_user(self, username):
        file_path = os.path.join(os.getcwd(), f"{username}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            user_profile = UserProfile(**data)
            self.show_user_info_frame(user_profile)
        else:
            tk.messagebox.showerror("Error", f"No such user: {username}")
            return None

    def show_user_info_frame(self, user_profile):
        self.main_frame.pack_forget()
        user_info_frame = UserInfoFrame(self, user_profile)
        user_info_frame.pack(fill="both", expand=True)

    def new_user_dialog(self):
        username = simpledialog.askstring("New User", "Enter new username:")
        if username:
            self.create_new_user(username)
            self.show_user_info_frame(username)  # Transition to the user info frame
    
    def edit_profile(self):
        messagebox.showinfo("Edit Profile", "Profile editing functionality not implemented yet.")
    
    def open_regulations(self):
        messagebox.showinfo("38 CFR Regulations", "Regulations viewing functionality not implemented yet.")

    def load_user(self, username):
        file_path = os.path.join(os.getcwd(), f"{username}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            user_profile = UserProfile(**data)
            self.show_user_info_frame(user_profile)
        else:
            tk.messagebox.showerror("Error", f"No such user: {username}")
            return None


class UserProfile:
    def __init__(self, username, disability_rating=0, spouse=None, children=None, spouse_aid_attendance=False):
        """
        Initialize a UserProfile instance.
        :param username: The username of the veteran.
        :param disability_rating: The disability rating of the veteran.
        :param spouse: Indicates if the veteran has a spouse.
        :param children: A list of children.
        :param spouse_aid_attendance: Indicates if the spouse receives Aid and Attendance benefits.
        """
        self.username = username
        self.disability_rating = disability_rating
        self.spouse = spouse
        self.children = children if children is not None else []
        self.spouse_aid_attendance = spouse_aid_attendance

    def calculate_benefits(self):
        """
        Calculate the benefits using the CalculateBenefits class.
        :return: The monthly payment based on the veteran's profile.
        """
        benefits_calculator = CalculateBenefits(
            disability_rating=self.disability_rating,
            spouse=bool(self.spouse),
            children=self.children,
            spouse_a_and_a=self.spouse_aid_attendance
        )
        return benefits_calculator.get_monthly_payment()


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
        tk.Label(self, text=f"Profile: {self.user_profile.username}").grid(row=0, columnspan=3, pady=(10, 10))

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

