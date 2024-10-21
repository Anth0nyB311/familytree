from turtle import window_height


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
finish = False
while(not finish):
    userOption = int(input("Your option:"))
    if userOption == 1 :
        import cli
        finish = True
    elif userOption == 2:
        import gui
        finish = True
    elif userOption == 3:
        exit()
        finish = True
    else:
        print("Sorry, I didn't understand the input.")