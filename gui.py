import lib
import tkinter as tk
from tkinter import ttk, messagebox


class FamilyTreeGUI:
    def __init__(self, lineages):
        self.amountOfPeople = len(lineages)
        self.lineages = lineages
        self.root = None

    def add_person(self, lineage, callback=None):
        # Popup dialog to get person details from user
        popup = tk.Toplevel(self.root)
        popup.title("Add Family Member")

        # Person name entry
        tk.Label(popup, text="Family Member Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Person DOB entry
        tk.Label(popup, text="Family Member DOB (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        dob_entry = tk.Entry(popup)
        dob_entry.grid(row=1, column=1, padx=10, pady=5)

        # Alive status entry
        tk.Label(popup, text="Are they alive? Yes/No:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        alive_entry = tk.Entry(popup)
        alive_entry.grid(row=2, column=1, padx=10, pady=5)

        # Ethnicity entry
        tk.Label(popup, text="Family Member Ethnicity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ethnicity_entry = tk.Entry(popup)
        ethnicity_entry.grid(row=3, column=1, padx=10, pady=5)

        # Add button to save the person
        def save_person():
            name = name_entry.get()
            dob = dob_entry.get()
            alive = alive_entry.get()
            ethnicity = ethnicity_entry.get()

            if name and dob and alive and ethnicity:
                is_alive = alive.lower() in ["yes", "y"]
                person = lib.Person(name, dob, is_alive, ethnicity)
                lineage._add_person(person)
                popup.destroy()
                if callback:
                    callback()
            else:
                messagebox.showwarning("Incomplete Data", "Please fill out all fields.")

        save_button = tk.Button(popup, text="Save Family Member", command=save_person)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def show_popup(self, lineage, times):
        if times > 0:
            self.add_person(lineage, lambda: self.show_popup(lineage, times - 1))

    def newMember(self):
        self.amountOfPeople += 1
        lin = lib.Lineage()
        no_of_people = lin.get_noOfPeople(self.amountOfPeople)
        print(f"Amount of People: {self.amountOfPeople}, Number of People to Loop: {no_of_people}")

        self.show_popup(lin, no_of_people)
        self.lineages.append(lin)
        self.draw_tree()
        

    def removeMember(self):
        print('Deleter Mode button clicked')

    def draw_tree(self):
        # Clear the canvas and redraw the tree based on the current lineages
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        y_position = 20
        for lineage in self.lineages:
            for person in lineage.persons:
                person_label = tk.Label(self.tree_frame, text=f"Name: {person.name}, DOB: {person.dob}, Alive: {'Yes' if person.is_alive else 'No'}, Ethnicity: {person.ethnicity}")
                person_label.pack(anchor='w', pady=2)
                y_position += 20

    def main_gui(self):
        self.root = tk.Tk()
        self.root.geometry('890x590')
        self.root.configure(background='#F0F8FF')
        self.root.title('FamilyTree')

        main_frame = tk.Frame(self.root, bg='#F0F8FF')
        main_frame.pack(fill=tk.BOTH, expand=True)

        welcome_label = tk.Label(
            main_frame,
            text='Welcome to the Family Tree program!',
            bg='#F0F8FF',
            font=('Arial', 12)
        )
        welcome_label.pack(pady=10)

        tree_canvas = tk.Canvas(
            main_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='black'
        )
        tree_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        scroll_x = tk.Scrollbar(main_frame, orient='horizontal', command=tree_canvas.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        scroll_y = tk.Scrollbar(main_frame, orient='vertical', command=tree_canvas.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        self.tree_frame = tk.Frame(tree_canvas, bg='white')
        tree_canvas.create_window((0, 0), window=self.tree_frame, anchor='nw')

        def on_frame_configure(event):
            tree_canvas.configure(scrollregion=tree_canvas.bbox('all'))

        self.tree_frame.bind('<Configure>', on_frame_configure)

        button_frame = tk.Frame(main_frame, bg='#F0F8FF')
        button_frame.pack(pady=10)

        new_member_button = tk.Button(
            button_frame,
            text='Add a new member',
            bg='#A9A9A9',
            font=('Arial', 12),
            command=self.newMember
        )
        new_member_button.pack(side=tk.LEFT, padx=10)

        remove_member_button = tk.Button(
            button_frame,
            text='Deleter Mode',
            bg='#A9A9A9',
            font=('Arial', 12),
            command=self.removeMember
        )
        remove_member_button.pack(side=tk.LEFT, padx=10)

        self.root.mainloop()


if __name__ == "__main__":
    app = FamilyTreeGUI()
    app.main_gui()
