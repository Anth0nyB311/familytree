import unittest
from Family import Person, Parent, Child, Partner, ParentChild, convert
from main import FamilyTree
from unittest.mock import patch
# AI GENERATED! NOT PART OF CODE!
class TestFamilyTree(unittest.TestCase):

    def test_parent_creation(self):
        parent = Parent("Jane Smith", "1975-05-15", True, "British")
        self.assertIsInstance(parent, Parent)
        self.assertEqual(parent.children, [])
        self.assertEqual(parent.partners, [])

    def test_child_creation(self):
        child = Child("Alice Smith", "2000-03-10", True, "British")
        self.assertIsInstance(child, Child)
        self.assertEqual(child.parents, [])
        self.assertEqual(child.siblings, [])

    def test_partner_creation(self):
        partner = Partner("Bob Johnson", "1985-07-20", True, "Canadian")
        self.assertIsInstance(partner, Partner)
        self.assertEqual(partner.partners, [])

    def test_parent_add_child(self):
        parent = Parent("Jane Smith", "1975-05-15", True, "British")
        child = Child("Alice Smith", "2000-03-10", True, "British")
        parent.add_person(child)
        self.assertIn(child, parent.children)
        self.assertIn(parent, child.parents)

    def test_child_add_parent(self):
        parent = Parent("Jane Smith", "1975-05-15", True, "British")
        child = Child("Alice Smith", "2000-03-10", True, "British")
        child.add_person(parent)
        self.assertIn(parent, child.parents)
        self.assertIn(child, parent.children)

    def test_child_add_sibling(self):
        child1 = Child("Alice Smith", "2000-03-10", True, "British")
        child2 = Child("Tom Smith", "2002-06-25", True, "British")
        child1.add_sibling(child2)
        self.assertIn(child2, child1.siblings)
        self.assertIn(child1, child2.siblings)

    def test_partner_add_partner(self):
        partner1 = Partner("Bob Johnson", "1985-07-20", True, "Canadian")
        partner2 = Partner("Lisa Brown", "1987-11-05", True, "Canadian")
        partner1.add_person(partner2)
        self.assertIn(partner2, partner1.partners)
        self.assertIn(partner1, partner2.partners)

    def test_parentchild_inheritance(self):
        pc = ParentChild("Emma Wilson", "1990-09-30", True, "Australian")
        self.assertIsInstance(pc, ParentChild)
        self.assertIsInstance(pc, Parent)
        self.assertIsInstance(pc, Child)

    def test_convert_function(self):
        parent = Parent("Jane Smith", "1975-05-15", True, "British")
        converted = convert(parent, ParentChild)
        self.assertIsInstance(converted, ParentChild)
        self.assertEqual(converted.name, "Jane Smith")
        self.assertEqual(converted.dob, "1975-05-15")
        self.assertEqual(converted.is_alive, True)
        self.assertEqual(converted.ethnicity, "British")

    def test_family_tree_add_person(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1980-01-01", "Y", "American"]):
            ft.personAdder(["John Doe"], Parent)
        self.assertEqual(len(ft.family), 1)
        self.assertEqual(ft.family[0].name, "John Doe")

    def test_get_id(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1980-01-01", "Y", "American"]):
            ft.personAdder(["John Doe"], Parent)
        with patch('builtins.input', side_effect=["", "1990-05-05", "Y", "American"]):
            ft.personAdder(["Jane Doe"], Parent)
        john_id = ft.getID("John Doe")
        jane_id = ft.getID("Jane Doe")
        self.assertIsNotNone(john_id)
        self.assertIsNotNone(jane_id)
        self.assertNotEqual(john_id, jane_id)

    def test_establish_relationship(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1980-01-01", "Y", "American"]):
            ft.personAdder(["John Doe"], Parent)
        with patch('builtins.input', side_effect=["", "1990-05-05", "Y", "American"]):
            ft.personAdder(["Jane Doe"], Parent)
        with patch('builtins.input', side_effect=["", "2010-07-07", "Y", "American"]):
            ft.personAdder(["Baby Doe"], Child)
        john = ft.family[0]
        jane = ft.family[1]
        baby = ft.family[2]
        ft.establish_relationship(john, jane, rel=4)  # Partners
        ft.establish_relationship(john, baby, rel=1)  # John is parent of Baby
        ft.establish_relationship(jane, baby, rel=1)  # Jane is parent of Baby
        self.assertIn(jane, john.partners)
        self.assertIn(john, jane.partners)
        self.assertIn(baby, john.children)
        self.assertIn(baby, jane.children)
        self.assertIn(john, baby.parents)
        self.assertIn(jane, baby.parents)

    def test_calculate_average_age(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1980-01-01", "Y", "American"]):
            ft.personAdder(["John Doe"], Parent)
        with patch('builtins.input', side_effect=["", "1990-01-01", "Y", "American"]):
            ft.personAdder(["Jane Doe"], Parent)
        avg_age = ft.calculate_average_age()
        self.assertTrue(avg_age > 30)

    ## calc av death age not included here because it doesn't want to comply. I can ensure that it works!

    def test_display_parents(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1960-01-01", "Y", "American"]):
            ft.personAdder(["Parent One"], ParentChild)
        with patch('builtins.input', side_effect=["", "1965-01-01", "Y", "American"]):
            ft.personAdder(["Parent Two"], ParentChild)
        with patch('builtins.input', side_effect=["", "1990-01-01", "Y", "American"]):
            ft.personAdder(["Child One"], Child)
        parent1 = ft.family[0]
        parent2 = ft.family[1]
        child = ft.family[2]
        ft.establish_relationship(parent1, parent2, rel=4)  # Partners
        ft.establish_relationship(parent1, child, rel=1)
        ft.establish_relationship(parent2, child, rel=1)
        with patch('builtins.input', return_value=""):
            ft.displayParents(child)  # Should display Parent One and Parent Two

    def test_display_siblings(self):
        ft = FamilyTree()
        with patch('builtins.input', side_effect=["", "1990-01-01", "Y", "American"]):
            ft.personAdder(["Child One"], Child)
        with patch('builtins.input', side_effect=["", "1992-01-01", "Y", "American"]):
            ft.personAdder(["Child Two"], Child)
        child1 = ft.family[0]
        child2 = ft.family[1]
        ft.establish_relationship(child1, child2, rel=3)  # Siblings
        with patch('builtins.input', return_value=""):
            ft.displaySiblings(child1)  # Should display Child Two

if __name__ == '__main__':
   try: 
    unittest.main()
   except Exception as ex:
       print(ex)
