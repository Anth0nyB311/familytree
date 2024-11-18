"""Base family member classes"""

from abc import ABC, abstractmethod
import sys
import subprocess
from datetime import datetime


class Person(ABC):
    """Base class for all people."""

    _id_counter = 1

    def __init__(self, name, dob, is_alive, ethnicity):
        self.id = Person._id_counter
        Person._id_counter += 1
        self.name = name
        self.dob = dob
        self.is_alive = is_alive
        self.ethnicity = ethnicity
        self._death_date = None

    @abstractmethod
    def add_person(self, person):
        """Abstract method to add a relationship to a person."""
        print("This method should be implemented in a subclass!")

    def __str__(self):
        alive_status = "Alive" if self.is_alive else f"Died ({self.death_date})"
        return (
            f"ID: {self.id}, Name: {self.name}, DOB: {self.dob}, "
            f"Status: {alive_status}, Eth: {self.ethnicity}"
        )

    @property
    def death_date(self):
        """Getter for death_date."""
        return self._death_date

    @death_date.setter
    def death_date(self, date):
        """Setter for death_date with validation."""
        if not self.is_alive and date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                self._death_date = date
            except ValueError as exc:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD.") from exc
        elif self.is_alive:
            self._death_date = None
        else:
            self._death_date = None


class Parent(Person):
    """Represents a parent in the family tree."""

    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.children = []
        self.partners = []

    def add_person(self, person):
        """Add a child to the parent."""
        if isinstance(person, Child):
            if person not in self.children:
                self.children.append(person)
                if self not in person.parents:
                    person.parents.append(self)
        else:
            raise TypeError("You can only add a Child instance!")

    def add_partner(self, person):
        """Add a partner to the parent."""
        if isinstance(person, Parent):
            if person not in self.partners:
                self.partners.append(person)
                if self not in person.partners:
                    person.partners.append(self)
        else:
            raise TypeError("You can only add a Parent instance as a partner!")


class Child(Person):
    """Represents a child in the family tree."""

    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.parents = []
        self.siblings = []

    def add_person(self, person):
        """Add a parent to the child."""
        if isinstance(person, Parent):
            if person not in self.parents:
                self.parents.append(person)
                if self not in person.children:
                    person.children.append(self)
        else:
            raise TypeError("You can only add a Parent instance!")

    def add_sibling(self, person):
        """Add a sibling to the child."""
        if isinstance(person, Child):
            if person not in self.siblings:
                self.siblings.append(person)
                if self not in person.siblings:
                    person.siblings.append(self)
        else:
            raise TypeError("You can only add a Child instance as a sibling!")


class Partner(Person):
    """Represents a partner in the family tree."""

    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.partners = []

    def add_person(self, person):
        """Add a partner."""
        if isinstance(person, Partner):
            if person not in self.partners:
                self.partners.append(person)
                if self not in person.partners:
                    person.partners.append(self)
        else:
            raise TypeError("You can only add a Partner instance!")


class ParentChild(Parent, Child):
    """Hybrid class of Parent and Child."""

    def __init__(self, name, dob, is_alive, ethnicity):
        super().__init__(name, dob, is_alive, ethnicity)
        self.children = []
        self.partners = []
        self.parents = []
        self.siblings = []

    def add_person(self, person):
        """Add a person as a child or parent."""
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

    def add_partner(self, person):
        """Add a partner to this person."""
        if isinstance(person, (Parent, ParentChild)):
            if person not in self.partners:
                self.partners.append(person)
                if self not in person.partners:
                    person.partners.append(self)
        else:
            raise TypeError(
                "You can only add a Parent or ParentChild instance as a partner!"
            )

    def add_sibling(self, person):
        """Add a sibling to this person."""
        if isinstance(person, Child):
            if person not in self.siblings:
                self.siblings.append(person)
                if self not in person.siblings:
                    person.siblings.append(self)
        else:
            raise TypeError("You can only add a Child instance as a sibling!")


def convert(instance, new_class):
    """Convert an instance to a new class, preserving relationships."""
    new_instance = new_class(
        name=instance.name,
        dob=instance.dob,
        is_alive=instance.is_alive,
        ethnicity=instance.ethnicity,
    )
    new_instance.id = instance.id
    if hasattr(instance, "children"):
        new_instance.children = instance.children
        for child in new_instance.children:
            child.parents = [
                new_instance if parent.id == instance.id else parent
                for parent in child.parents
            ]
    if hasattr(instance, "parents"):
        new_instance.parents = instance.parents
        for parent in new_instance.parents:
            parent.children = [
                new_instance if child.id == instance.id else child
                for child in parent.children
            ]
    if hasattr(instance, "partners"):
        new_instance.partners = instance.partners
        for partner in new_instance.partners:
            partner.partners = [
                new_instance if p.id == instance.id else p for p in partner.partners
            ]
    if hasattr(instance, "siblings"):
        new_instance.siblings = instance.siblings
        for sibling in new_instance.siblings:
            sibling.siblings = [
                new_instance if s.id == instance.id else s for s in sibling.siblings
            ]

    return new_instance  # This acts like a global function that can be used anywhere in the code.
if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"],check=True)
    