"""The main file, where the code runs from"""

import re
from datetime import datetime
import family_lib
import clear
from family_calendar import display_calendar


class FamilyTree:
    """Main class of code"""

    def __init__(self):
        self.family = []  # list of people in the family
        self.stats = FamilyTreeStatistics(self.family)
        self.prog_exit = False

    def display_help(self):
        """Prompts the help option for the user"""
        clear.clear()  # clear the screen
        how_to_use = """
        How to use program -->
        =====================
        You are currently in CLI mode, which will not create the tree. You must use GUI for the tree diagram. All functionalities are the same...

        Commands and what they do -->

        ADD
        ===
        |
        --> CHILD/PARENT/PARTNER
            This will add a new person into the family, depending on what role you chose for them.
            Use Case --> ADD CHILD ''Jack'', ADD PARENT ''Smith'', ADD PARENT 'Mary'
        |
        --> RELATIONSHIP
            This will help to bind relationships between family members.
            Use Case --> ADD RELATIONSHIP 'Jack' TO 'Smith'

        REMOVE (Unrecoverable data loss!)
        =================================
        |
        --> CHILD/PARENT/PARTNER
            This will remove a person from the family.
            NOTE: if one person relies on the other person’s existence e.g., a child requires two parents to exist and you try to remove one of the parents, you must first remove any redundancies (remove the child first then the parent).
            Use Case --> REMOVE CHILD 'Jack' (this will also automatically remove any relationships with it too)
        |
        --> RELATIONSHIP
            This will remove a relationship between family members.
            Use Case --> REMOVE RELATIONSHIP 'Jack' FROM 'Smith'

        GET
        ===
        |
        --> PARENTS/GRANDPARENTS/SIBLINGS/COUSINS
            This will return the people (based on relationships) that are related to the selected user.
            Use Case --> GET PARENTS OF 'Jack'
        |
        --> IMMEDIATE
            This will output all the immediate family of the selected user (based on relationships).
            Use Case --> GET IMMEDIATE OF 'Jack'
        |
        --> EXTENDED
            This will output all the extended family of the selected user (based on relationships).
            Use Case --> GET EXTENDED OF 'Jack'
        |
        --> ALLBIRTHDAYS or SORTEDBIRTHDAYS
            This will display all the birthdays of the people saved.
            Use Case --> GET ALLBIRTHDAYS
        |
        --> CALENDAR
            This will display an ASCII art style calendar with all the people's birthdays on it.
            Use Case --> GET CALENDAR
        |
        --> AVAGE or DAVAGE (gets your average and or the death average age)

        |
        --> INDIVCHILDCOUNT (counts how many children one person has) so INDIVCHILDCOUNT OF 'Jack'

        |
        --> ACPP (gets you the Average Child Per Person)
        |
        --> EVERYTHING
            This will output all the lists in a nice manner for saving.
            Use Case --> GET EVERYTHING

        CLEAR
        =====
        |
        --> Clears the console. Use Case --> CLEAR

        EXIT
        ====
        |
        --> Exits the program. Use Case --> EXIT
        """

        print(how_to_use)  # print the help text

    def parse_command(self, user_input, search_for):
        """Gets the subject of the action (ADD CHILD will return CHILD)"""
        add_pattern = (
            rf"{search_for}\s+(\S+)"  # regex pattern to search for the command
        )
        comm = re.search(add_pattern, user_input)
        return comm.group(1).upper() if comm else None  # return the command

    def valid_dob(self, date, date_format="%Y-%m-%d"):
        """Checks if the date given is correct"""
        try:
            datetime.strptime(date, date_format)  # check if the date is valid
            return True
        except ValueError:
            return False

    def person_adder(self, names, person_type):
        """CLI prompt to add users to the program"""
        dob = "na"
        alive_status = True
        death_date = None
        ethnicity = "na"
        if not names:
            print(
                "This user needs a name, please give us their full name (including middle names)."
            )
            while True:
                name = input("Name(s):")
                if name:
                    names = f"{name}".strip()
                    break
        else:
            print("Add more details to name or leave empty (like middle name):")
            name = input("Name(s):")  # get the name
            names = f"{names[0]} {name}".strip()

        while True:  # get the date of birth
            dob = input(f"Enter {names}'s date of birth, in this format YYYY-MM-DD:")
            if self.valid_dob(dob, "%Y-%m-%d"):  # check if the date is valid
                break
        alive = input(f"Is {names} alive? Y/N:")
        if alive.upper() == "Y":
            alive_status = True
        else:
            alive_status = False
        while True:
            ethnicity = input(f"Enter {names}'s ethnicity:")
            if ethnicity:
                break
        person = person_type(names, dob, alive_status, ethnicity)
        if not alive_status:
            while True:
                death_date = input(
                    f"Enter {names}'s date of death, in this format YYYY-MM-DD:"
                )
                if self.valid_dob(death_date, "%Y-%m-%d"):
                    person.death_date = death_date  # Use the setter method
                    break
                # create the person
        self.family.append(person)  # add the person to the family
        print(f"Added {names} to the family!")

    def add_remove_person(self, add_mode, user_input):
        """Add or remove a person from the program"""
        pattern = r"'([^']+)'"  # regex pattern to search for the name
        names = re.findall(pattern, user_input)
        current_command = self.parse_command(
            user_input, "ADD" if add_mode else "REMOVE"
        )

        if current_command == "RELATIONSHIP" and len(names) == 2:
            self.handle_relationship(add_mode, names)
        elif len(names) == 1:
            if add_mode:
                self.handle_person_addition(current_command, names)
            else:
                self.person_remover(names)
        else:
            self.__invalid_usage(user_input)

    def handle_relationship(self, add_mode, names):
        """Handle the relationship between two people"""
        id1 = self.stats.get_id(names[0])
        id2 = self.stats.get_id(names[1])
        if id1 is None or id2 is None:
            print("One or both persons could not be found.")
            return
        per1 = next((person for person in self.family if person.id == id1), None)
        per2 = next((person for person in self.family if person.id == id2), None)
        if add_mode:
            self.establish_relationship(per1, per2)
        else:
            self.remove_relationship(per1, per2)

    def handle_person_addition(self, current_command, names):
        """Handle the addition of a person to the program"""
        if current_command == "CHILD":
            self.person_adder(names, family_lib.Child)
        elif current_command == "PARENT":
            self.person_adder(names, family_lib.Parent)
        elif current_command == "PARTNER":
            self.person_adder(names, family_lib.Partner)
        else:
            self.__invalid_usage(current_command)

    def establish_relationship(self, per1, per2, rel=None):
        """Establish a relationship between two people. Can also convert person type"""
        original_id_per1 = per1.id
        original_id_per2 = per2.id
        if rel is None:  # if the relationship is not found
            print("Please choose what relationship you want to add:")
            print(f"1) {per1.name} is the parent of {per2.name}")
            print(f"2) {per2.name} is the parent of {per1.name}")
            print(f"3) {per1.name} and {per2.name} are siblings.")
            print(f"4) {per1.name} and {per2.name} are partners.")
            try:
                rel = int(input("Input:"))
                if rel > 4 or rel < 1:
                    print(f"{rel} is not an option.")
                    return
            except ValueError:
                print("Invalid input. Please enter a number.")
                return

        try:
            if rel == 1:
                per1.add_person(per2)
                print(f"Added {per2.name} as a child of {per1.name}")  # add the child
            elif rel == 2:
                per2.add_person(per1)
                print(f"Added {per1.name} as a child of {per2.name}")  # add the child
            elif rel == 3:
                per1.add_sibling(per2)
                print(
                    f"{per1.name} and {per2.name} are now siblings"
                )  # add the sibling
            elif rel == 4:
                per1.add_partner(per2)
                print(
                    f"{per1.name} and {per2.name} are now partners"
                )  # add the partner
        except TypeError:  # if the type is not valid
            if not isinstance(per1, family_lib.ParentChild):
                per1 = family_lib.convert(
                    per1, family_lib.ParentChild
                )  # convert the person
                self.family = [
                    per1 if person.id == original_id_per1 else person
                    for person in self.family
                ]  # add the person
            if not isinstance(per2, family_lib.ParentChild):
                per2 = family_lib.convert(
                    per2, family_lib.ParentChild
                )  # convert the person
                self.family = [
                    per2 if person.id == original_id_per2 else person
                    for person in self.family
                ]  # add the person

            self.establish_relationship(
                per1, per2, rel
            )  # establish the relationship againt with recusrion

    def person_remover(self, name):
        """Remove a person from the program"""
        person_id = self.stats.get_id(name[0])  # get the id of the person
        if person_id is None:
            print(f"{name} does not exist!")
            return
        person = next(
            (person for person in self.family if person.id == person_id), None
        )
        if person is None:
            print(f"{name} does not exist!")
            return
        if isinstance(
            person, (family_lib.Parent, family_lib.ParentChild)
        ):  # if the person is a parent
            if person.children:
                print(f"In order to remove {name[0]}, you must remove:")
                for child in person.children:
                    print(f"{child.name}")  # print the children
                return

        self.remove_all_relationships(person)  # remove all the relationships

        self.family.remove(person)  # remove the person
        print(f"{person.name} has been removed from the family.")

    def remove_all_relationships(self, person):  # remove all the relationships
        """Remove all relationships of a person"""
        class_relationships = {  # the relationships
            family_lib.Parent: ["partners", "parents", "siblings"],
            family_lib.Child: ["parents", "siblings"],
            family_lib.Partner: ["partners"],
            family_lib.ParentChild: ["children", "partners", "parents", "siblings"],
        }

        relationships = []
        for cls, attrs in class_relationships.items():  # get the relationships
            if isinstance(person, cls):
                relationships.extend(attrs)  # add the relationships
                break

        for relation in relationships:
            rel_list = getattr(person, relation, [])  # get the relationships
            for related_person in rel_list[:]:  # get the related
                self.remove_relationship(
                    person, related_person
                )  # remove the relationship

    def remove_relationship(self, per1, per2):
        """Remove a relationship between two people"""
        relationships = self.get_existing_relationships(per1, per2)
        if not relationships:
            print(f"No relationships found between {per1.name} and {per2.name}.")
            return

        print("Please choose which relationship you want to remove:")
        for idx, relation in enumerate(relationships, start=1):
            print(f"{idx}) {relation['description']}")

        selected_relation = self.__select_relationship(relationships)

        # Call the appropriate function to remove the relationship
        selected_relation["remove_func"](per1, per2)
        print(f"Removed relationship: {selected_relation['description']}")

    def get_existing_relationships(self, per1, per2):
        """Get a list of existing relationships between two people"""
        relationships = []
        if hasattr(per1, "children") and per2 in per1.children:
            relationships.append(
                {
                    "description": f"{per1.name} is the parent of {per2.name}",
                    "remove_func": self.__remove_parent_child_relationship,
                }
            )
        if hasattr(per2, "children") and per1 in per2.children:
            relationships.append(
                {
                    "description": f"{per2.name} is the parent of {per1.name}",
                    "remove_func": self.__remove_parent_child_relationship,
                }
            )
        if hasattr(per1, "siblings") and per2 in per1.siblings:
            relationships.append(
                {
                    "description": f"{per1.name} and {per2.name} are siblings",
                    "remove_func": self.__remove_sibling_relationship,
                }
            )
        if hasattr(per1, "partners") and per2 in per1.partners:
            relationships.append(
                {
                    "description": f"{per1.name} and {per2.name} are partners",
                    "remove_func": self.__remove_partner_relationship,
                }
            )
        return relationships

    def __select_relationship(self, relationships):
        """Prompt user to select a relationship to remove"""
        while True:
            try:
                choice = int(input("Input: "))
                if 1 <= choice <= len(relationships):
                    return relationships[choice - 1]
            except ValueError:
                print("Invalid input. Please enter a number.")

    def __remove_parent_child_relationship(self, per1, per2):
        """Remove parent-child relationship between two people"""
        if hasattr(per1, "children") and per2 in per1.children:
            per1.children.remove(per2)
            if hasattr(per2, "parents"):
                per2.parents.remove(per1)
        elif hasattr(per2, "children") and per1 in per2.children:
            per2.children.remove(per1)
            if hasattr(per1, "parents"):
                per1.parents.remove(per2)

    def __remove_sibling_relationship(self, per1, per2):
        """Remove sibling relationship between two people"""
        if hasattr(per1, "siblings") and per2 in per1.siblings:
            per1.siblings.remove(per2)
        if hasattr(per2, "siblings") and per1 in per2.siblings:
            per2.siblings.remove(per1)

    def __remove_partner_relationship(self, per1, per2):
        """Remove partner relationship between two people"""
        if hasattr(per1, "partners") and per2 in per1.partners:
            per1.partners.remove(per2)
        if hasattr(per2, "partners") and per1 in per2.partners:
            per2.partners.remove(per1)

    def display_everything(self):
        """Display everything in a formatted table"""
        headers = self.get_headers()
        rows = self.get_family_rows()
        col_widths = [
            max(len(header), max(len(row[idx]) for row in rows))
            for idx, header in enumerate(headers)
        ]
        row_format = " | ".join(f"{{:<{width}}}" for width in col_widths)

        print("-" * (sum(col_widths) + len(col_widths) * 3 - 1))
        print(row_format.format(*headers))
        print("-" * (sum(col_widths) + len(col_widths) * 3 - 1))
        for row in rows:
            print(row_format.format(*row))
        print("-" * (sum(col_widths) + len(col_widths) * 3 - 1))

    def get_headers(self):
        """Just gets headers back"""
        return [
            "Name",
            "DOB",
            "Alive Status",
            "Ethnicity",
            "Children",
            "Partners",
            "Parents",
            "Siblings",
        ]

    def get_family_rows(self):
        """Makes the rows"""
        rows = []
        for person in self.family:
            row = [
                person.name,
                person.dob,
                "Alive" if person.is_alive else f"Deceased ({person.death_date})",
                person.ethnicity,
                ", ".join(child.name for child in getattr(person, "children", [])),
                ", ".join(partner.name for partner in getattr(person, "partners", [])),
                ", ".join(parent.name for parent in getattr(person, "parents", [])),
                ", ".join(sibling.name for sibling in getattr(person, "siblings", [])),
            ]
            rows.append(row)
        return rows

    def get_relationships(self, relationship, name):
        """Get the relationships between person"""
        person_id = self.stats.get_id(name)  # get the id of the person
        if person_id is None:
            print(f"{name} does not exist!")
            return
        person = next(
            (person for person in self.family if person.id == person_id), None
        )  # get the person
        if person is None:
            print(f"{name} does not exist!")
            return
        if relationship == "PARENTS":
            self.stats.display_parents(person)  # display the parents
        elif relationship == "GRANDPARENTS":
            self.stats.display_grandparents(person)  # display the grandparents
        elif relationship == "SIBLINGS":
            self.stats.display_siblings(person)  # display the siblings
        elif relationship == "COUSINS":
            self.stats.display_cousins(person)  # display the cousins
        elif relationship == "IMMEDIATE":
            self.stats.display_immediate(person)  # display the immediate family
        elif relationship == "EXTENDED":
            self.stats.display_extended(person)  # display the extended family
        else:
            self.__invalid_usage(relationship)

    def get_command(self, user_input):
        """Get the command from the user"""
        pattern = r"'([^']+)'"  # get the name
        names = re.findall(pattern, user_input)
        current_command = self.parse_command(user_input, "GET")

        # Define a dictionary mapping commands to handler methods
        command_handlers = {
            "CALENDAR": lambda: display_calendar(self.family),
            "ALLBIRTHDAYS": self.__handle_all_birthdays,
            "SORTBIRTHDAYS": self.__handle_sort_birthdays,
            "AVAGE": self.__handle_avage,
            "DAVAGE": self.__handle_davage,
            "INDIVCHILDCOUNT": lambda: (
                self.stats.get_indiv_cc(names[0])
                if names
                else self.__invalid_usage(user_input)
            ),
            "ACPP": self.stats.calc_acpp,
            "EVERYTHING": self.display_everything,
        }

        relationship_commands = {
            "PARENTS",
            "GRANDPARENTS",
            "SIBLINGS",
            "COUSINS",
            "IMMEDIATE",
            "EXTENDED",
        }

        if current_command in command_handlers:
            command_handlers[current_command]()  # Call the handler function
        elif current_command in relationship_commands and names:
            self.get_relationships(current_command, names[0])  # get the relationships
        else:
            self.__invalid_usage(user_input)

    def __handle_all_birthdays(self):
        for member in self.family:
            print(f"{member.name} has the birthday of {member.dob}")

    def __handle_sort_birthdays(self):
        # Sort birthdays ignoring the year of birth
        sorted_family = sorted(
            self.family,
            key=lambda member: (
                member.dob[5:],
                member.dob[:4],
            ),
        )
        # Create a dictionary to store birthdays by month and day only
        birthday_calendar = {}
        for member in sorted_family:
            birthday_key = member.dob[5:]  # only use MM-DD for the calendar key
            birthday_calendar.setdefault(birthday_key, []).append(member.name)
        # Display the birthday calendar
        for date, names in birthday_calendar.items():
            names_list = ", ".join(names)
            print(f"{date}: {names_list}")

    def __handle_avage(self):
        avg_age = self.stats.calc_avage()
        if avg_age is not None:
            print(f"The average age of living family members is {avg_age:.2f} years.")
        else:
            print("No living family members with valid date of birth.")

    def __handle_davage(self):
        avg_death_age = self.stats.calc_davage()
        if avg_death_age is not None:
            print(f"Average age at death is {avg_death_age:.2f} years.")
        else:
            print("No deceased family members with valid dates of birth and death.")

    def __invalid_usage(self, user_input):
        print(f'"{user_input}" isn\'t used correctly. Please type HELP to get started.')

    def main(self):
        """Main function of the code"""
        print("Welcome to Family Tree CLI! Type HELP to get started!")
        print()
        while not self.prog_exit:
            user_input = input(">>")
            if user_input.upper().startswith("HELP"):
                self.display_help()
            elif user_input.upper().startswith(
                "CLEAR"
            ) or user_input.upper().startswith("CLS"):
                clear.clear()
            elif user_input.upper().startswith("EXIT"):
                self.prog_exit = True
            elif user_input.upper().startswith("ADD"):
                self.add_remove_person(True, user_input)
            elif user_input.upper().startswith("REMOVE"):
                self.add_remove_person(False, user_input)
            elif user_input.upper().startswith("GET"):
                self.get_command(user_input)
            else:
                print(
                    f'"{user_input}" is not a valid command. Please type HELP if you are stuck.'
                )


