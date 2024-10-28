import xml.etree.ElementTree as ET
import os

# Global variables to hold family data and the filename
family_data = {}
filename = ""

# Function to load family data from XML
def load_from_xml(file_path):
    global family_data
    family_data = {}

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
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

        print("Loaded family data successfully.")
        update_listbox()

    except ET.ParseError:
        print("Error: Error parsing the XML file.")
    except Exception as e:
        print(f"Error: {str(e)}")

# Function to save family data to XML
def save_to_xml():
    if not filename:
        print("Error: No file loaded to save data.")
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
    print(f"Saved family data to {filename}.")

# Function to update the Listbox (simulate output)
def update_listbox():
    print("Current family members:")
    for person_id, person_info in family_data.items():
        print(f"{person_info['name']} (ID: {person_id}) - {'Alive' if person_info['alive'] else 'Deceased'}")

# Function to add a person to the family data
def add_person(name, birth_date, alive, relationships):
    if not name or not birth_date:
        print("Error: Name and Birth Date cannot be blank.")
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

    print(f"Added Person - ID: {new_person_id}, Name: {name}, Birth Date: {birth_date}, Status: {'Alive' if alive else 'Deceased'}")

    # Process relationships
    for rel_name, rel_type in relationships:
        for existing_person_id, person_info in family_data.items():
            if person_info['name'] == rel_name:
                if rel_type == "Parent":
                    family_data[existing_person_id]['children'].append(new_person_id)
                    family_data[new_person_id]['parents'].append(existing_person_id)
                elif rel_type == "Child":
                    family_data[existing_person_id]['parents'].append(new_person_id)
                    family_data[new_person_id]['children'].append(existing_person_id)
                elif rel_type == "Partner":
                    family_data[existing_person_id]['partners'].append(new_person_id)
                    family_data[new_person_id]['partners'].append(existing_person_id)

    update_listbox()
    save_to_xml()

# Function to edit person details
def edit_person(person_id):
    if person_id not in family_data:
        print("Error: Selected person not found.")
        return

    person_info = family_data[person_id]
    print(f"Editing {person_info['name']}")

    new_name = input("New Name (leave blank to keep current): ")
    new_birth_date = input("New Birth Date (leave blank to keep current): ")
    new_alive_status = input("Alive? (yes/no, leave blank to keep current): ")

    if new_name:
        family_data[person_id]['name'] = new_name
    if new_birth_date:
        family_data[person_id]['birth_date'] = new_birth_date
    if new_alive_status:
        family_data[person_id]['alive'] = new_alive_status.lower() == 'yes'

    update_listbox()
    save_to_xml()

# Main CLI application loop
def main():
    global filename
    while True:
        print("============================")
        print("Family Tree Application")
        print("1. Load Family Tree")
        print("2. View Family Members")
        print("3. Add New Person")
        print("4. Edit Person")
        print("5. Save Family Tree")
        print("6. Exit")
        print("============================")
        choice = input("Choose an option: ")
        print("============================")

        if choice == "1":
            filename = input("Enter XML file path to load: ")
            load_from_xml(filename)
        elif choice == "2":
            update_listbox()
        elif choice == "3":
            name = input("Enter name: ")
            birth_date = input("Enter birth date (YYYY-MM-DD): ")
            alive = input("Is the person alive? (yes/no): ").lower() == 'yes'
            relationships = []
            while True:
                rel_name = input("Enter a relationship name (or 'done' to finish): ")
                if rel_name.lower() == 'done':
                    break
                rel_type = input("Enter relationship type (Parent, Child, Partner): ")
                relationships.append((rel_name, rel_type))
            add_person(name, birth_date, alive, relationships)
        elif choice == "4":
            person_id = input("Enter the ID of the person to edit: ")
            edit_person(person_id)
        elif choice == "5":
            save_to_xml()
        elif choice == "6":
            print("Exiting the application.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
