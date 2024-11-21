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
        with open(filename, "r") as f:
            family_data = yaml.safe_load(f)

        if not family_data:
            print(f"File not found, starting with empty family.")
            return []
        id_to_person = {}
        family = []

        for person_dict in family_data:
            person_type = person_dict.get("type", "Person")
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
            elif person_type == "ParentChild":
                person = ParentChild(
                    name=person_dict["name"],
                    dob=person_dict["dob"],
                    is_alive=person_dict["is_alive"],
                    ethnicity=person_dict["ethnicity"],
                )
            else:
                raise ValueError(f"Unknown person type: {person_type}")
            person.id = person_dict["id"]
            if not person.is_alive:
                person.death_date = person_dict.get("death_date")
            else:
                person.death_date = None
            id_to_person[person.id] = person
            family.append(person)
        max_id = max(id_to_person.keys(), default=0)
        if hasattr(Person, "_id_counter"):
            Person._id_counter = max_id + 1
        else:
            Person._id_counter = max_id + 1
        for person_dict in family_data:
            person = id_to_person[person_dict["id"]]
            for child_id in person_dict.get("children_ids", []):
                child = id_to_person.get(child_id)
                if child and child not in getattr(person, "children", []):
                    person.children.append(child)
                    if person not in getattr(child, "parents", []):
                        child.parents.append(person)
            for partner_id in person_dict.get("partners_ids", []):
                partner = id_to_person.get(partner_id)
                if partner and partner not in getattr(person, "partners", []):
                    person.partners.append(partner)
                    if person not in getattr(partner, "partners", []):
                        partner.partners.append(person)
            for parent_id in person_dict.get("parents_ids", []):
                parent = id_to_person.get(parent_id)
                if parent and parent not in getattr(person, "parents", []):
                    person.parents.append(parent)
                    if person not in getattr(parent, "children", []):
                        parent.children.append(person)
            for sibling_id in person_dict.get("siblings_ids", []):
                sibling = id_to_person.get(sibling_id)
                if sibling and sibling not in getattr(person, "siblings", []):
                    person.siblings.append(sibling)
                    if person not in getattr(sibling, "siblings", []):
                        sibling.siblings.append(person)

        print(f"{filename} was a success.")
        return family

    except FileNotFoundError:
        print(f"File not found, starting with empty family.")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing the save file: {e}")
        return []
    except ValueError as ve:
        print(f"Value error occured: {ve}")
        return []
    except Exception as e:
        print(f"Unexpected error found: {e}")
        return []

if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"])