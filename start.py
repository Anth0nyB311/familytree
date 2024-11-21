import os
import yaml
from main import FamilyTree
from family_lib import Parent, Child, Partner, ParentChild


class StartProgram:
    def __init__(self):
        self.saves = []  # Empty list for saved files

    def load_family_data(self, file_name):
        """Load the family data from the specified YAML file."""
        
        # Define the path to the 'Saves' folder
        save_folder = "C:/Users/ASUS/OneDrive - University of Greenwich/Computer Science Modules/reposo/Saves"
        
        # Construct the full path to the YAML file
        full_file_path = os.path.join(save_folder, file_name)

        if os.path.exists(full_file_path):
            with open(full_file_path, 'r') as file:
                return yaml.safe_load(file)  # Load the family data from the file
        else:
            print("Error: No file loaded")
            create_new = input("Would you like to create a new save? (y/n): ")
            if create_new.lower() == 'y':
                # Create a new save file if the user agrees
                self.create_new_save()
            return {"members": []}  # Return an empty family structure if file doesn't exist

    def save_family_data(self, file_name, data):
        """Save the family data to the specified YAML file."""
        with open(file_name, 'w') as file:
            yaml.dump(data, file)

    def mainMenu(self, save_selection):
     """Main menu where the user can choose between CLI and GUI modes."""
     if save_selection == -1:
        create_new_save = input("No saved family tree files found. Would you like to create a new save? (y/n): ")
        if create_new_save.lower() == "y":
            self.create_new_save()
            save_selection = 0  # After creating a new save, we set this to 0 to proceed
        else:
            print("Exiting program as no save is selected.")
            exit()

     # Check if save_selection is within bounds before accessing the saves list
     if save_selection < 0 or save_selection >= len(self.saves):
        print("Invalid save selection.")
        return  # Exit the method if the selection is invalid

     file_name = self.saves[save_selection]  # Use the self.saves list to get the file
     family_data = self.load_family_data(file_name)

     # Ensure family_data is a dictionary and contains "members"
     if isinstance(family_data, dict) and "members" in family_data:
        family_members = []
        if family_data["members"]:
            for member_data in family_data["members"]:  # Iterating over the "members" key
                role = member_data.pop("role", "Parent")  # Default role is "Parent"
                if role == "Parent":
                    person = Parent(**member_data)
                elif role == "Child":
                    person = Child(**member_data)
                elif role == "Partner":
                    person = Partner(**member_data)
                elif role == "ParentChild":
                    person = ParentChild(**member_data)
                else:
                    raise ValueError(f"Unknown role: {role}")
                family_members.append(person)
        else:
            print("Warning: No family members found in this save.")
            # Optionally, allow the user to add members or proceed with empty data
            add_members = input("Would you like to add family members? (y/n): ")
            if add_members.lower() == 'y':
                # You can implement the functionality to add new members here
                pass
     else:
        print("Invalid family data structure. Exiting...")
        print(family_data)  # Debugging to inspect the loaded family data

        return  # Exit the method if the structure is not as expected

     # Menu for CLI vs GUI selection
     finish = False
     while not finish:
        print("=" * 45)
        print("Welcome to the Family Tree Program!")
        print("Please select the version you wish to run:")
        print("1) Command Line Interface Mode")
        print("2) Graphical User Interface Mode")
        print("3) Exit program")
        print("=" * 45)

        try:
            user_option = int(input("Your option: "))
            if user_option == 1:
                # Running the CLI Mode
                program = FamilyTree(self.saves)  # Pass self.saves instead of saves
                program.main()
                finish = True
            elif user_option == 2:
                # Running the GUI Mode
                print("Launching the GUI...")
                gui_program = FamilyTreeGUI(family_members)
                gui_program.display_family()  # This should launch your Tkinter GUI window
                finish = True
            elif user_option == 3:
                finish = True
                exit()
            else:
                print("Sorry, I didn't understand the input.")
        except ValueError:
            print("Invalid input. Please enter a numerical value.")



    def create_new_save(self):
     """Create a new family save file with an empty family structure."""
     # Implement save creation logic, e.g., ask for a file name and save a blank family structure
     print("Creating a new save...")
     new_file_name = input("Enter the name for the new save file (without .yaml): ") + ".yaml"
     save_folder = "C:/Users/ASUS/OneDrive - University of Greenwich/Computer Science Modules/reposo/Saves"
     full_file_path = os.path.join(save_folder, new_file_name)

     # Ensure the new save file contains the correct structure
     data = {"members": []}  # Start with an empty family structure
     with open(full_file_path, 'w') as new_file:
        yaml.dump(data, new_file)  # Save the empty structure to the file

     print(f"New family tree save created: {full_file_path}")


    def main(self):
        """Main entry point for the program."""
        print("There is a bug with PyCharm and VS22 where the clear command does not work." 
              " We recommend you DO NOT run this program on the debug console but instead with cmd.exe")
        print("Press enter to dismiss...")
        input()

        # Get the current directory and search for family tree files
        cur_dir = os.path.join(os.getcwd(), "Saves")  # Make sure it points to the Saves folder
        print(f"Looking for files in: {cur_dir}")  # Debugging print
        save_selection = -1  # Set to -1 if no files are found
        
        # List all files in the Saves folder and check
        for file_name in os.listdir(cur_dir):
            print(f"Found file: {file_name}")  # Debugging print to see files in Saves folder
            if file_name.endswith(".yaml"):  # Ensure it ends with .yaml
                self.saves.append(file_name)
        
        if len(self.saves) > 0:
            save_selection = self.loadSaves(self.saves)
        else:
            print("No saved family tree files found.")
            create_new = input("Would you like to create a new save? (y/n): ")
            if create_new.lower() == 'y':
                # Create a new save file
                self.create_new_save()

        # Show the main menu for CLI/GUI selection
        self.mainMenu(save_selection)

    def loadSaves(self, saves):
        """Load the saved family tree files."""
        is_done = False
        while not is_done:
            print("=" * 50)
            print("We found your previous saves, please select one:")
            print(" 0: Do not load a save")
            for i in range(len(saves)):
                print(f" {i + 1}: {saves[i].replace('family_tree_', '')}")
            print("=" * 50)

            option = input("Enter your choice: ")

            if option.isdigit() and 0 <= int(option) <= len(saves):
                option = int(option) - 1  # Adjust option to match list index (starts from 0)
                is_done = True
            else:
                print("Sorry, I didn't understand the input.")

        return option


if __name__ == "__main__":
    prog = StartProgram()
    prog.main()
