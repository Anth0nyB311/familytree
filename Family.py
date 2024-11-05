from abc import ABC, abstractmethod # allows us to make abstract classes and methods


class Person(ABC):
    _id_counter = 1

    def __init__(self, name, dob, is_alive, ethnicity, death_date=None): # persons attributes
        self.id = Person._id_counter
        Person._id_counter += 1 # every person gets an ID so we can resolve collisions
        self.name = name
        self.dob = dob
        self.is_alive = is_alive
        self.ethnicity = ethnicity
        self.death_date = death_date # Not needed to be passed in, if the person is alive, this will be None

    @abstractmethod
    def add_person(self, person): # abstract method to add a relationship to a person
        pass

    def __str__(self): # debugging purposes only
        alive_status = "Alive" if self.is_alive else f"Deceased ({self.death_date})"
        return f"ID: {self.id}, Name: {self.name}, DOB: {self.dob}, Status: {alive_status}, Ethnicity: {self.ethnicity}"


class Parent(Person):
    """This class represents a parent in the family tree, can only have children and partners."""
    def __init__(self, name, dob, is_alive, ethnicity, death_date=None):
        super().__init__(name, dob, is_alive, ethnicity, death_date) # inherit from the person class
        self.children = []
        self.partners = []

    def add_person(self, child): # add a child to the parent and makes sure only a child can be added
        if isinstance(child, Child):
            if child not in self.children:
                self.children.append(child)
                if self not in child.parents:
                    child.parents.append(self)
        else:
            raise TypeError("You can only add a Child instance!")

    def add_partner(self, partner): # add a partner to the parent and makes sure only a parent  can be added
        if isinstance(partner, Parent):
            if partner not in self.partners:
                self.partners.append(partner)
                if self not in partner.partners:
                    partner.partners.append(self)
        else:
            raise TypeError("You can only add a Parent instance as a partner!")
        # You might ask yourself, why didn't you add a Partner inside add_partner? Because the code will convert the person into a ParentChild instance as mostly in real life, a partner is a parent as well.

class Child(Person):
    def __init__(self, name, dob, is_alive, ethnicity, death_date=None): # same as parent but with siblings and now as a child
        super().__init__(name, dob, is_alive, ethnicity, death_date)
        self.parents = []
        self.siblings = []

    def add_person(self, parent):
        if isinstance(parent, Parent):
            if parent not in self.parents:
                self.parents.append(parent)
                if self not in parent.children:
                    parent.children.append(self)
        else:
            raise TypeError("You can only add a Parent instance!")

    def add_sibling(self, sibling):
        if isinstance(sibling, Child):
            if sibling not in self.siblings:
                self.siblings.append(sibling)
                if self not in sibling.siblings:
                    sibling.siblings.append(self)
        else:
            raise TypeError("You can only add a Child instance as a sibling!")


class Partner(Person): # Same as before but now with partners
    def __init__(self, name, dob, is_alive, ethnicity, death_date=None):
        super().__init__(name, dob, is_alive, ethnicity, death_date)
        self.partners = []

    def add_person(self, partner):
        if isinstance(partner, Partner):
            if partner not in self.partners:
                self.partners.append(partner)
                if self not in partner.partners:
                    partner.partners.append(self)
        else:
            raise TypeError("You can only add a Partner instance!")


class ParentChild(Parent, Child):
    def __init__(self, name, dob, is_alive, ethnicity, death_date=None):
        Person.__init__(self, name, dob, is_alive, ethnicity, death_date)
        self.children = []
        self.partners = []
        self.parents = []
        self.siblings = []

    def add_person(self, person):
        if isinstance(person, Child):
            if person not in self.children:
                self.children.append(person)
                if self not in person.parents:
                    person.parents.append(self)
        elif isinstance(person, Parent):
            if person not in self.parents:
                self.parents.append(person)
                if self not in person.children:
                    person.children.append(self)
        else:
            raise TypeError("You can only add a Parent or Child instance!")

    def add_partner(self, partner):
        if isinstance(partner, (Parent, ParentChild)):
            if partner not in self.partners:
                self.partners.append(partner)
                if self not in partner.partners:
                    partner.partners.append(self)
        else:
            raise TypeError(
                "You can only add a Parent or ParentChild instance as a partner!")

    def add_sibling(self, sibling):
        if isinstance(sibling, Child):
            if sibling not in self.siblings:
                self.siblings.append(sibling)
                if self not in sibling.siblings:
                    sibling.siblings.append(self)
        else:
            raise TypeError("You can only add a Child instance as a sibling!")


def convert(instance, new_class):
    new_instance = new_class(
        name=instance.name,
        dob=instance.dob,
        is_alive=instance.is_alive,
        ethnicity=instance.ethnicity,
        death_date=instance.death_date
    )
    new_instance.id = instance.id
    if hasattr(instance, 'children'):
        new_instance.children = instance.children
        for child in new_instance.children:
            child.parents = [new_instance if parent.id ==
                             instance.id else parent for parent in child.parents]
    if hasattr(instance, 'parents'):
        new_instance.parents = instance.parents
        for parent in new_instance.parents:
            parent.children = [new_instance if child.id ==
                               instance.id else child for child in parent.children]
    if hasattr(instance, 'partners'):
        new_instance.partners = instance.partners
        for partner in new_instance.partners:
            partner.partners = [new_instance if p.id ==
                                instance.id else p for p in partner.partners]
    if hasattr(instance, 'siblings'):
        new_instance.siblings = instance.siblings
        for sibling in new_instance.siblings:
            sibling.siblings = [new_instance if s.id ==
                                instance.id else s for s in sibling.siblings]

    return new_instance
