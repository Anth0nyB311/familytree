"""autosave feature"""
import datetime
import sys
import os
import subprocess
import yaml
from family_lib import Person, Parent, Child, Partner, ParentChild


def return_save_filename():
    """Gets the filename"""
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    return f"saves/family_tree_{timestamp}.yaml"


def yaml_export(family, filename=return_save_filename()):
    """exports yaml file"""
    if  not os.path.exists("saves"):
        os.makedirs("saves")
    try:
        serialized_family = []
        for person in family:
            person_type = person.__class__.__name__
            person_dict = {
                "id": person.id,
                "type": person_type,
                "name": person.name,
                "dob": person.dob,
                "is_alive": person.is_alive,
                "death_date": person.death_date,
                "ethnicity": person.ethnicity,
            }
            person_dict["children_ids"] = [
                child.id for child in getattr(person, "children", [])
            ]
            person_dict["partners_ids"] = [
                partner.id for partner in getattr(person, "partners", [])
            ]
            person_dict["parents_ids"] = [
                parent.id for parent in getattr(person, "parents", [])
            ]
            person_dict["siblings_ids"] = [
                sibling.id for sibling in getattr(person, "siblings", [])
            ]
            serialized_family.append(person_dict)
        with open(filename, "w") as f:
            yaml.safe_dump(serialized_family, f, sort_keys=False)

        print(f"{filename} was a success.")

    except Exception as e:
        print(f"An error was found: {e}")


def yaml_import(filename):
    """imports the yaml"""
    try:
        print(f"Attempting to load file: {filename}")
        with open(filename, "r") as f:
            family_data = yaml.safe_load(f)
            print(f"Loaded data length: {len(family_data) if family_data else 0}")

        if not family_data:
            print(f"File empty or not found, starting with empty family.")
            return []

        id_to_person = {}
        family = []
        max_id = 0

        # First pass: Create all person objects
        for person_dict in family_data:
            try:
                print(f"Processing person: {person_dict.get('name', 'Unknown')}")
                person_type = person_dict.get("type")
                
                if person_type == "Parent":
                    person = Parent(
                        name=person_dict["name"],
                        dob=person_dict["dob"],
                        is_alive=person_dict["is_alive"],
                        ethnicity=person_dict["ethnicity"],
                    )
                elif person_type == "Child":
                    person = Child(
                        name=person_dict["name"],
                        dob=person_dict["dob"],
                        is_alive=person_dict["is_alive"],
                        ethnicity=person_dict["ethnicity"],
                    )
                elif person_type == "Partner":
                    person = Partner(
                        name=person_dict["name"],
                        dob=person_dict["dob"],
                        is_alive=person_dict["is_alive"],
                        ethnicity=person_dict["ethnicity"],
                    )
                else:
                    print(f"Unknown person type: {person_type}")
                    continue

                person.id = person_dict["id"]
                if not person.is_alive:
                    person.death_date = person_dict.get("death_date")
                
                person.children = []
                person.partners = []
                person.parents = []
                person.siblings = []
                
                max_id = max(max_id, person.id)
                id_to_person[person.id] = person
                family.append(person)
                print(f"Successfully added {person.name}")

            except Exception as e:
                print(f"Error processing person: {str(e)}")
                continue

        print(f"First pass complete. Family size: {len(family)}")
        Person._id_counter = max_id + 1

        # Second pass: Process relationships
        for person_dict in family_data:
            try:
                person = id_to_person.get(person_dict["id"])
                if not person:
                    continue

                print(f"Processing relationships for: {person.name}")
                for child_id in person_dict.get("children_ids", []):
                    child = id_to_person.get(child_id)
                    if child and child not in person.children:
                        person.children.append(child)
                        if person not in child.parents:
                            child.parents.append(person)

                for partner_id in person_dict.get("partners_ids", []):
                    partner = id_to_person.get(partner_id)
                    if partner and partner not in person.partners:
                        person.partners.append(partner)
                        if person not in partner.partners:
                            partner.partners.append(person)

                for parent_id in person_dict.get("parents_ids", []):
                    parent = id_to_person.get(parent_id)
                    if parent and parent not in person.parents:
                        person.parents.append(parent)
                        if person not in parent.children:
                            parent.children.append(person)

                for sibling_id in person_dict.get("siblings_ids", []):
                    sibling = id_to_person.get(sibling_id)
                    if sibling and sibling not in person.siblings:
                        person.siblings.append(sibling)
                        if person not in sibling.siblings:
                            sibling.siblings.append(person)

            except Exception as e:
                print(f"Error processing relationships: {str(e)}")
                continue

        print(f"Import complete. Final family size: {len(family)}")
        return family

    except Exception as e:
        print(f"Error loading family: {str(e)}")
        return []

if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"])