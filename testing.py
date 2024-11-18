import unittest
from main import FamilyTree, FamilyTreeStatistics
from family_lib import Person, Parent, ParentChild, Partner, Child, convert
import family_calendar
import yaml_lib
from datetime import datetime
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
import io
from contextlib import redirect_stdout

class TestFamilyLib(unittest.TestCase):
    def test_person_death_date_property(self):
        # Since Person is abstract, test via a subclass
        parent = Parent(name="John Doe", dob="1980-01-01", is_alive=True, ethnicity="American")
        self.assertTrue(parent.is_alive)
        self.assertIsNone(parent.death_date)
        
        # Set death date when is_alive is False
        parent.is_alive = False
        parent.death_date = "2020-01-01"
        self.assertEqual(parent.death_date, "2020-01-01")
        
        # Try setting invalid death date
        with self.assertRaises(ValueError):
            parent.death_date = "invalid-date"
        
        # Set death date when is_alive is True
        parent.is_alive = True
        parent.death_date = "2020-01-01"
        self.assertIsNone(parent.death_date)
    
    def test_person_str_method(self):
        parent = Parent(name="John Doe", dob="1980-01-01", is_alive=False, ethnicity="American")
        parent.death_date = "2020-01-01"
        expected_str = f"ID: {parent.id}, Name: John Doe, DOB: 1980-01-01, Status: Died (2020-01-01), Eth: American"
        self.assertEqual(str(parent), expected_str)
    
    def test_parent_add_person(self):
        parent = Parent(name="Parent", dob="1980-01-01", is_alive=True, ethnicity="American")
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        parent.add_person(child)
        self.assertIn(child, parent.children)
        self.assertIn(parent, child.parents)
        
        # Try adding invalid type
        with self.assertRaises(TypeError):
            parent.add_person(parent)
    
    def test_parent_add_partner(self):
        parent1 = Parent(name="Parent1", dob="1980-01-01", is_alive=True, ethnicity="American")
        parent2 = Parent(name="Parent2", dob="1982-02-02", is_alive=True, ethnicity="American")
        parent1.add_partner(parent2)
        self.assertIn(parent2, parent1.partners)
        self.assertIn(parent1, parent2.partners)
        
        # Try adding invalid type
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            parent1.add_partner(child)
    
    def test_child_add_person(self):
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        parent = Parent(name="Parent", dob="1980-01-01", is_alive=True, ethnicity="American")
        child.add_person(parent)
        self.assertIn(parent, child.parents)
        self.assertIn(child, parent.children)
        
        # Try adding invalid type
        with self.assertRaises(TypeError):
            child.add_person(child)
    
    def test_child_add_sibling(self):
        child1 = Child(name="Child1", dob="2005-05-15", is_alive=True, ethnicity="American")
        child2 = Child(name="Child2", dob="2007-07-20", is_alive=True, ethnicity="American")
        child1.add_sibling(child2)
        self.assertIn(child2, child1.siblings)
        self.assertIn(child1, child2.siblings)
        
        # Try adding invalid type
        parent = Parent(name="Parent", dob="1980-01-01", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            child1.add_sibling(parent)
    
    def test_partner_add_person(self):
        partner1 = Partner(name="Partner1", dob="1980-01-01", is_alive=True, ethnicity="American")
        partner2 = Partner(name="Partner2", dob="1982-02-02", is_alive=True, ethnicity="American")
        partner1.add_person(partner2)
        self.assertIn(partner2, partner1.partners)
        self.assertIn(partner1, partner2.partners)
        
        # Try adding invalid type
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            partner1.add_person(child)
    
    def test_parentchild_add_person(self):
        pc = ParentChild(name="ParentChild", dob="1980-01-01", is_alive=True, ethnicity="American")
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        parent = Parent(name="Parent", dob="1960-01-01", is_alive=True, ethnicity="American")
        pc.add_person(child)
        self.assertIn(child, pc.children)
        self.assertIn(pc, child.parents)
        pc.add_person(parent)
        self.assertIn(parent, pc.parents)
        self.assertIn(pc, parent.children)
        
        # Try adding invalid type
        partner = Partner(name="Partner", dob="1982-02-02", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            pc.add_person(partner)
    
    def test_parentchild_add_partner(self):
        pc1 = ParentChild(name="PC1", dob="1980-01-01", is_alive=True, ethnicity="American")
        pc2 = ParentChild(name="PC2", dob="1982-02-02", is_alive=True, ethnicity="American")
        pc1.add_partner(pc2)
        self.assertIn(pc2, pc1.partners)
        self.assertIn(pc1, pc2.partners)
        
        # Try adding invalid type
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            pc1.add_partner(child)
    
    def test_parentchild_add_sibling(self):
        pc = ParentChild(name="PC", dob="1980-01-01", is_alive=True, ethnicity="American")
        child = Child(name="Child", dob="1982-02-02", is_alive=True, ethnicity="American")
        pc.add_sibling(child)
        self.assertIn(child, pc.siblings)
        self.assertIn(pc, child.siblings)
        
        # Try adding invalid type
        parent = Parent(name="Parent", dob="1960-01-01", is_alive=True, ethnicity="American")
        with self.assertRaises(TypeError):
            pc.add_sibling(parent)
    
    def test_convert_function(self):
        parent = Parent(name="Parent", dob="1980-01-01", is_alive=True, ethnicity="American")
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        parent.add_person(child)
        
        pc = convert(parent, ParentChild)
        self.assertIsInstance(pc, ParentChild)
        self.assertEqual(pc.name, parent.name)
        self.assertEqual(pc.id, parent.id)
        self.assertEqual(pc.children, parent.children)
        self.assertEqual(pc.partners, parent.partners)
        # Ensure relationships are updated
        for c in pc.children:
            self.assertIn(pc, c.parents)

class TestYamlLib(unittest.TestCase):
    def test_return_save_filename(self):
        filename = yaml_lib.return_save_filename()
        self.assertTrue(filename.startswith("family_tree_"))
        self.assertTrue(filename.endswith(".yaml"))
    
    def test_yaml_export_import(self):
        # Create a family
        parent = Parent(name="Parent", dob="1980-01-01", is_alive=True, ethnicity="American")
        child = Child(name="Child", dob="2005-05-15", is_alive=True, ethnicity="American")
        parent.add_person(child)
        family = [parent, child]
        
        # Export to YAML
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            filename = temp_file.name
            yaml_lib.yaml_export(family, filename=filename)
        
        # Import from YAML
        imported_family = yaml_lib.yaml_import(filename)
        os.remove(filename)
        
        # Test imported data
        self.assertEqual(len(imported_family), 2)
        imported_parent = next(p for p in imported_family if p.name == "Parent")
        imported_child = next(p for p in imported_family if p.name == "Child")
        self.assertIn(imported_child, imported_parent.children)
        self.assertIn(imported_parent, imported_child.parents)
    
    def test_yaml_import_file_not_found(self):
        # Import from a non-existent file
        imported_family = yaml_lib.yaml_import("non_existent_file.yaml")
        self.assertEqual(len(imported_family), 0)

class TestFamilyCalendar(unittest.TestCase):
    def test_get_ordinal_suffix(self):
        self.assertEqual(family_calendar.get_ordinal_suffix(1), 'st')
        self.assertEqual(family_calendar.get_ordinal_suffix(2), 'nd')
        self.assertEqual(family_calendar.get_ordinal_suffix(3), 'rd')
        self.assertEqual(family_calendar.get_ordinal_suffix(4), 'th')
        self.assertEqual(family_calendar.get_ordinal_suffix(11), 'th')
        self.assertEqual(family_calendar.get_ordinal_suffix(21), 'st')
        self.assertEqual(family_calendar.get_ordinal_suffix(22), 'nd')
        self.assertEqual(family_calendar.get_ordinal_suffix(23), 'rd')
        self.assertEqual(family_calendar.get_ordinal_suffix(31), 'st')
    
    def test_get_birthdays_in_month(self):
        # Prepare sample data
        important_dates = [
            {"name": "John Doe", "month": 1, "day": 15, "dob": datetime(1980, 1, 15), "death_date": None},
            {"name": "Jane Doe", "month": 1, "day": 20, "dob": datetime(1985, 1, 20), "death_date": datetime(2020, 1, 25)},
            {"name": "Jim Doe", "month": 2, "day": 5, "dob": datetime(1990, 2, 5), "death_date": None},
        ]
        birthdays_in_january = family_calendar.get_birthdays_in_month(important_dates, 1, 2023)
        self.assertIn(15, birthdays_in_january)
        self.assertIn(20, birthdays_in_january)
        self.assertNotIn(5, birthdays_in_january)
    
    def test_format_birthday_line(self):
        # Test for alive person
        line = family_calendar.format_birthday_line(15, {
            "name": "John Doe",
            "age": 43,
            "dob": datetime(1980, 1, 15),
            "is_alive": True,
        }, 1)
        self.assertIn("John Doe", line)
        self.assertIn("Age 43", line)
        # Test for deceased person
        line = family_calendar.format_birthday_line(20, {
            "name": "Jane Doe",
            "age_at_death": 35,
            "death_date": datetime(2020, 1, 25),
            "dob": datetime(1985, 1, 20),
            "is_alive": False,
        }, 1)
        self.assertIn("Jane Doe", line)
        self.assertIn("Age at Death 35", line)

class TestFamilyTree(unittest.TestCase):
    def setUp(self):
        # Load the family data from family_tree_demo.yaml
        self.demo_yaml_file = 'family_tree_demo.yaml'  # Adjust the filename if necessary
        self.family = yaml_lib.yaml_import(self.demo_yaml_file)
        self.family_tree = FamilyTree(save_file=self.demo_yaml_file)
        self.family_tree.family = self.family
        self.family_tree.stats = FamilyTreeStatistics(self.family)
    
    def test_parse_command(self):
        cmd = self.family_tree.parse_command("ADD CHILD 'John'", "ADD")
        self.assertEqual(cmd, "CHILD")
        cmd = self.family_tree.parse_command("GET PARENTS OF 'Jane'", "GET")
        self.assertEqual(cmd, "PARENTS")
        cmd = self.family_tree.parse_command("REMOVE CHILD 'Jake'", "REMOVE")
        self.assertEqual(cmd, "CHILD")
    
    def test_valid_dob(self):
        self.assertTrue(self.family_tree.valid_dob("1980-01-01"))
        self.assertFalse(self.family_tree.valid_dob("invalid-date"))
    
    def test_get_headers(self):
        headers = self.family_tree.get_headers()
        expected_headers = [
            "Name",
            "DOB",
            "Alive Status",
            "Ethnicity",
            "Children",
            "Partners",
            "Parents",
            "Siblings",
        ]
        self.assertEqual(headers, expected_headers)
    
    def test_get_family_rows(self):
        rows = self.family_tree.get_family_rows(self.family)
        self.assertEqual(len(rows), len(self.family))
        # Check that the first row corresponds to a known person
        self.assertIn('Jake Smith', [row[0] for row in rows])
    
    def test_handle_all_birthdays(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree._FamilyTree__handle_all_birthdays()
            output = buf.getvalue()
        self.assertIn("Jake Smith has the birthday of 2015-05-25", output)
    
    def test_handle_sort_birthdays(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree._FamilyTree__handle_sort_birthdays()
            output = buf.getvalue()
        # Check that the output contains sorted birthdays
        self.assertIn("07-18: Lucy Cartwrite", output)
    
    def test_handle_avage(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree._FamilyTree__handle_avage()
            output = buf.getvalue()
        self.assertIn("The average age of living family members is", output)
    
    def test_handle_davage(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree._FamilyTree__handle_davage()
            output = buf.getvalue()
        self.assertIn("Average age at death is", output)
    
    def test_invalid_usage(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree._FamilyTree__invalid_usage("Invalid Command")
            output = buf.getvalue()
        self.assertIn("isn't used correctly. Please type HELP to get started.", output)
    
    def test_person_adder(self):
        # Simulate user input for adding a person
        with patch('builtins.input', side_effect=['Smith', '1990-01-01', 'Y', 'English']):
            self.family_tree.person_adder(['Michael'], Parent)
        # Check that 'Michael Smith' is in the family
        names = [member.name for member in self.family_tree.family]
        self.assertIn('Michael Smith', names)
    
    def test_add_remove_person_add(self):
        # Test adding a person using add_remove_person
        with patch('builtins.input', side_effect=['Smith', '1990-01-01', 'Y', 'English']):
            self.family_tree.add_remove_person(True, "ADD PARENT 'Michael'")
        names = [member.name for member in self.family_tree.family]
        self.assertIn('Michael Smith', names)
    
    def test_add_remove_person_remove(self):
        # Test removing a person using add_remove_person
        initial_count = len(self.family_tree.family)
        self.family_tree.add_remove_person(False, "REMOVE CHILD 'Jake Smith'")
        new_count = len(self.family_tree.family)
        self.assertEqual(new_count, initial_count - 1)
        names = [member.name for member in self.family_tree.family]
        self.assertNotIn('Jake Smith', names)
    
    def test_establish_relationship(self):
        # Test establishing a relationship
        jake = next((member for member in self.family_tree.family if member.name == 'Jake Smith'), None)
        laura = next((member for member in self.family_tree.family if member.name == 'Laura Smith'), None)
        self.family_tree.establish_relationship(jake, laura, rel=3)
        self.assertIn(laura, jake.siblings)
        self.assertIn(jake, laura.siblings)
    
    def test_person_remover(self):
        # Test removing a person
        initial_count = len(self.family_tree.family)
        self.family_tree.person_remover(['Laura Smith'])
        new_count = len(self.family_tree.family)
        self.assertEqual(new_count, initial_count - 1)
        names = [member.name for member in self.family_tree.family]
        self.assertNotIn('Laura Smith', names)
    
    def test_remove_relationship(self):
        # Test removing a relationship
        # Remove partnership between Josh Smith and Lima Smith
        josh = next((member for member in self.family_tree.family if member.name == 'Josh Smith'), None)
        lima = next((member for member in self.family_tree.family if member.name == 'Lima Smith'), None)
        self.assertIn(lima, josh.partners)
        with patch('builtins.input', return_value='1'):
            self.family_tree.remove_relationship(josh, lima)
        self.assertNotIn(lima, josh.partners)
    
    def test_get_relationships(self):
        # Test get_relationships method
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree.get_relationships('PARENTS', 'Jake Smith')
            output = buf.getvalue()
        self.assertIn('Parents of Jake Smith:', output)
        self.assertIn('- Josh Smith', output)
        self.assertIn('- Lima Smith', output)
    
    def test_display_everything(self):
        # Test that display_everything runs without error
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree.display_everything()
            output = buf.getvalue()
        # Check that key family members are in the output
        self.assertIn('Jake Smith', output)
        self.assertIn('Josh Smith', output)
    
    def test_display_help(self):
        # Test that display_help runs without error
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree.display_help()
            output = buf.getvalue()
        self.assertIn("How to use program", output)
    
    def test_get_command(self):
        # Test get_command method with various inputs
        with patch.object(self.family_tree, '_FamilyTree__handle_avage') as mock_avage:
            self.family_tree.get_command("GET AVAGE")
            mock_avage.assert_called_once()
        with patch.object(self.family_tree, '_FamilyTree__handle_all_birthdays') as mock_birthdays:
            self.family_tree.get_command("GET ALLBIRTHDAYS")
            mock_birthdays.assert_called_once()
        # Test invalid command
        with io.StringIO() as buf, redirect_stdout(buf):
            self.family_tree.get_command("GET UNKNOWN")
            output = buf.getvalue()
        self.assertIn("isn't used correctly. Please type HELP to get started.", output)

class TestFamilyTreeStatistics(unittest.TestCase):
    def setUp(self):
        # Load the family data from family_tree_demo.yaml
        self.demo_yaml_file = 'family_tree_demo.yaml'
        self.family = yaml_lib.yaml_import(self.demo_yaml_file)
        self.stats = FamilyTreeStatistics(self.family)
    
    def test_get_grandparents(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        grandparents = self.stats.get_grandparents(jake)
        grandparent_names = [gp.name for gp in grandparents]
        expected_grandparents = ['Bob Smith', 'Jenny Smith', 'Logan Cartwrite', 'Lucy Cartwrite']
        for name in expected_grandparents:
            self.assertIn(name, grandparent_names)
    
    def test_get_grandchildren(self):
        bob = next((member for member in self.family if member.name == 'Bob Smith'), None)
        grandchildren = self.stats.get_grandchildren(bob)
        grandchild_names = [gc.name for gc in grandchildren]
        expected_grandchildren = ['Jake Smith', 'Laura Smith', 'Percy Smith', 'Janice Laceheart', 'Josh Kowalski']
        for name in expected_grandchildren:
            self.assertIn(name, grandchild_names)
    
    def test_get_cousins(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        cousins = self.stats.get_cousins(jake)
        cousin_names = [cousin.name for cousin in cousins]
        expected_cousins = ['Janice Laceheart', 'Josh Kowalski']
        for name in expected_cousins:
            self.assertIn(name, cousin_names)
    
    def test_get_immediate_family(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        immediate_family = self.stats.get_immediate_family(jake)
        immediate_family_names = [member.name for member in immediate_family]
        expected_immediate_family = ['Josh Smith', 'Lima Smith', 'Laura Smith', 'Percy Smith']
        for name in expected_immediate_family:
            self.assertIn(name, immediate_family_names)
    
    def test_display_extended(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_extended(jake)
            output = buf.getvalue()
        self.assertIn("Extended family of Jake Smith:", output)
        self.assertIn("- Bob Smith", output)
    
    def test_calc_avage(self):
        avg_age = self.stats.calc_avage()
        # Calculate expected average age
        today = datetime.today()
        total_age = 0
        count = 0
        for member in self.family:
            if member.is_alive and member.dob != 'na':
                try:
                    dob = datetime.strptime(member.dob, '%Y-%m-%d')
                    age = (today - dob).days / 365.25
                    total_age += age
                    count += 1
                except ValueError:
                    continue
        expected_avg_age = total_age / count if count > 0 else None
        if expected_avg_age:
            self.assertAlmostEqual(avg_age, expected_avg_age, places=1)
        else:
            self.assertIsNone(avg_age)
    
    def test_calc_davage(self):
        avg_death_age = self.stats.calc_davage()
        deceased_members = [member for member in self.family if not member.is_alive]
        self.assertEqual(len(deceased_members), 1)
        member = deceased_members[0]
        try:
            dob = datetime.strptime(member.dob, '%Y-%m-%d')
            death_date = datetime.strptime(member.death_date, '%Y-%m-%d')
            age_at_death = (death_date - dob).days / 365.25
            expected_avg_death_age = age_at_death
            self.assertAlmostEqual(avg_death_age, expected_avg_death_age, places=1)
        except ValueError:
            self.assertIsNone(avg_death_age)
    
    def test_get_id(self):
        person_id = self.stats.get_id('Josh Smith')
        self.assertEqual(person_id, 3)
        # Test ambiguous name 'Josh'
        with patch('builtins.input', side_effect=['1']):
            person_id = self.stats.get_id('Josh')
            self.assertEqual(person_id, 3)
        # Test non-existent name
        person_id = self.stats.get_id('Nonexistent Person')
        self.assertIsNone(person_id)
    
    def test_calc_acpp(self):
        total_children = 0
        for member in self.family:  # get the average child per person
            if isinstance(member, (ParentChild, Child)):
                if len(member.parents) > 0:
                    total_children += 1
        if total_children > 0:
            av = total_children / len(self.family)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.calc_acpp()
            output = buf.getvalue()
        self.assertIn(f"Average ACPP is: {str(round(av,2))}", output)
    
    def test_get_indiv_cc(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.get_indiv_cc()
            output = buf.getvalue()
        self.assertIn('Josh Smith : 3 children', output)
        self.assertIn('Bob Smith : 2 children', output)
        self.assertIn('Jake Smith : 0 children', output)
    
    def test_display_parents(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_parents(jake)
            output = buf.getvalue()
        self.assertIn('Parents of Jake Smith:', output)
        self.assertIn('- Josh Smith', output)
    
    def test_display_grandparents(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_grandparents(jake)
            output = buf.getvalue()
        self.assertIn('Grandparents of Jake Smith:', output)
        self.assertIn('- Bob Smith', output)
        self.assertIn('- Jenny Smith', output)
    
    def test_display_grandchildren(self):
        bob = next((member for member in self.family if member.name == 'Bob Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_grandchildren(bob)
            output = buf.getvalue()
        self.assertIn('Grandchildren of Bob Smith:', output)
        self.assertIn('- Jake Smith', output)
    
    def test_display_siblings(self):
        josh = next((member for member in self.family if member.name == 'Josh Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_siblings(josh)
            output = buf.getvalue()
        self.assertIn('Siblings of Josh Smith:', output)
        self.assertIn('- Alice Smith', output)
    
    def test_display_cousins(self):
        jake = next((member for member in self.family if member.name == 'Jake Smith'), None)
        with io.StringIO() as buf, redirect_stdout(buf):
            self.stats.display_cousins(jake)
            output = buf.getvalue()
        self.assertIn('Cousins of Jake Smith:', output)
        self.assertIn('- Janice Laceheart', output)

if __name__ == "__main__":
    unittest.main()
