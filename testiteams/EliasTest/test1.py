from abc import ABC, abstractmethod
from clear import clear
class Person(ABC):
    def __init__(self, name, dob, is_alive, ethnicity):
        self.name = name
        self.dob = dob
        self.is_alive = is_alive
        self.ethnicity = ethnicity

    @abstractmethod
    def add_person(self, person):
        """Abstract method to add a person to the relationship."""
        pass

class Parent(Person):
    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.children = []

    def add_person(self, child):
        """Add a child to the parent."""
        if isinstance(child, Child):
            self.children.append(child)
            child.parents.append(self)
        else:
            raise TypeError("You can only add a Child instance!")

class Child(Person):
    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.parents = []

    def add_person(self, parent):
        """Add a parent to the child."""
        if isinstance(parent, Parent):
            self.parents.append(parent)
            parent.children.append(self)
        else:
            raise TypeError("You can only add a Parent instance!")

class Partner(Person):
    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.partners = []

    def add_person(self, partner):
        """Add a partner."""
        if isinstance(partner, Partner):
            self.partners.append(partner)
            partner.partners.append(self)
        else:
            raise TypeError("You can only add a Partner instance!")

class FamilyTree:
    def __init__(self):
       self.family = []
    def _getAliveStatus(self, status):
        if status.lower() == "y" or status.lower() == "yes":
            return True
        return False
    def create_new_person(self,personType):
        """This code creates a new Person vairable and stores them into the Lineage list."""
        qList = ["Please enter the name:", "Please enter the DOB:", "Are they/you alive?:", "What is their ethnicity?:"]
        userIn = [len(qList)]
        for i in range(len(qList)):
            userIn.append(input(qList[i]))
        tempPerson = personType(userIn[0],userIn[1],self._getAliveStatus(userIn[2]),userIn[3])
        return tempPerson

    def firstTime(self):
        print()
        print("Welcome to the Family Tree Program!")
        print()
        print("Lets add you first!")
        currentUser = self.create_new_person(Child)
        self.family.append(currentUser)
        clear()
    def mainMenu(self):


    def main(self):
        self.firstTime();
       

    
if __name__ == "__main__":
    family_tree = FamilyTree()
    family_tree.main()