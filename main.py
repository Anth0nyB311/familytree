import subprocess, sys, os
import lib
from clear import clear

class mainProgram:
    def __init__(self):
        self.foundXmls = []
        self.lineages = []

    def mainMenu(self, selection):
        if selection > 0:
            importer = lib.ImExPorter()  
            self.lineages = importer.importProgress(self.foundXmls[selection - 1]) 
            finish = False
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
                userOption = int(input("Your option: "))
                if userOption == 1:
                    import cli
                    finish = True
                elif userOption == 2:
                    import gui
                    gui_app = gui.FamilyTreeGUI(self.lineages)
                    gui_app.main_gui()
                    finish = True
                elif userOption == 3:
                    exit()
                    finish = True
                else:
                    print("Sorry, I didn't understand the input.")
            except ValueError:
                print("Invalid input. Please enter a numerical value.")



    def loadSaves(self, saves):
        isDone = False
        while not isDone:
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
                isDone = True
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
    program = mainProgram()
    sys.exit(int(program.main() or 0))
