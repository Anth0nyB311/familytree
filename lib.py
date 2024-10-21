import xml.etree.ElementTree as ET
class Lineage:
    def __init__(self):
        self.persons = []

    def _getAliveStatus(self, status):
        if status.lower() == "y" or status.lower() == "yes":
            return True
        return False
    def _add_person(self, person):
        self.persons.append(person)

    def create_new_person(self):
        """This code creates a new Person vairable and stores them into the Lineage list."""
        qList = ["Please enter the name:", "Please enter the DOB:", "Are they alive?:", "What is their ethnicity?:"]
        userIn = [len(qList)]
        for i in range(len(qList)):
            userIn.append(input(qList[i]))
        tempPerson = Person(userIn[0],userIn[1],self._getAliveStatus(userIn[2]),userIn[3])
        self._add_person(tempPerson)
    
# Note for me, in order to use private methods or variables. You must use SELF!

class Person:
    def __init__(self, name, dob, is_alive, ethnicity):
        self.name = name
        self.dob = dob
        self.is_alive = is_alive
        self.ethnicity = ethnicity

class ImExPorter:
    def saveProgress(lineages):
        rootNode = ET.Element("FamilyTree")

