import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import os

# Global variables to hold family data and the filename
family_data = {}
filename = ""  # Will be set when loading the XML file
family_tree_window = None
# Function to load family data from XML
def load_from_xml(file_path):
    global family_data
    family_data = {}

    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"File '{file_path}' not found.")
        return

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for person in root.findall('person'):
            person_id = person.get('id')
            name = person.get('name')
            birth_date = person.get('birth_date')
            status = person.get('status') == "alive"
            parents = [p.text for p in person.findall('parent_id')]
            children = [c.text for c in person.findall('child_id')]
            partners = [p.text for p in person.findall('partner_id')]

            family_data[person_id] = {
                "name": name,
                "birth_date": birth_date,
                "alive": status,
                "parents": parents,
                "children": children,
                "partners": partners
            }

        print("Loaded family data:", family_data)  # Debugging print
        update_listbox()
        draw_family_tree()  # Draw family tree after loading data

    except ET.ParseError:
        messagebox.showerror("Error", "Error parsing the XML file.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to save family data to XML
def save_to_xml():
    if not filename:
        messagebox.showerror("Error", "No file loaded to save data.")
        return

    root = ET.Element("family")
    for person_id, person_info in family_data.items():
        person = ET.SubElement(root, "person")
        person.set("id", person_id)
        person.set("name", person_info["name"])
        person.set("birth_date", person_info["birth_date"])
        person.set("status", "alive" if person_info["alive"] else "deceased")

        for parent_id in person_info["parents"]:
            parent = ET.SubElement(person, "parent_id")
            parent.text = parent_id
        for child_id in person_info["children"]:
            child = ET.SubElement(person, "child_id")
            child.text = child_id
        for partner_id in person_info["partners"]:
            partner = ET.SubElement(person, "partner_id")
            partner.text = partner_id

    tree = ET.ElementTree(root)
    tree.write(filename)
    print(f"Saved family data to {filename}")  # Debugging print

# Function to add a person to the family data
def add_person(name, birth_date, alive, relationships):
    if not name or not birth_date:
        messagebox.showerror("Error", "Name and Birth Date cannot be blank.")
        return

    new_person_id = str(len(family_data) + 1)  # Use a new variable for ID generation
    family_data[new_person_id] = {
        "name": name,
        "birth_date": birth_date,
        "alive": alive,
        "parents": [],
        "children": [],
        "partners": []
    }
    
    print(f"Added Person - ID: {new_person_id}, Name: {name}, Birth Date: {birth_date}, Status: {'Alive' if alive else 'Deceased'}")  # Debugging print

    # Process relationships
    for rel_name, rel_type in relationships:
        print(f"Adding relationship: {rel_name} as {rel_type}")  # Debugging print
        for existing_person_id, person_info in family_data.items():
            if person_info['name'] == rel_name:
                if rel_type == "Parent":
                    family_data[existing_person_id]['children'].append(new_person_id)  # Update existing person
                    family_data[new_person_id]['parents'].append(existing_person_id)  # Update new person
                elif rel_type == "Child":
                    family_data[existing_person_id]['parents'].append(new_person_id)  # Update existing person
                    family_data[new_person_id]['children'].append(existing_person_id)  # Update new person
                elif rel_type == "Partner":
                    family_data[existing_person_id]['partners'].append(new_person_id)  # Update existing person
                    family_data[new_person_id]['partners'].append(existing_person_id)  # Update new person

    # Update the Listbox and draw family tree
    update_listbox()
    save_to_xml()
    draw_family_tree()  # Update family tree display


# Function to update the Listbox with current family members
def update_listbox():
    family_tree_listbox.delete(0, tk.END)  # Clear existing entries
    for person_id, person_info in family_data.items():
        family_tree_listbox.insert(tk.END, f"{person_info['name']} (ID: {person_id}) - {'Alive' if person_info['alive'] else 'Deceased'}")
    print("Updated Listbox with family members")  # Debugging print

# Function to load an XML file via dialog
def load_file():
    global filename
    filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if filename:
        load_from_xml(filename)

# Function to draw the family tree in a conventional layout
import tkinter as tk

# Assuming family_data is already defined with loaded XML data

# Define a global family_tree_window variable
family_tree_window = None

# Function to draw the family tree in a conventional layout
# Define a global grid size to prevent overlap
GRID_WIDTH = 300  # Width between each person in the x direction
GRID_HEIGHT = 300  # Height between each person in the y direction

# Function to draw the family tree in a structured grid layout
def draw_family_tree():
    global family_tree_window, canvas, person_positions  # Ensure we have access to the global variables

    # Close previous family tree window if it exists
    if family_tree_window is not None and family_tree_window.winfo_exists():
        family_tree_window.destroy()

    # Create a new window for displaying the family tree
    family_tree_window = tk.Toplevel()
    family_tree_window.title("Family Tree Viewer")
    family_tree_window.geometry("1000x800")

    # Frame for Canvas and Scrollbars
    canvas_frame = tk.Frame(family_tree_window)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    # Scrollbars
    x_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    y_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Canvas for displaying the family tree
    canvas = tk.Canvas(canvas_frame, width=1000, height=800, bg="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure scrollbars
    canvas.configure(xscrollcommand=x_scroll.set)
    canvas.configure(yscrollcommand=y_scroll.set)
    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)

    # Position tracking for each person
    person_positions = {}
    available_positions = {}  # New dictionary to track available grid positions

    # Function to draw a person and their relationships
    def draw_person(person_id, x, y, partner_spacing=80, child_spacing=120, parent_spacing=120):
        global canvas  # Access the global canvas variable

        if person_id in person_positions:  # Skip if already drawn
            return

        # Access the person's information
        person = family_data.get(person_id)
        if not person:
            return

        name = person.get("name", "Unknown")
        birth_date = person.get("birth_date", "Unknown")

        # Draw the person oval and text
        canvas.create_oval(x - 50, y - 30, x + 50, y + 30, fill="lightblue")
        canvas.create_text(x, y - 10, text=name, font=("Arial", 10, "bold"))
        canvas.create_text(x, y + 10, text=f"({birth_date})", font=("Arial", 9, "italic"))

        # Store position to avoid redrawing
        person_positions[person_id] = (x, y)

        # Draw partners
        partner_x = x + partner_spacing // 2  # Start position for partners
        for partner_id in person.get("partners", []):
            if partner_id not in person_positions:
                canvas.create_line(x + 50, y, partner_x - 50, y, fill="green", width=2)  # Line color for partners
                draw_person(partner_id, partner_x, y, partner_spacing, child_spacing, parent_spacing)
                partner_x += partner_spacing  # Move right for next partner

        # Draw children
        child_y = y + child_spacing
        if person.get("children"):
            child_x_start = x - (len(person["children"]) - 1) * (child_spacing // 2)
            for i, child_id in enumerate(person["children"]):
                if child_id not in person_positions:
                    canvas.create_line(x, y + 30, child_x_start + i * child_spacing, child_y - 30, fill="blue", width=2)  # Line color for children
                    draw_person(child_id, child_x_start + i * child_spacing, child_y, partner_spacing, child_spacing, parent_spacing)

        # Draw parents
        parent_y = y - parent_spacing
        if person.get("parents"):
            parent_x_start = x - (len(person["parents"]) - 1) * (parent_spacing // 2)
            for i, parent_id in enumerate(person["parents"]):
                if parent_id not in person_positions:
                    canvas.create_line(parent_x_start + i * parent_spacing, parent_y + 30, x, y - 30, fill="red", width=2)  # Line color for parents
                    draw_person(parent_id, parent_x_start + i * parent_spacing, parent_y, partner_spacing, child_spacing, parent_spacing)

    # Identify root people (those with no parents) to start drawing
    root_people = [pid for pid, pdata in family_data.items() if not pdata["parents"]]
    start_x = 100  # Starting x position for each root person
    for i, root_person in enumerate(root_people):
        draw_person(root_person, start_x + i * GRID_WIDTH, 100, partner_spacing=GRID_WIDTH, child_spacing=GRID_HEIGHT, parent_spacing=GRID_HEIGHT)

    # Update canvas scroll region to encompass all drawn elements
    canvas.config(scrollregion=canvas.bbox("all"))

# Note: Colors are assigned to lines based on the relationship type
# - Green for partners
# - Blue for children
# - Red for parents

# Update draw_person to ensure no overlaps







# Function to edit person details
def edit_person(person_id):
    if person_id not in family_data:
        messagebox.showerror("Error", "Selected person not found.")
        return

    person_info = family_data[person_id]

    # Create a new window for editing
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit {person_info['name']}")
    
    # Name entry
    tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(edit_window)
    name_entry.insert(0, person_info["name"])
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Birth date entry
    tk.Label(edit_window, text="Birth Date(YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    birth_date_entry = tk.Entry(edit_window)
    birth_date_entry.insert(0, person_info["birth_date"])
    birth_date_entry.grid(row=1, column=1, padx=5, pady=5)

    # Status checkbox
    tk.Label(edit_window, text="Alive:").grid(row=2, column=0, padx=5, pady=5)
    alive_var = tk.BooleanVar(value=person_info["alive"])
    tk.Checkbutton(edit_window, variable=alive_var).grid(row=2, column=1, padx=5, pady=5)

    # Save button
    def save_edit():
        new_name = name_entry.get()
        new_birth_date = birth_date_entry.get()
        new_alive_status = alive_var.get()
        if new_name and new_birth_date:
            family_data[person_id]['name'] = new_name
            family_data[person_id]['birth_date'] = new_birth_date
            family_data[person_id]['alive'] = new_alive_status
            update_listbox()
            draw_family_tree()
            print(f"Edited Person - ID: {person_id}, New Name: {new_name}, New Birth Date: {new_birth_date}, Status: {'Alive' if new_alive_status else 'Deceased'}")  # Debugging print
            edit_window.destroy()
        else:
            messagebox.showerror("Error", "Name and Birth Date cannot be blank.")

    tk.Button(edit_window, text="Save", command=save_edit).grid(row=3, columnspan=2, padx=5, pady=5)

# Main application window
main_window = tk.Tk()
main_window.title("Family Tree Application")

# Load and Save buttons
tk.Button(main_window, text="Load Family Tree", command=load_file).pack(pady=5)
tk.Button(main_window, text="Save Family Tree", command=save_to_xml).pack(pady=5)

# Listbox for displaying family members
family_tree_listbox = tk.Listbox(main_window, width=50, height=15)
family_tree_listbox.pack(pady=5)

# Add new person section
def add_new_person_window():
    add_window = tk.Toplevel(main_window)
    add_window.title("Add New Person")

    tk.Label(add_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(add_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_window, text="Birth Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    birth_date_entry = tk.Entry(add_window)
    birth_date_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(add_window, text="Alive:").grid(row=2, column=0, padx=5, pady=5)
    alive_var = tk.BooleanVar()
    tk.Checkbutton(add_window, variable=alive_var).grid(row=2, column=1, padx=5, pady=5)

    # Relationship section
    tk.Label(add_window, text="Relationships:").grid(row=3, column=0, padx=5, pady=5)

    relationships = []

    # Dropdown for selecting existing person
    def add_relationship():
        selected_name = existing_person_combobox.get()
        selected_relationship = relationship_combobox.get()
        if selected_name and selected_relationship:
            relationships.append((selected_name, selected_relationship))
            print(f"Relationship added: {selected_name} as {selected_relationship}")  # Debugging print
            update_relationships_display()

    existing_person_combobox = ttk.Combobox(add_window, values=list(family_data.values()), state="readonly")
    existing_person_combobox.grid(row=3, column=1, padx=5, pady=5)

    relationship_combobox = ttk.Combobox(add_window, values=["Parent", "Child", "Partner"], state="readonly")
    relationship_combobox.grid(row=4, column=1, padx=5, pady=5)

    tk.Button(add_window, text="Add Relationship", command=add_relationship).grid(row=5, columnspan=2, padx=5, pady=5)

    # Display added relationships
    relationships_display = tk.Listbox(add_window, width=50, height=5)
    relationships_display.grid(row=6, columnspan=2, padx=5, pady=5)

    def update_relationships_display():
        relationships_display.delete(0, tk.END)
        for rel_name, rel_type in relationships:
            relationships_display.insert(tk.END, f"{rel_name} - {rel_type}")

    # Button to save the new person
    tk.Button(add_window, text="Add Person", command=lambda: add_person(name_entry.get(), birth_date_entry.get(), alive_var.get(), relationships)).grid(row=7, columnspan=2, padx=5, pady=5)

# Button to open the add new person window
tk.Button(main_window, text="Add New Person", command=add_new_person_window).pack(pady=5)

# Start the main application loop
main_window.mainloop()