class FamilyTreeStatistics:
    """Class to handle the statistics of the family"""

    def __init__(self, family):
        self.family = family

    def get_grandparents(self, person):
        """Return the grandparents of a person"""
        grandparents = []
        parents = getattr(person, "parents", [])
        for parent in parents:
            grandparents.extend(getattr(parent, "parents", []))
        return grandparents

    def get_grandchildren(self, person):
        """Return the grandchildren of a person"""
        grandchildren = []
        children = getattr(person, "children", [])
        for child in children:
            grandchildren.extend(getattr(child, "children", []))
        return grandchildren

    def get_aunts_uncles(self, person):
        """Return the aunts and uncles of a person"""
        aunts_uncles = []
        parents = getattr(person, "parents", [])
        for parent in parents:
            aunts_uncles.extend(getattr(parent, "siblings", []))
        return aunts_uncles

    def get_nieces_nephews(self, person):
        """Return the nieces and nephews of a person"""
        nieces_nephews = []
        siblings = getattr(person, "siblings", [])
        for sibling in siblings:
            nieces_nephews.extend(getattr(sibling, "children", []))
        return nieces_nephews

    def get_cousins(self, person):
        """Return the cousins of a person"""
        cousins = []
        aunts_uncles = self.get_aunts_uncles(person)
        for aunt_uncle in aunts_uncles:
            cousins.extend(getattr(aunt_uncle, "children", []))
        return cousins

    def get_immediate_family(self, person):
        """Return the immediate family of a person"""
        immediate_family = set()
        immediate_family.update(getattr(person, "partners", []))
        immediate_family.update(getattr(person, "parents", []))
        immediate_family.update(getattr(person, "children", []))
        immediate_family.update(getattr(person, "siblings", []))
        return immediate_family

    def display_extended(self, person):
        """Display the extended family of a person"""
        extended_family = set()
        extended_family.update(self.get_grandparents(person))
        extended_family.update(self.get_grandchildren(person))
        extended_family.update(self.get_aunts_uncles(person))
        extended_family.update(self.get_nieces_nephews(person))
        extended_family.update(self.get_cousins(person))

        immediate_family = self.get_immediate_family(person)
        extended_family.difference_update(immediate_family)  # get the extended family

        if extended_family:
            print(f"Extended family of {person.name}:")  # print the extended family
            for member in extended_family:
                print(f"- {member.name}")
        else:
            print(f"{person.name} has no extended family recorded.")

    def display_immediate(self, person):
        """Display the immediate family of a person"""
        immediate_family = set()
        if hasattr(person, "partners") and person.partners:  # get the immediate family
            immediate_family.update(person.partners)
        if hasattr(person, "parents") and person.parents:
            immediate_family.update(person.parents)
        if hasattr(person, "children") and person.children:
            immediate_family.update(person.children)
        if hasattr(person, "siblings") and person.siblings:
            immediate_family.update(person.siblings)
        if immediate_family:
            print(f"Immediate family of {person.name}:")
            for member in immediate_family:
                print(f"- {member.name}")  # print the immediate family
        else:
            print(f"{person.name} has no immediate family recorded.")

    def display_parents(self, person):
        """Display the parents of a person"""
        if hasattr(person, "parents") and person.parents:  # get the parents
            print(f"Parents of {person.name}:")
            for parent in person.parents:  # print the parents
                print(f"- {parent.name}")
        else:
            print(f"{person.name} has no parents recorded.")

    def display_grandparents(self, person):
        """Display the grandparents of a person"""
        grandparents = []
        if hasattr(person, "parents") and person.parents:  # get the grandparents
            for parent in person.parents:
                if hasattr(parent, "parents") and parent.parents:
                    grandparents.extend(parent.parents)
        if grandparents:
            print(f"Grandparents of {person.name}:")  # print the grandparents
            for grandparent in grandparents:
                print(f"- {grandparent.name}")
        else:
            print(f"{person.name} has no grandparents recorded.")

    def display_siblings(self, person):
        """Display the siblings of a person"""
        if hasattr(person, "siblings") and person.siblings:  # get the siblings
            print(f"Siblings of {person.name}:")
            for sibling in person.siblings:
                print(f"- {sibling.name}")  # print the siblings
        else:
            print(f"{person.name} has no siblings recorded.")

    def display_cousins(self, person):
        """Display the cousins of a person"""
        cousins = []
        if hasattr(person, "parents") and person.parents:  # get the cousins
            for parent in person.parents:
                if hasattr(parent, "siblings") and parent.siblings:
                    for aunt_uncle in parent.siblings:
                        if hasattr(aunt_uncle, "children") and aunt_uncle.children:
                            cousins.extend(aunt_uncle.children)
        if cousins:
            print(f"Cousins of {person.name}:")
            for cousin in cousins:
                print(f"- {cousin.name}")  # print the cousins
        else:
            print(f"{person.name} has no cousins recorded.")

    def calc_avage(self):
        """Calculate the average age of the family"""
        today = datetime.today()  # get the date
        ages = []
        for member in self.family:
            if member.is_alive:
                try:
                    dob = datetime.strptime(member.dob, "%Y-%m-%d")
                    age = (today - dob).days / 365.25
                    ages.append(age)
                except ValueError:
                    continue
        if ages:
            return sum(ages) / len(ages)
        return None

    def get_indiv_cc(self, name):
        """Get the individual child count"""
        person_id = self.get_id(name)  # get the id of the person
        if person_id is None:
            print(f"{name} does not exist!")
            return
        person = next(
            (person for person in self.family if person.id == person_id), None
        )  # get the person
        if person is None:
            print(f"{name} does not exist!")
            return
        if hasattr(person, "children") and person.children:  # get the children
            child_count = len(person.children)
            print(
                f'{person.name} has {child_count} child{"ren" if child_count > 1 else ""}.'
            )  # print the children
        else:
            print(f"{person.name} has no children.")

    def calc_acpp(self):
        """Calculate the average child per person"""
        total_children = 0
        parent_count = 0
        for member in self.family:  # get the average child per person
            if hasattr(member, "children") and member.children:
                total_children += len(member.children)
                parent_count += 1
        if parent_count > 0:
            average_children = total_children / parent_count
            print(
                f"The average number of children per person is {average_children:.2f}."
            )  # print the average children
        else:
            print("No parents with children found in the family.")

    def calc_davage(self):
        """Calculate the average death age of the family"""

        death_ages = []
        for member in self.family:  # get the average death age
            if not member.is_alive and member.death_date:
                try:
                    dob = datetime.strptime(member.dob, "%Y-%m-%d")
                    death_date = datetime.strptime(member.death_date, "%Y-%m-%d")
                    age_at_death = (
                        death_date - dob
                    ).days / 365.25  # get the age at death in years
                    death_ages.append(age_at_death)
                except ValueError:
                    continue
        if death_ages:
            average_death_age = sum(death_ages) / len(
                death_ages
            )  # get the average death age
            return average_death_age
        return None

    def get_id(self, name):
        """Get the ID of a person, sorts out any collisions too"""
        matches = [
            person for person in self.family if name.lower() in person.name.lower()
        ]  # get the id of the person
        if not matches:
            print(f"Couldn't find '{name}'.")  # if the person is not found
            return None

        if len(matches) == 1:  # if the person is found
            return matches[0].id
        while True:
            print(
                f'There are multiple people matching "{name}":'
            )  # if there are multiple people with the same name
            for i, person in enumerate(matches, start=1):
                print(f"{i}: {person.name} (ID: {person.id})")  # print the people
            try:
                selection = int(  # get the selection
                    input(f'Please select which "{name}" you want (enter the number): ')
                )
                if 1 <= selection <= len(matches):
                    return matches[selection - 1].id
            except ValueError:  # if the selection is not valid
                print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    family_tree = FamilyTree()
    family_tree.main()
