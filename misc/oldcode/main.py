import subprocess, sys, os
import lib
from clear import clear

class main_program:
    def __init__(self):
        self.foundXmls = []
        self.lineages = []

    def mainMenu(self, selection):
        finish = False
        if selection > 0:
            importer = lib.ImExPorter()  
            self.lineages = importer.importProgress(self.foundXmls[selection - 1]) 
        while not finish:
            clear()
            print("=" * 45)
            print()
            print("Please note, you need to install tkcalendar.")
            print("Please do pip install tkcalendar to use GUI!")
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
                    import cli
                    finish = True
                elif user_option == 2:
                    import gui
                    gui_app = gui.FamilyTreeGUI(self.lineages)
                    gui_app.main_gui()
                    finish = True
                elif user_option == 3:
                    exit()
                    finish = True
                else:
                    print("Sorry, I didn't understand the input.")
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

                #test

    def loadSaves(self, saves):
        is_done = False
        while not is_done:
            clear()
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

    def main(self):
        print("NOTE: This program works as intended when not running via debugger. I recommend you launch this program using the old CMD.")
        input()
        clear()
        curDir = os.getcwd()
        saveSelection = 0
        for file_name in os.listdir(curDir):
            if file_name.startswith("family_tree_") and file_name.endswith(".xml"):
                self.foundXmls.append(file_name)
        if len(self.foundXmls) > 0:
            saveSelection = self.loadSaves(self.foundXmls)
        clear()
        self.mainMenu(saveSelection)

if __name__ == "__main__":
    program = main_program()
    sys.exit(int(program.main() or 0))
