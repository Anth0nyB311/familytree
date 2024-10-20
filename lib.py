class Lineage:
    def __init__(self):
        self.persons = []

    def add_person(self, person):
        self.persons.append(person)

class Person:
    def __init__(self, id, name, dob, is_alive, ethnicity):
        self.id = id
        self.name = name
        self.dob = dob
        self.is_alive = is_alive
        self.ethnicity = ethnicity
