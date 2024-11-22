import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import yaml_lib
from main import FamilyTree
from family_lib import Parent, Child, Partner
from datetime import datetime
import os

class FamilyTreeGUI:
    def __init__(self, save_file="na"):
        self.root = None
        self.selected_person = None

        # Debug print for save_file path
        print(f"Attempting to load save file: {save_file}")

        # Ensure the save file path is correct
        if save_file != "na" and not os.path.isabs(save_file):
            save_file = os.path.join(os.getcwd(), save_file)
            print(f"Absolute path: {save_file}")

        # Initialize FamilyTree with the save file
        self.ft = FamilyTree(save_file)

        # Debug prints
        if hasattr(self.ft, 'family'):
            print(f"Loaded {len(self.ft.family)} family members")
            for member in self.ft.family:
                print(f"- {member.name} ({type(member).__name__})")
        else:
            print("No family attribute found in FamilyTree instance")

        # Mapping from person to unique ID
        self.members = {}
        for idx, person in enumerate(self.ft.family):
            person.id = idx
            self.members[person.id] = person

    def load_family(self):
        """Load a family tree from a save file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            initialdir="./saves",
            title="Select save file",
            filetypes=(("YAML files", "*.yaml"), ("all files", "*.*"))
        )
        if filename:
            try:
                print(f"Loading file: {filename}")  # Debug print
                self.ft = FamilyTree(filename)
                print(f"Family tree loaded, members: {len(self.ft.family)}")  # Debug print
                self.refresh_family_list()
                messagebox.showinfo("Success", f"Family tree loaded successfully! {len(self.ft.family)} members loaded.")
            except Exception as e:
                print(f"Error loading family tree: {str(e)}")  # Debug print
                messagebox.showerror("Error", f"Failed to load family tree: {str(e)}")

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
                self.draw_family_tree()  # Redraw the tree
            except Exception as e:
                messagebox.showerror("Error", str(e))

            dialog.destroy()

        ttk.Button(dialog, text="Remove Relationship", command=submit).pack(pady=10)

    def display_family(self):
        self.root = tk.Tk()
        self.root.title("Family Tree Manager")
        self.root.geometry("1000x800")
        self.root.minsize(1000, 800)

        # Configure the main window grid
        self.root.grid_rowconfigure(0, weight=1)  # Main content area
        self.root.grid_rowconfigure(1, weight=0)  # Bottom button area
        self.root.grid_columnconfigure(0, weight=0)  # Left panel
        self.root.grid_columnconfigure(1, weight=1)  # Right panel (canvas)

        # Left Panel: Family Members
        left_frame = ttk.LabelFrame(self.root, text="Family Members", padding="5")
        left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        self.family_listbox = tk.Listbox(left_frame)
        self.family_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.family_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.family_listbox.configure(yscrollcommand=scrollbar.set)
        self.family_listbox.bind('<<ListboxSelect>>', self.on_select_person)

        # Canvas: Right Panel (Big Rectangle)
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Create a scrollable canvas
        self.canvas = tk.Canvas(canvas_frame, background="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Create a frame inside the canvas
        self.canvas_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        # Update scroll region whenever the frame size changes
        self.canvas_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bottom Buttons
        bottom_frame = ttk.Frame(self.root, padding="5")
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        for i in range(5):
            bottom_frame.grid_columnconfigure(i, weight=1)

        ttk.Button(bottom_frame, text="Add Person", command=lambda: self.add_person_dialog("Parent")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(bottom_frame, text="Add Relationship", command=self.add_relationship_dialog).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(bottom_frame, text="Remove Relationship", command=self.remove_relationship_dialog).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(bottom_frame, text="Save Family", command=self.save_family).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(bottom_frame, text="Exit", command=self.exit_program).grid(row=0, column=4, padx=5, pady=5)

        # Populate the family listbox with sample data
        self.refresh_family_list()

        # Draw the family tree
        self.draw_family_tree()

        self.root.mainloop()


    def refresh_family_list(self):
        """Refresh the family list display"""
        self.family_listbox.delete(0, tk.END)  # Clear current list

        if not hasattr(self.ft, 'family') or not self.ft.family:
            self.family_listbox.insert(tk.END, "No family members added yet")
            self.family_listbox.itemconfig(0, {'fg': 'gray'})
            return

        # Debug print
        print(f"Number of family members: {len(self.ft.family)}")

        for person in self.ft.family:
            try:
                display_text = f"{person.name} ({person.__class__.__name__})"
                print(f"Adding to list: {display_text}")  # Debug print
                self.family_listbox.insert(tk.END, display_text)
            except Exception as e:
                print(f"Error adding person to list: {e}")  # Debug print
                messagebox.showerror("Error", f"Error loading family member: {e}")

        # Redraw the family tree
        self.draw_family_tree()

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
            new_person.id = len(self.members)  # Assign a unique ID
            self.ft.family.append(new_person)
            self.members[new_person.id] = new_person  # Add to members mapping
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
                self.draw_family_tree()  # Redraw the tree
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

    def new_family(self):
        """Create a new empty family tree"""
        if messagebox.askyesno("New Family Tree", "Are you sure you want to create a new family tree? Any unsaved changes will be lost."):
            self.ft = FamilyTree("na")  # Create new empty family tree
            self.members = {}  # Reset members mapping
            self.refresh_family_list()  # Clear the display
            messagebox.showinfo("Success", "New family tree created!")


    def assign_levels(self):
        # Assign level to each person based on their depth in the hierarchy
        def assign_level_recursively(person):
            if person in self.levels:
                return self.levels[person]
            if not hasattr(person, 'parents') or len(person.parents) == 0:
                self.levels[person] = 0
            else:
                parent_levels = [assign_level_recursively(parent) for parent in person.parents]
                self.levels[person] = max(parent_levels) + 1
            return self.levels[person]

        for person in self.ft.family:
            assign_level_recursively(person)

    def calculate_positions(self):
        # Organize persons by level for horizontal positioning
        levels_to_persons = {}
        for person, level in self.levels.items():
            if level not in levels_to_persons:
                levels_to_persons[level] = []
            levels_to_persons[level].append(person)

        # Calculate positions for each person
        positions = {}
        vertical_spacing = 200
        person_div_width = 150
        person_div_height = 100

        max_level = max(self.levels.values()) if self.levels else 0

        for level, persons_in_level in levels_to_persons.items():
            spacing = (1600 - len(persons_in_level) * person_div_width) // (len(persons_in_level) + 1)
            for index, person in enumerate(persons_in_level):
                positions[person] = {
                    'x': spacing + (person_div_width + spacing) * index + 75,
                    'y': (level) * vertical_spacing + 50  # Adjusted to place parents at the top
                }

        return positions

    def draw_family_tree(self):
        self.node_positions = {}
        self.canvas.delete("all")

        if not self.ft.family:
            return

        # Assign levels to each person
        self.levels = {}
        self.assign_levels()

        # Determine positioning based on levels
        self.positions = self.calculate_positions()

        # Draw each person node
        for person, position in self.positions.items():
            self.draw_person(person, position['x'], position['y'])

        # Draw lines for relationships
        self.draw_relationships()
        max_x, max_y = 0, 0
        for position in self.positions.values():
            x, y = position['x'], position['y']
            max_x = max(max_x, x + 75)  # Adding half the width of the box to get the right edge
            max_y = max(max_y, y + 50)  # Adding half the height of the box to get the bottom edge

        # Set the canvas scroll region to include all drawn elements
        self.canvas.configure(scrollregion=(0, 0, max_x + 100, max_y + 100))  # Adding a bit of padding

    def draw_person(self, person, x, y):
        # Draw the person box with details
        self.node_positions[person] = (x, y)
        self.canvas.create_rectangle(x - 75, y - 50, x + 75, y + 50, fill="grey", outline="white")
        text = (
            f"{person.name}\n"
            f"DOB: {person.dob}\n"
            f"Alive: {'Yes' if person.is_alive else 'No'}\n"
            f"Ethnicity: {person.ethnicity}"
        )
        self.canvas.create_text(x, y, text=text, fill="white")

    def draw_relationships(self):
        # Draw lines for parent-child relationships only
        for person in self.ft.family:
            # Draw lines from parents to their children
            if hasattr(person, 'children'):
                for child in person.children:
                    self.draw_line(person, child, color='red')

    def draw_line(self, parent, child, color='red'):
        # Draw a straight line from the bottom of the parent to the top of the child
        if parent not in self.node_positions or child not in self.node_positions:
            return

        x1, y1 = self.node_positions[parent]
        x2, y2 = self.node_positions[child]

        self.canvas.create_line(x1, y1 + 50, x2, y2 - 50, fill=color)

# You can run the GUI by creating an instance of FamilyTreeGUI and calling display_family()
if __name__ == "__main__":
    gui = FamilyTreeGUI()
    gui.display_family()
