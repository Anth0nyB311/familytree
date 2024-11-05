import re
import datetime
import Family
import clear
from family_calendar import display_calendar


class FamilyTree:
    def __init__(self):
        self.family = [] # list of people in the family
        self.progExit = False

    def display_help(self):
        clear.clear()   # clear the screen
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

        print(how_to_use) # print the help text

    def parse_command(self, userIn, searchFor):
        addPattern = rf"{searchFor}\s+(\S+)" # regex pattern to search for the command
        comm = re.search(addPattern, userIn)
        return comm.group(1).upper() if comm else None # return the command

    def valid_dob(self, date, format="%Y-%m-%d"):
        try:
            datetime.datetime.strptime(date, format) # check if the date is valid
            return True
        except ValueError:
            return False
         
    def person_adder(self, names, type): # add a person to the family
        dob = "na"
        alive_status = True
        death_date = None
        ethnicity = "na"
        if not names:
            print(
                "This user needs a name, please give us their full name (including middle names).")
            while True:
                name = input("Name(s):")
                if name:
                    names = f'{name}'.strip()
                    break
        else:
            print("Please add more names for this user e.g., their middle and last name. If you have already given all details, leave empty.")
            name = input("Name(s):") # get the name
            names = f'{names[0]} {name}'.strip()

        while True: # get the date of birth
            dob = input(
                f'Enter {names}\'s date of birth, in this format YYYY-MM-DD:')
            if self.valid_dob(dob, "%Y-%m-%d"): # check if the date is valid
                break
        alive = input(f'Is {names} alive? Y/N:')
        if alive.upper() == "Y":
            alive_status = True
        else:
            alive_status = False
            while True:
                death_date = input(
                    f'Enter {names}\'s date of death, in this format YYYY-MM-DD:')
                if self.valid_dob(death_date, "%Y-%m-%d"): # check if the date is valid
                    break
        while True:
            ethnicity = input(f'Enter {names}\'s ethnicity:')
            if ethnicity:
                break
        person = type(names, dob, alive_status, ethnicity, death_date) # create the person
        self.family.append(person) # add the person to the family
        print(f'Added {names} to the family!')

    def get_id(self, name):
        matches = [person for person in self.family if name.lower() 
                   in person.name.lower()] # get the id of the person
        if not matches:
            print(f"Couldn't find '{name}'.") # if the person is not found
            return None

        if len(matches) == 1: # if the person is found
            return matches[0].id
        while True: 
            print(f'There are multiple people matching "{name}":') # if there are multiple people with the same name
            for i, person in enumerate(matches, start=1): 
                print(f"{i}: {person.name} (ID: {person.id})") # print the people
            try:
                selection = int( # get the selection
                    input(f'Please select which "{name}" you want (enter the number): '))
                if 1 <= selection <= len(matches):
                    return matches[selection - 1].id
                else:
                    print("Invalid selection. Please try again.")
            except ValueError: # if the selection is not valid
                print("Invalid input. Please enter a number.")

    def add_remove_person(self, add_mode, userIn): # add or remove a person
        pattern = r"'([^']+)'" # regex pattern to search for the name
        names = re.findall(pattern, userIn)
        current_command = "na"
        if add_mode:
            current_command = self.parse_command(userIn, "ADD") # get the command
        else:
            current_command = self.parse_command(userIn, "REMOVE") # get the command
        if current_command == "RELATIONSHIP" and len(names) == 2: # if the command is relationship
            id1 = self.get_id(names[0])
            id2 = self.get_id(names[1])
            if id1 is None or id2 is None: # if the person is not found
                print("One or both persons could not be found.")
                return
            per1 = next(
                (person for person in self.family if person.id == id1), None) # get the person
            per2 = next(
                (person for person in self.family if person.id == id2), None) # get the person
            if per1 is None or per2 is None:
                print("One or both persons could not be found in the family list.")
                return
            if add_mode: # if the mode is add
                self.establish_relationship(per1, per2) # establish the relationship
            else:
                self.remove_relationship(per1, per2) # remove the relationship
        elif len(names) == 1:
            if not add_mode: # if the mode is remove
                self.person_remover(names) # remove the person
            else:
                if not current_command: # if the command is not found
                    print(
                        f'"{userIn}" isn\'t used correctly. Please type HELP to get started.') # if the command is not valid
            if add_mode: 
                if current_command == "CHILD":
                    self.person_adder(names, Family.Child) # add a child
                elif current_command == "PARENT":
                    self.person_adder(names, Family.Parent) # add a parent
                elif current_command == "PARTNER":
                    self.person_adder(names, Family.Partner)  # add a partner
                else:
                    print(
                        f'"{userIn}" isn\'t used correctly. Please type HELP to get started.')
                    return
        else:
            if add_mode:
                if userIn.upper() == "ADD CHILD":
                    self.person_adder(None, Family.Child) # add a child
                elif userIn.upper() == "ADD PARENT":
                    self.person_adder(None, Family.Parent) # add a parent
                elif userIn.upper() == "ADD PARTNER":
                    self.person_adder(None, Family.Partner) # add a partner
                else:
                    print(
                        f'"{userIn}" isn\'t used correctly. Please type HELP to get started.')
            else:
                print(
                    f'"{userIn}" isn\'t used correctly. Please type HELP to get started.')

    def establish_relationship(self, per1, per2, rel=None):
        original_id_per1 = per1.id
        original_id_per2 = per2.id
        if rel is None: # if the relationship is not found
            print("Please choose what relationship you want to add:")
            print(f'1) {per1.name} is the parent of {per2.name}')
            print(f'2) {per2.name} is the parent of {per1.name}')
            print(f'3) {per1.name} and {per2.name} are siblings.')
            print(f'4) {per1.name} and {per2.name} are partners.')
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
                print(f"Added {per2.name} as a child of {per1.name}") # add the child
            elif rel == 2:
                per2.add_person(per1)
                print(f"Added {per1.name} as a child of {per2.name}")   # add the child
            elif rel == 3:
                per1.add_sibling(per2)
                print(f"{per1.name} and {per2.name} are now siblings") # add the sibling
            elif rel == 4:
                per1.add_partner(per2)
                print(f"{per1.name} and {per2.name} are now partners") # add the partner
        except TypeError as e: # if the type is not valid
            if not isinstance(per1, Family.ParentChild):
                per1 = Family.convert(per1, Family.ParentChild) # convert the person
                self.family = [
                    per1 if person.id == original_id_per1 else person for person in self.family] # add the person
            if not isinstance(per2, Family.ParentChild):
                per2 = Family.convert(per2, Family.ParentChild) # convert the person
                self.family = [
                    per2 if person.id == original_id_per2 else person for person in self.family] # add the person

            self.establish_relationship(per1, per2, rel) # establish the relationship againt with recusrion

    def person_remover(self, name):
        person_id = self.get_id(name[0]) # get the id of the person
        if person_id is None:
            print(f'{name} does not exist!')
            return
        person = next(
            (person for person in self.family if person.id == person_id), 
            None)
        if person is None:
            print(f'{name} does not exist!')
            return
        if isinstance(person, (Family.Parent, Family.ParentChild)): # if the person is a parent 
            if person.children:
                print(f'In order to remove {name[0]}, you must remove:')
                for child in person.children:
                    print(f'{child.name}') # print the children
                return

        self.remove_all_relationships(person) # remove all the relationships

        self.family.remove(person) # remove the person
        print(f'{person.name} has been removed from the family.')

    def remove_all_relationships(self, person): # remove all the relationships
        class_relationships = { # the relationships
            Family.Parent: ['partners', 'parents', 'siblings'],
            Family.Child: ['parents', 'siblings'],
            Family.Partner: ['partners'],
            Family.ParentChild: ['children', 'partners', 'parents', 'siblings'],
        }

        relationships = []
        for cls, attrs in class_relationships.items(): # get the relationships
            if isinstance(person, cls):
                relationships.extend(attrs) # add the relationships
                break

        for relation in relationships:
            rel_list = getattr(person, relation, []) # get the relationships
            for related_person in rel_list[:]: # get the related
                self.remove_relationship(person, related_person) # remove the relationship

    def remove_relationship(self, per1, per2):
        relationships = []
        if hasattr(per1, 'children') and per2 in per1.children:
            relationships.append(f"{per1.name} is the parent of {per2.name}")
        if hasattr(per2, 'children') and per1 in per2.children:
            relationships.append(f"{per2.name} is the parent of {per1.name}")
        if hasattr(per1, 'siblings') and per2 in per1.siblings:
            relationships.append(f"{per1.name} and {per2.name} are siblings")
        if hasattr(per1, 'partners') and per2 in per1.partners:
            relationships.append(f"{per1.name} and {per2.name} are partners")
        if not relationships:
            print(
                f"No relationships found between {per1.name} and {per2.name}.")
            return
        print("Please choose which relationship you want to remove:")
        for idx, relation in enumerate(relationships, start=1): # get the relationships
            print(f"{idx}) {relation}")

        while True:
            try: # get the selection
                choice = int(input("Input: "))
                if 1 <= choice <= len(relationships):
                    selected_relation = relationships[choice - 1] # get the selected relationship
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        if "is the parent of" in selected_relation:
            if hasattr(per1, 'children') and per2 in per1.children:
                per1.children.remove(per2) # remove the child
                if hasattr(per2, 'parents'):
                    per2.parents.remove(per1)   # remove the parent
            elif hasattr(per2, 'children') and per1 in per2.children:
                per2.children.remove(per1)
                if hasattr(per1, 'parents'): # remove the parent
                    per1.parents.remove(per2)
        elif "are siblings" in selected_relation:
            if hasattr(per1, 'siblings') and per2 in per1.siblings: # remove the sibling
                per1.siblings.remove(per2)
            if hasattr(per2, 'siblings') and per1 in per2.siblings: # remove the sibling
                per2.siblings.remove(per1)
        elif "are partners" in selected_relation:
            if hasattr(per1, 'partners') and per2 in per1.partners: # remove the partner
                per1.partners.remove(per2)
            if hasattr(per2, 'partners') and per1 in per2.partners: # remove the partner
                per2.partners.remove(per1)

        print(f"Removed relationship: {selected_relation}")

    def display_everything(self):
        headers = [ # the headers
            "Name", 
            "DOB",
            "Alive Status",
            "Ethnicity",
            "Children",
            "Partners",
            "Parents",
            "Siblings"]
        rows = []
        for person in self.family:
            name = person.name
            dob = person.dob
            alive_status = "Alive" if person.is_alive else f"Deceased ({person.death_date})"
            ethnicity = person.ethnicity
            children = ', '.join(
                child.name for child in person.children) if hasattr( # get the children
                person, 'children') and person.children else ''
            partners = ', '.join(
                partner.name for partner in person.partners) if hasattr( # get the partners
                person, 'partners') and person.partners else ''
            parents = ', '.join(
                parent.name for parent in person.parents) if hasattr( # get the parents
                person, 'parents') and person.parents else ''
            siblings = ', '.join(
                sibling.name for sibling in person.siblings) if hasattr( # get the siblings
                person, 'siblings') and person.siblings else ''

            rows.append([name, dob, alive_status, ethnicity,
                        children, partners, parents, siblings]) # add the rows

        col_widths = [len(header) for header in headers]
        for row in rows:
            for idx, item in enumerate(row):  
                col_widths[idx] = max(col_widths[idx], len(item)) # get the width

        row_format = ' | '.join(f'{{:<{width}}}' for width in col_widths) # get the format

        print('-' * (sum(col_widths) + len(col_widths) * 3 - 1)) # print the rows
        print(row_format.format(*headers))
        print('-' * (sum(col_widths) + len(col_widths) * 3 - 1)) 
        for row in rows:
            print(row_format.format(*row))
        print('-' * (sum(col_widths) + len(col_widths) * 3 - 1))

    def get_relationships(self, relationship, name):
        person_id = self.get_id(name) # get the id of the person
        if person_id is None:
            print(f'{name} does not exist!')
            return
        person = next(
            (person for person in self.family if person.id == person_id), 
            None) # get the person
        if person is None:
            print(f'{name} does not exist!')
            return
        if relationship == 'PARENTS':
            self.display_parents(person) # display the parents
        elif relationship == 'GRANDPARENTS':
            self.display_grandparents(person) # display the grandparents
        elif relationship == 'SIBLINGS':
            self.display_siblings(person) # display the siblings
        elif relationship == 'COUSINS':
            self.display_cousins(person) # display the cousins
        elif relationship == 'IMMEDIATE':
            self.display_immediate(person) # display the immediate family
        elif relationship == 'EXTENDED':
            self.display_extended(person) # display the extended family
        else:
            print(f'"{relationship}" is not a recognized relationship.')

    def get_command(self, userIn):
        pattern = r"'([^']+)'" # get the name
        names = re.findall(pattern, userIn)
        current_command = self.parse_command(userIn, "GET")
        if current_command == "CALENDAR":
            display_calendar(self.family) # display the calendar
        elif current_command == "ALLBIRTHDAYS":
            for i in range(len(self.family)):
                print(
                    f'{self.family[i].name} has the birthday of {self.family[i].dob}') # print the birthdays
        elif current_command == "SORTBIRTHDAYS":
            sorted_family = sorted(
                self.family, key=lambda member: datetime.strptime(
                    member.dob, '%Y-%m-%d')) # sort the birthdays
            for member in sorted_family:
                print(f'{member.name} has the birthday of {member.dob}') # print the birthdays
        elif current_command == "AVAGE":
            avg_age = self.calc_avage() # get the average age
            if avg_age is not None:
                print(
                    f"The average age of living family members is {avg_age:.2f} years.") # print the average age
            else:
                print("No living family members with valid date of birth.") # if there are no living family members
        elif current_command == "DAVAGE":   
            avg_death_age = self.calc_davage() # get the average death age
            if avg_death_age is not None:
                print(
                    f"The average age at death of deceased family members is {avg_death_age:.2f} years.") # print the average death age
            else:
                print("No deceased family members with valid dates of birth and death.")
        elif current_command == "INDIVCHILDCOUNT" and names:
            self.get_IndivCC(names[0]) # get the individual child count
        elif current_command == "ACPP":
            self.calc_ACPP() # get the average child per person
        elif current_command == "EVERYTHING":
            self.display_everything() # display everything
        elif current_command in ("PARENTS", "GRANDPARENTS", "SIBLINGS", "COUSINS", "IMMEDIATE", "EXTENDED") and names:
            self.get_relationships(current_command, names[0]) # get the relationships
        else:
            print(
                f'"{userIn}" isn\'t used correctly. Please type HELP to get started.')

    def display_parents(self, person):
        if hasattr(person, 'parents') and person.parents: # get the parents
            print(f'Parents of {person.name}:')
            for parent in person.parents: # print the parents
                print(f'- {parent.name}')
        else:
            print(f'{person.name} has no parents recorded.')

    def display_grandparents(self, person):
        grandparents = []
        if hasattr(person, 'parents') and person.parents: # get the grandparents
            for parent in person.parents:
                if hasattr(parent, 'parents') and parent.parents: 
                    grandparents.extend(parent.parents)
        if grandparents:
            print(f'Grandparents of {person.name}:')    # print the grandparents
            for grandparent in grandparents:
                print(f'- {grandparent.name}')
        else:
            print(f'{person.name} has no grandparents recorded.')

    def display_siblings(self, person):
        if hasattr(person, 'siblings') and person.siblings: # get the siblings
            print(f'Siblings of {person.name}:')
            for sibling in person.siblings:
                print(f'- {sibling.name}') # print the siblings
        else:
            print(f'{person.name} has no siblings recorded.')

    def display_cousins(self, person):
        cousins = []
        if hasattr(person, 'parents') and person.parents: # get the cousins
            for parent in person.parents:
                if hasattr(parent, 'siblings') and parent.siblings:
                    for aunt_uncle in parent.siblings: 
                        if hasattr(
                                aunt_uncle,
                                'children') and aunt_uncle.children:
                            cousins.extend(aunt_uncle.children)
        if cousins:
            print(f'Cousins of {person.name}:')
            for cousin in cousins:
                print(f'- {cousin.name}') # print the cousins
        else:
            print(f'{person.name} has no cousins recorded.')

    def calc_avage(self):
        from datetime import datetime
        today = datetime.today() # get the date
        ages = []
        for member in self.family:
            if member.is_alive: # get the age
                try:
                    dob = datetime.strptime(member.dob, '%Y-%m-%d')
                    age = (today - dob).days / 365.25 # get the age in years
                    ages.append(age)
                except Exception:
                    continue
        if ages:
            average_age = sum(ages) / len(ages)
            return average_age # return the average age
        else: 
            return None

    def get_IndivCC(self, name):
        person_id = self.get_id(name) # get the id of the person
        if person_id is None:
            print(f'{name} does not exist!')
            return
        person = next(
            (person for person in self.family if person.id == person_id), 
            None) # get the person
        if person is None:
            print(f'{name} does not exist!')
            return
        if hasattr(person, 'children') and person.children: # get the children
            child_count = len(person.children)
            print(
                f'{person.name} has {child_count} child{"ren" if child_count > 1 else ""}.') # print the children
        else:
            print(f'{person.name} has no children.')

    def calc_ACPP(self):
        total_children = 0
        parent_count = 0
        for member in self.family: # get the average child per person
            if hasattr(member, 'children') and member.children:
                total_children += len(member.children)
                parent_count += 1
        if parent_count > 0:
            average_children = total_children / parent_count
            print(
                f'The average number of children per person is {average_children:.2f}.') # print the average children
        else:
            print('No parents with children found in the family.')

    def calc_davage(self):
        from datetime import datetime 
        death_ages = []
        for member in self.family: # get the average death age
            if not member.is_alive and member.death_date:
                try:
                    dob = datetime.strptime(member.dob, '%Y-%m-%d')
                    death_date = datetime.strptime(
                        member.death_date, '%Y-%m-%d')
                    age_at_death = (death_date - dob).days / 365.25 # get the age at death in years
                    death_ages.append(age_at_death)
                except Exception:
                    continue
        if death_ages:
            average_death_age = sum(death_ages) / len(death_ages) # get the average death age
            return average_death_age
        else:
            return None

    def display_immediate(self, person):
        immediate_family = set()
        if hasattr(person, 'partners') and person.partners: # get the immediate family
            immediate_family.update(person.partners)
        if hasattr(person, 'parents') and person.parents:
            immediate_family.update(person.parents)
        if hasattr(person, 'children') and person.children:
            immediate_family.update(person.children)
        if hasattr(person, 'siblings') and person.siblings:
            immediate_family.update(person.siblings)
        if immediate_family:
            print(f'Immediate family of {person.name}:')
            for member in immediate_family:
                print(f'- {member.name}') # print the immediate family
        else:
            print(f'{person.name} has no immediate family recorded.')

    def display_extended(self, person):
        extended_family = set()
        grandparents = []
        if hasattr(person, 'parents') and person.parents:
            for parent in person.parents:
                if hasattr(parent, 'parents') and parent.parents:
                    grandparents.extend(parent.parents)
        extended_family.update(grandparents)
        grandchildren = []
        if hasattr(person, 'children') and person.children:
            for child in person.children:
                if hasattr(child, 'children') and child.children:
                    grandchildren.extend(child.children)
        extended_family.update(grandchildren)
        aunts_uncles = []
        if hasattr(person, 'parents') and person.parents:
            for parent in person.parents:
                if hasattr(parent, 'siblings') and parent.siblings:
                    aunts_uncles.extend(parent.siblings)
        extended_family.update(aunts_uncles)
        nieces_nephews = []
        if hasattr(person, 'siblings') and person.siblings:
            for sibling in person.siblings:
                if hasattr(sibling, 'children') and sibling.children:
                    nieces_nephews.extend(sibling.children)
        extended_family.update(nieces_nephews)
        cousins = []
        for aunt_uncle in aunts_uncles:
            if hasattr(aunt_uncle, 'children') and aunt_uncle.children:
                cousins.extend(aunt_uncle.children)
        extended_family.update(cousins)
        immediate_family = set()
        if hasattr(person, 'partners') and person.partners:
            immediate_family.update(person.partners)
        if hasattr(person, 'parents') and person.parents:
            immediate_family.update(person.parents)
        if hasattr(person, 'children') and person.children:
            immediate_family.update(person.children)
        if hasattr(person, 'siblings') and person.siblings:
            immediate_family.update(person.siblings)
        extended_family.difference_update(immediate_family) # get the extended family
        if extended_family:
            print(f'Extended family of {person.name}:') # print the extended family
            for member in extended_family:
                print(f'- {member.name}')
        else:
            print(f'{person.name} has no extended family recorded.')

    def main(self):
        print("Welcome to Family Tree CLI! Type HELP to get started!")
        print()
        while not self.progExit:
            userIn = input(">>")
            if userIn.upper().startswith("HELP"):
                self.display_help()
            elif userIn.upper().startswith("CLEAR") or userIn.upper().startswith("CLS"):
                clear.clear()
            elif userIn.upper().startswith("EXIT"):
                self.progExit = True
            elif userIn.upper().startswith("ADD"):
                self.add_remove_person(True, userIn)
            elif userIn.upper().startswith("REMOVE"):
                self.add_remove_person(False, userIn)
            elif userIn.upper().startswith("GET"):
                self.get_command(userIn)
            else:
                print(
                    f'"{userIn}" is not a valid command. Please type HELP if you are stuck.')


if __name__ == "__main__":
    family_tree = FamilyTree()
    family_tree.main()
