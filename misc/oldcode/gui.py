from lib import Lineage, Person
import tkinter as tk
from tkinter import ttk, messagebox


class FamilyTreeGUI:
    def __init__(self, lineages):
        self.amountOfPeople = len(lineages)
        self.lineages = lineages
        self.root = None
        self.tree_canvas = None
        self.nodes = []

    def add_person(self, lineage, callback=None):
        popup = tk.Toplevel(self.root)
        popup.title("Add Family Member")
        tk.Label(popup, text="Family Member Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(popup, text="Family Member DOB (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        dob_entry = tk.Entry(popup)
        dob_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(popup, text="Are they alive? Yes/No:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        alive_entry = tk.Entry(popup)
        alive_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(popup, text="Family Member Ethnicity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ethnicity_entry = tk.Entry(popup)
        ethnicity_entry.grid(row=3, column=1, padx=10, pady=5)

        def save_person():
            name = name_entry.get()
            dob = dob_entry.get()
            alive = alive_entry.get()
            ethnicity = ethnicity_entry.get()

            if name and dob and alive and ethnicity:
                is_alive = alive.lower() in ["yes", "y"]
                person = Person(name, dob, is_alive, ethnicity)
                lineage._add_person(person)
                popup.destroy()
                if callback:
                    callback()
                self.draw_tree()
            else:
                messagebox.showwarning("Incomplete Data", "Please fill out all fields.")

        save_button = tk.Button(popup, text="Save Family Member", command=save_person)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def show_popup(self, lineage, times):
        if times > 0:
            self.add_person(lineage, lambda: self.show_popup(lineage, times - 1))

    def newMember(self):
        self.amountOfPeople += 1
        lin = Lineage()
        no_of_people = lin.get_noOfPeople(self.amountOfPeople)
        print(f"Amount of People: {self.amountOfPeople}, Number of People to Loop: {no_of_people}")

        self.show_popup(lin, no_of_people)
        self.lineages.append(lin)
        self.draw_tree()

    def removeMember(self):
        print('Deleter Mode button clicked')

    def _draw_node(self, person, x, y):
        node_radius = 40
        # Draw the node itself
        self.tree_canvas.create_oval(x - node_radius, y - 20, x + node_radius, y + 20, fill="white", outline="black")
        self.tree_canvas.create_text(x, y, text=person.name, font=("Arial", 12))
        # Store the node's data, including position and initial connection count
        self.nodes.append({'person': person, 'x': x, 'y': y, 'connections': 0})

    def draw_tree(self):
        self.tree_canvas.delete("all")
        self.nodes.clear()  # Clear the list of nodes before drawing again

        canvas_width = 800
        canvas_height = 600
        x_center = canvas_width // 2
        y_start = 100

        level_gap = 100
        x_gap = 150
        for idx, lineage in enumerate(self.lineages):
            num_people = len(lineage.persons)
            if num_people == 0:
                continue
            y_position = y_start + idx * level_gap
            start_x = x_center - ((num_people - 1) * x_gap) // 2

            for i, person in enumerate(lineage.persons):
                x_position = start_x + i * x_gap
                self._draw_node(person, x_position, y_position)

                # Find a suitable parent node to connect to
                for node in self.nodes:
                    if node['connections'] < 2:
                        # Draw a line from the parent node to the current node
                        self.tree_canvas.create_line(node['x'], node['y'], x_position, y_position, fill="black")
                        # Increment the number of connections for the parent node
                        node['connections'] += 1
                        break


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

        self.tree_canvas = tk.Canvas(
            main_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='black'
        )
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        scroll_x = tk.Scrollbar(main_frame, orient='horizontal', command=self.tree_canvas.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        scroll_y = tk.Scrollbar(main_frame, orient='vertical', command=self.tree_canvas.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        def on_frame_configure(event):
            self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all'))

        self.tree_canvas.bind('<Configure>', on_frame_configure)

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

        self.draw_tree()
        self.root.mainloop()


if __name__ == "__main__":
    app = FamilyTreeGUI([])
    app.main_gui()