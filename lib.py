import time, datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom
class Lineage:
    def __init__(self):
        self.persons = []

    def _getAliveStatus(self, status):
        if status.lower() == "y" or status.lower() == "yes":
            return True
        return False
    def _add_person(self, person):
        self.persons.append(person)

    def create_new_person_cli(self):
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
    def saveProgress(self, lineages):
        ts = time.time()
        rootNode = ET.Element("FamilyTree")
        for i, lineage in enumerate(lineages): 
            lineage = ET.SubElement(rootNode, "Lineage", id=str(i)) 
            person_id = 1  
            for person in lineage.persons:
                person_element = ET.SubElement(lineage, "Person", id=str(person_id))  
                ET.SubElement(person_element, "Name").text = str(person.name)
                ET.SubElement(person_element, "DOB").text = str(person.dob)
                ET.SubElement(person_element, "AliveStatus").text = str(person.is_alive)  
                ET.SubElement(person_element, "Ethnicity").text = str(person.ethnicity)
                person_id += 1 
        filename = "family_tree_" + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S') + ".xml"
        tree = ET.ElementTree(rootNode)
        rough_string = ET.tostring(rootNode, encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(pretty_xml)

    def importProgress(self,file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        lineages = []
        for lineage_element in root.findall('Lineage'):
            lineage_id = lineage_element.get('id')
            lineage = Lineage()
            for person_element in lineage_element.findall('Person'):
                person = Person(
                    name=person_element.find('Name').text,
                    dob=person_element.find('DOB').text,
                    is_alive=person_element.find('AliveStatus').text,
                    ethnicity=person_element.find('Ethnicity').text
                )
                lineage._add_person(person)
            lineages.append(lineage)

        return lineages




