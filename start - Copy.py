import clear
import os
from main import FamilyTree
class main_prog:
    def __init__(self):
        self.save_files =[]
    def chk_lib(self):
        missing = []
        try:
            import curses
        except ImportError:
            missing.append("windows-curses")
        try:
            import yaml
        except ImportError:
            missing.append("pyyaml")
        if not missing:
            print("Libraries already present...")
            clear.clear()
            return True
        else:
            for lib in missing:
                print(f"{lib} library is missing. Please install it in order for this program to work! Do this --> \n\n1)Make sure you are running the latest version of python.\n2)Open a new privileged CMD and type:\npip install {lib}\n3)Re-open this program.\n\n\n")
        return False
    
    def loadSaves(self, saves):
        is_done = False
        while not is_done:
            clear.clear()
            print("=" * 50)
            print()
            print("We found your previous saves, please select one:")
            print()
            print(" 0: Do not load a save")
            for i in range(len(saves)):
                print(f" {i+1}: {saves[i].replace('family_tree_', '')}")
            print()
            print("=" * 50)
        
            option = input("Enter your choice: ")
        
            if option.isdigit() and 0 <= int(option) <= len(saves):
                option = int(option)
                is_done = True
            else:
                print("Sorry, I didn't understand the input.")

        return option
    
    def mainMenu(self, selection):
        finish = False
        saves = "na"
        if selection > 0:
            saves = self.save_files[selection-1]
        while not finish:
            clear.clear()
            print("=" * 45)
            print()
            print("Welcome to the Family Tree Program!")
            print()
            print("https://github.com/Anth0nyB311/familytree")
            print()
            print("Please select the version you wish to run:")
            print("1) Command Line Interface Mode")
            print("2) Graphical User Interface Mode")
            print("3) Exit program")
            print()
            print("=" * 45)
            try:
                user_option = int(input("Your option: "))
                if user_option == 1:
                    program = FamilyTree(saves)
                    program.main()
                    finish = True
                elif user_option == 2:
                    # Anthony, place your code here
                    finish = True
                elif user_option == 3:
                    finish = True
                    exit()
                else:
                    print("Sorry, I didn't understand the input.")
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

    def main(self):
        print("There is a bug with PyCharm and VS22 where the clear command does not work. We recommend you DO NOT run this program on the debug console but instead with cmd.exe")
        print()
        print("Press enter to dismiss...")
        input()
        clear.clear()
        if not self.chk_lib():
            exit()
        cur_dir = os.getcwd()
        save_selection = 0
        for file_name in os.listdir(cur_dir):
            if file_name.startswith("family_tree_") and file_name.endswith(".yaml"):
                self.save_files.append(file_name)
        if len(self.save_files) > 0:
            save_selection = self.loadSaves(self.save_files)
        clear.clear()
        self.mainMenu(save_selection)
        

if __name__ == "__main__":
        prog = main_prog()
        prog.main()
