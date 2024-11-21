import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import yaml_lib
from main import FamilyTree
from family_lib import Parent, Child, Partner
from datetime import datetime

class FamilyTreeGUI:
    def __init__(self, save_file="na"):
        # Create FamilyTree instance to handle logic
        self.ft = FamilyTree(save_file)
        self.root = None
        self.selected_person = None

    def remove_relationship_dialog(self):
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Remove Relationship")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Select relationship type:").pack(pady=5)
        rel_type = ttk.Combobox(dialog, values=["Parent-Child", "Siblings", "Partners"])
        rel_type.pack(pady=5)

        ttk.Label(dialog, text="Select person:").pack(pady=5)
        other_person = ttk.Combobox(dialog, values=[p.name for p in self.ft.family if p != self.selected_person])
        other_person.pack(pady=5)

        def submit():
            if not all([rel_type.get(), other_person.get()]):
                messagebox.showerror("Error", "All fields are required!")
                return

            other = next(p for p in self.ft.family if p.name == other_person.get())
            
            try:
                if rel_type.get() == "Parent-Child":
                    self.selected_person.remove_person(other)
                elif rel_type.get() == "Siblings":
                    self.selected_person.remove_sibling(other)
                elif rel_type.get() == "Partners":
                    self.selected_person.remove_partner(other)
                messagebox.showinfo("Success", "Relationship removed successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

            dialog.destroy()

        ttk.Button(dialog, text="Remove Relationship", command=submit).pack(pady=10)

    def display_family(self):
        self.root = tk.Tk()
        self.root.title("Family Tree Manager")
        self.root.geometry("800x600")

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Left panel - Family list
        left_frame = ttk.LabelFrame(main_frame, text="Family Members", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        self.family_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.family_listbox.pack(fill=tk.BOTH, expand=True)
        self.family_listbox.bind('<<ListboxSelect>>', self.on_select_person)

        # Right panel - Actions
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add Person section
        add_frame = ttk.LabelFrame(right_frame, text="Add Person", padding="5")
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Button(add_frame, text="Add Parent", command=lambda: self.add_person_dialog("Parent")).pack(fill=tk.X, pady=2)
        ttk.Button(add_frame, text="Add Child", command=lambda: self.add_person_dialog("Child")).pack(fill=tk.X, pady=2)
        ttk.Button(add_frame, text="Add Partner", command=lambda: self.add_person_dialog("Partner")).pack(fill=tk.X, pady=2)

        # Relationships section
        rel_frame = ttk.LabelFrame(right_frame, text="Relationships", padding="5")
        rel_frame.pack(fill=tk.X, pady=5)

        ttk.Button(rel_frame, text="Add Relationship", command=self.add_relationship_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(rel_frame, text="Remove Relationship", command=self.remove_relationship_dialog).pack(fill=tk.X, pady=2)

        # View section
        view_frame = ttk.LabelFrame(right_frame, text="View Information", padding="5")
        view_frame.pack(fill=tk.X, pady=5)

        ttk.Button(view_frame, text="View Parents", command=lambda: self.show_relatives("parents")).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="View Siblings", command=lambda: self.show_relatives("siblings")).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="View Children", command=lambda: self.show_relatives("children")).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="View Extended Family", command=self.show_extended_family).pack(fill=tk.X, pady=2)

        # Statistics section
        stats_frame = ttk.LabelFrame(right_frame, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)

        ttk.Button(stats_frame, text="Average Age", command=self.show_average_age).pack(fill=tk.X, pady=2)
        ttk.Button(stats_frame, text="Show Birthdays", command=self.show_birthdays).pack(fill=tk.X, pady=2)

        # Save/Exit section
        save_frame = ttk.Frame(right_frame, padding="5")
        save_frame.pack(fill=tk.X, pady=5)

        ttk.Button(save_frame, text="New Family Tree", command=self.new_family).pack(fill=tk.X, pady=2)
        ttk.Button(save_frame, text="Save Family Tree", command=self.save_family).pack(fill=tk.X, pady=2)
        ttk.Button(save_frame, text="Load Family Tree", command=self.load_family).pack(fill=tk.X, pady=2)
        ttk.Button(save_frame, text="Exit", command=self.exit_program).pack(fill=tk.X, pady=2)

        self.refresh_family_list()
        self.root.mainloop()

    def refresh_family_list(self):
        self.family_listbox.delete(0, tk.END)
        for person in self.ft.family:
            self.family_listbox.insert(tk.END, f"{person.name} ({person.__class__.__name__})")

    def add_person_dialog(self, person_type):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add {person_type}")
        dialog.geometry("300x250")

        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Date of Birth (YYYY-MM-DD):").pack(pady=5)
        dob_entry = ttk.Entry(dialog)
        dob_entry.pack(pady=5)

        ttk.Label(dialog, text="Ethnicity:").pack(pady=5)
        ethnicity_entry = ttk.Entry(dialog)
        ethnicity_entry.pack(pady=5)

        alive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Is Alive", variable=alive_var).pack(pady=5)

        def submit():
            name = name_entry.get()
            dob = dob_entry.get()
            ethnicity = ethnicity_entry.get()
            is_alive = alive_var.get()

            if not all([name, dob, ethnicity]):
                messagebox.showerror("Error", "All fields are required!")
                return

            person_classes = {"Parent": Parent, "Child": Child, "Partner": Partner}
            new_person = person_classes[person_type](name, dob, is_alive, ethnicity)
            self.ft.family.append(new_person)
            self.refresh_family_list()
            dialog.destroy()

        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)

    def add_relationship_dialog(self):
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Relationship")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Select relationship type:").pack(pady=5)
        rel_type = ttk.Combobox(dialog, values=["Parent-Child", "Siblings", "Partners"])
        rel_type.pack(pady=5)

        ttk.Label(dialog, text="Select other person:").pack(pady=5)
        other_person = ttk.Combobox(dialog, values=[p.name for p in self.ft.family if p != self.selected_person])
        other_person.pack(pady=5)

        def submit():
            if not all([rel_type.get(), other_person.get()]):
                messagebox.showerror("Error", "All fields are required!")
                return

            other = next(p for p in self.ft.family if p.name == other_person.get())
            
            try:
                if rel_type.get() == "Parent-Child":
                    self.selected_person.add_person(other)
                elif rel_type.get() == "Siblings":
                    self.selected_person.add_sibling(other)
                elif rel_type.get() == "Partners":
                    self.selected_person.add_partner(other)
                messagebox.showinfo("Success", "Relationship added successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

            dialog.destroy()

        ttk.Button(dialog, text="Add Relationship", command=submit).pack(pady=10)

    def on_select_person(self, event):
        selection = self.family_listbox.curselection()
        if selection:
            self.selected_person = self.ft.family[selection[0]]

    def show_relatives(self, relative_type):
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        # Use the display methods from FamilyTree class
        if relative_type == "parents":
            self.ft.display_parents(self.selected_person)
        elif relative_type == "siblings":
            self.ft.display_siblings(self.selected_person)
        elif relative_type == "children":
            self.ft.display_children(self.selected_person)

    def show_extended_family(self):
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return
        
        self.ft.display_extended_family(self.selected_person)

    def show_average_age(self):
        avg_age = self.ft.calc_avage()
        if avg_age:
            messagebox.showinfo("Average Age", f"The average age is {avg_age:.1f} years")
        else:
            messagebox.showinfo("Average Age", "No valid ages to calculate average")

    def show_birthdays(self):
        birthdays = []
        for member in self.ft.family:
            try:
                dob = datetime.strptime(member.dob, "%Y-%m-%d")
                birthdays.append(f"{member.name}: {dob.strftime('%B %d, %Y')}")
            except ValueError:
                continue
        
        if birthdays:
            birthday_text = "\n".join(birthdays)
            messagebox.showinfo("Birthdays", birthday_text)
        else:
            messagebox.showinfo("Birthdays", "No birthdays recorded")

    def save_family(self):
        yaml_lib.yaml_export(self.ft.family)
        messagebox.showinfo("Success", "Family tree saved successfully!")

    def exit_program(self):
        if messagebox.askyesno("Exit", "Do you want to save before exiting?"):
            self.save_family()
        self.root.quit()

    def load_family(self):
        """Load a family tree from a save file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            initialdir="./saves",
            title="Select save file",
            filetypes=(("YAML files", "*.yaml"), ("all files", "*.*"))
        )
        if filename:
            self.ft = FamilyTree(filename)
            self.refresh_family_list()
            messagebox.showinfo("Success", "Family tree loaded successfully!")

    def new_family(self):
        """Create a new empty family tree"""
        if messagebox.askyesno("New Family Tree", "Are you sure you want to create a new family tree? Any unsaved changes will be lost."):
            self.ft = FamilyTree("na")  # Create new empty family tree
            self.refresh_family_list()  # Clear the display
            messagebox.showinfo("Success", "New family tree created!")
