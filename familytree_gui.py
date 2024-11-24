"""Family Tree GUI Module."""
import sys
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import yaml_lib
from family_lib import Parent, Child, Partner
from main import FamilyTreeStatistics
from family_calendar import (
    generate_month_calendar,
    get_birthdays_in_month,
    format_birthday_line,
)


class FamilyTreeVisualizer:
    """Handles the visual representation of the family tree."""

    def __init__(self):
        """Initialize the visualizer with grid-based layout."""
        self.cell_width = 180
        self.cell_height = 100
        self.node_radius = 45
        self.base_font_size = 11  # Base font size for names
        self.base_date_font_size = 9  # Base font size for dates
        self.current_scale = 1.0  # Track current zoom level
        self.grid = {}
        self.positions = {}
        self.level_count = {}
        self.visited = set()
        self.margin = 20
        self.node_colors = {
            "bg": "#404040",
            "outline": "#606060",
            "text": "#ffffff",
            "secondary_text": "#cccccc",
        }

    def draw_tree(self, canvas, root_person):
        """Draw the family tree on the canvas.

        Args:
            canvas: tkinter Canvas to draw on
            root_person: Person object to use as tree root
        """
        if not root_person:
            return

        self._reset_state()
        self._create_tree_matrix(root_person, 0, 0)
        self._calculate_dimensions(canvas)
        self._draw_tree_elements(canvas, root_person)

    def _reset_state(self):
        """Reset the visualizer's state."""
        self.grid = {}
        self.positions = {}
        self.level_count = {}
        self.visited = set()

    def _create_tree_matrix(self, person, row, col):
        """Create tree matrix using depth-first traversal with adjusted spacing.

        Args:
            person: Person object to position
            row: Current row in grid
            col: Current column in grid

        Returns:
            int: Next available column position
        """
        if not person or person in self.visited:
            return col

        self.visited.add(person)
        start_col = col

        # Place current person
        while self._is_cell_occupied(row, start_col):
            start_col += 0.5
        self.grid[(row, start_col)] = person

        # Handle partners with increased spacing
        partner_end_col = start_col
        if hasattr(person, "partners"):
            partner_col = (
                start_col + 0.8
            )  # Increased from 0.4 for wider partner spacing
            for partner in person.partners:
                if partner not in self.visited:
                    while self._is_cell_occupied(row, partner_col):
                        partner_col += 0.8  # Increased partner increment
                    self.grid[(row, partner_col)] = partner
                    self.visited.add(partner)
                    partner_col += 0.8
            partner_end_col = partner_col

        # Handle children with tighter spacing
        if hasattr(person, "children") and person.children:
            child_row = row + 1
            num_children = len(person.children)

            # Calculate child positioning with reduced spacing
            parent_span = partner_end_col - start_col
            child_spacing = max(
                1, parent_span / (num_children + 1)
            )  # Reduced from 0.5 for closer siblings
            child_start = start_col - (child_spacing * (num_children - 1) / 2)

            child_col = child_start
            for child in person.children:
                if child not in self.visited:
                    next_col = self._create_tree_matrix(child, child_row, child_col)
                    child_col = next_col + child_spacing

        return max(partner_end_col, child_col if "child_col" in locals() else start_col)

    def _calculate_dimensions(self, canvas):
        """Calculate and set canvas dimensions."""
        if not self.grid:
            return

        # Find the extremes of the grid
        max_row = max(row for row, _ in self.grid.keys())
        max_col = max(col for _, col in self.grid.keys())
        min_col = min(col for _, col in self.grid.keys())

        self._calculate_canvas_positions()
        canvas.delete("all")

        # Calculate dimensions with extra padding
        padding = 1000  # Increased padding for better visibility
        canvas_width = (max_col - min_col + 4) * self.cell_width + padding
        canvas_height = (max_row + 4) * self.cell_height + padding

        # Set scrollable region with extra space on all sides
        scroll_left = -padding / 2
        scroll_top = -padding / 2
        scroll_right = canvas_width + padding / 2
        scroll_bottom = canvas_height + padding / 2

        canvas.configure(
            scrollregion=(scroll_left, scroll_top, scroll_right, scroll_bottom)
        )

    def _draw_tree_elements(self, canvas, root_person):
        """Draw all tree elements.

        Args:
            canvas: tkinter Canvas to draw on
            root_person: Person object to use as tree root
        """
        self._draw_all_connections(canvas, root_person)
        self._draw_all_nodes(canvas)

    def _draw_all_nodes(self, canvas):
        """Draw all nodes in the tree."""
        for person, (x, y) in self.positions.items():
            self._draw_node(canvas, person, x, y)

    def _draw_all_connections(self, canvas, root_person):
        """Draw all family connections."""
        drawn_connections = set()

        def draw_connections(person):
            """Recursive helper to draw connections.

            Args:
                person: Person object to draw connections for
            """
            if person in drawn_connections:
                return

            drawn_connections.add(person)
            if person not in self.positions:
                return

            x, y = self.positions[person]

            # Draw partner connections
            if hasattr(person, "partners"):
                for partner in person.partners:
                    if (
                        partner in self.positions
                        and (partner, person) not in drawn_connections
                    ):
                        px, py = self.positions[partner]
                        canvas.create_line(
                            x + self.node_radius,
                            y,
                            px - self.node_radius,
                            py,
                            fill="#E74C3C",  # Red for partner connections
                            width=2,
                            dash=(4, 2),
                        )
                        drawn_connections.add((person, partner))
                        drawn_connections.add((partner, person))

            # Draw child connections
            if hasattr(person, "children"):
                for child in person.children:
                    if child in self.positions:
                        cx, cy = self.positions[child]
                        canvas.create_line(
                            x,
                            y + self.node_radius,
                            cx,
                            cy - self.node_radius,
                            fill="#27AE60",  # Green for child connections
                            width=2,
                            smooth=True,
                        )
                        draw_connections(child)

        draw_connections(root_person)

    def _is_cell_occupied(self, row, col):
        """Check if a grid cell is already occupied, with adjusted spacing checks.

        Args:
            row: Grid row to check
            col: Grid column to check (can be fractional)

        Returns:
            bool: True if cell is occupied or too close to occupied cell
        """
        if (row, col) in self.grid:
            return True

        # Check nearby positions with reduced minimum distance for siblings
        for existing_row, existing_col in self.grid.keys():
            if (
                existing_row == row and abs(existing_col - col) < 0.25
            ):  # Reduced from 0.3
                return True
        return False

    def _calculate_canvas_positions(self):
        """Convert grid positions to canvas coordinates."""
        margin = 50
        for (row, col), person in self.grid.items():
            x = margin + (col * self.cell_width) + (self.cell_width // 2)
            y = margin + (row * self.cell_height) + (self.cell_height // 2)
            self.positions[person] = (x, y)

    def _draw_node(self, canvas, person, x, y):
        """Draw a single person node with scaled text size."""
        # Draw background circle
        canvas.create_oval(
            x - self.node_radius,
            y - self.node_radius,
            x + self.node_radius,
            y + self.node_radius,
            fill=self.node_colors["bg"],
            outline=self.node_colors["outline"],
            width=2,
        )

        # Calculate scaled font sizes
        name_font_size = max(8, int(self.base_font_size * self.current_scale))
        date_font_size = max(6, int(self.base_date_font_size * self.current_scale))

        # Draw person's name with scaled font
        canvas.create_text(
            x,
            y - 12 * self.current_scale,
            text=person.name,
            font=("Arial", name_font_size, "bold"),
            fill=self.node_colors["text"],
            anchor="center",
            width=self.node_radius * 1.8,
        )

        # Draw birth/death years with scaled font
        birth_year = person.dob.split("-")[0] if hasattr(person, "dob") else "?"
        death_year = (
            "†" + person.death_date.split("-")[0]
            if hasattr(person, "death_date") and person.death_date
            else ""
        )
        date_text = f"{birth_year}{' ' + death_year if death_year else ''}"

        canvas.create_text(
            x,
            y + 12 * self.current_scale,
            text=date_text,
            font=("Arial", date_font_size),
            fill=self.node_colors["secondary_text"],
            anchor="center",
        )


class FamilyTreeGUI:
    def __init__(self, save_file=None):
        """init the class"""
        self.root = None
        self.tree_canvas = None
        self.family_listbox = None
        self.tree_visualizer = None
        self.selected_person = None
        self.family = []
        self.stats = None
        self.zoom_scale = 1.0
        self.save_file = save_file
        if save_file:
            self.family = yaml_lib.yaml_import(save_file)
            self.stats = FamilyTreeStatistics(self.family)
        self.themes = {
            "Dark": {
                "bg": "#2b2b2b",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
                "button_active": "#505050",
                "button_pressed": "#303030",
                "text": "#ffffff",
                "secondary_text": "#cccccc",
                "listbox_bg": "#404040",
                "listbox_fg": "#ffffff",
                "listbox_select_bg": "#606060",
                "node_bg": "#404040",
                "node_outline": "#606060",
            },
            "Light": {
                "bg": "#ffffff",
                "button_bg": "#e0e0e0",
                "button_fg": "#000000",
                "button_active": "#d0d0d0",
                "button_pressed": "#c0c0c0",
                "text": "#000000",
                "secondary_text": "#666666",
                "listbox_bg": "#ffffff",
                "listbox_fg": "#000000",
                "listbox_select_bg": "#0078d7",
                "node_bg": "#ffffff",
                "node_outline": "#000000",
            },
            "Neon": {
                "bg": "#000000",
                "button_bg": "#000000",
                "button_fg": "#00ffff",
                "button_active": "#001f1f",
                "button_pressed": "#003f3f",
                "text": "#00ffff",
                "secondary_text": "#0088ff",
                "listbox_bg": "#000000",
                "listbox_fg": "#00ffff",
                "listbox_select_bg": "#003f3f",
                "node_bg": "#000000",
                "node_outline": "#00ffff",
            },
        }
        self.current_theme = "Dark"

    def display_family(self):
        """function to show the family on the canvas"""
        self.root = tk.Tk()
        self.root.title("Family Tree Manager")
        self.root.geometry("1400x800")

        # Bind window close button to exit_program
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)

        # Configure dark theme colors
        self.root.configure(bg="#2b2b2b")
        style = ttk.Style()

        # Create custom theme
        style.theme_create(
            "darktheme",
            parent="alt",
            settings={
                "TFrame": {"configure": {"background": "#2b2b2b"}},
                "TLabel": {
                    "configure": {"background": "#2b2b2b", "foreground": "#ffffff"}
                },
                "TButton": {
                    "configure": {
                        "background": "#404040",
                        "foreground": "#ffffff",
                        "padding": [10, 5],
                        "relief": "raised",
                    },
                    "map": {
                        "background": [
                            ("active", "#505050"),
                            ("pressed", "#303030"),
                            ("!disabled", "#404040"),
                        ],
                        "foreground": [("!disabled", "#ffffff")],
                    },
                },
            },
        )

        # Use the custom theme
        style.theme_use("darktheme")

        # Configure other widgets
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="#ffffff",
            fieldbackground="#2b2b2b",
        )

        # Configure dark theme for listbox and canvas
        self.root.option_add("*TCombobox*Listbox.background", "#404040")
        self.root.option_add("*TCombobox*Listbox.foreground", "#ffffff")

        self.tree_visualizer = FamilyTreeVisualizer()

        # Create main frames
        left_frame = ttk.Frame(self.root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add components to frames
        self._create_left_frame_content(left_frame)
        self._create_right_frame_content(right_frame)

        # Initialize the family list
        self.refresh_family_list()

        self.root.mainloop()

    def _create_left_frame_content(self, frame):
        """Create the left frame content."""
        # Create a canvas and scrollbar for the left frame
        canvas = tk.Canvas(
            frame, bg=self.themes[self.current_theme]["bg"], highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)

        # Create a frame inside the canvas to hold all content
        content_frame = ttk.Frame(canvas)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add the content frame to the canvas
        canvas_frame = canvas.create_window(
            (0, 0), window=content_frame, anchor="nw", width=canvas.winfo_width()
        )

        # File operations section
        ttk.Label(
            content_frame, text="File Operations", font=("Arial", 10, "bold")
        ).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(content_frame, text="New Family Tree", command=self.new_family).pack(
            fill=tk.X
        )
        ttk.Button(
            content_frame, text="Load Family Tree", command=self.load_family
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame, text="Save Family Tree", command=self.save_family
        ).pack(fill=tk.X)

        # Zoom controls section
        ttk.Label(content_frame, text="Zoom Controls", font=("Arial", 10, "bold")).pack(
            fill=tk.X, pady=(10, 5)
        )
        zoom_frame = ttk.Frame(content_frame)
        zoom_frame.pack(fill=tk.X, pady=2)
        ttk.Button(
            zoom_frame, text="Zoom In (+)", command=lambda: self._canvas_zoom(1.2)
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(
            zoom_frame, text="Zoom Out (-)", command=lambda: self._canvas_zoom(0.8)
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Family list section
        ttk.Label(
            content_frame, text="Family Members", font=("Arial", 10, "bold")
        ).pack(fill=tk.X, pady=(10, 5))
        self.family_listbox = tk.Listbox(
            content_frame,
            height=8,
            bg="#404040",
            fg="#ffffff",
            selectbackground="#606060",
            selectforeground="#ffffff",
        )
        self.family_listbox.pack(fill=tk.X)
        self.family_listbox.bind("<<ListboxSelect>>", self.on_select_person)

        # Person management section
        ttk.Label(
            content_frame, text="Person Management", font=("Arial", 10, "bold")
        ).pack(fill=tk.X, pady=(10, 5))
        ttk.Button(
            content_frame, text="Add Person", command=self.add_person_dialog
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame, text="Add Relationship", command=self.add_relationship_dialog
        ).pack(fill=tk.X)

        # Relationship viewing section
        ttk.Label(
            content_frame, text="View Relationships", font=("Arial", 10, "bold")
        ).pack(fill=tk.X, pady=(10, 5))
        ttk.Button(
            content_frame,
            text="Show Parents",
            command=lambda: self.show_relationships(self.selected_person, "Parents"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Grandparents",
            command=lambda: self.show_relationships(
                self.selected_person, "Grandparents"
            ),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Siblings",
            command=lambda: self.show_relationships(self.selected_person, "Siblings"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Children",
            command=lambda: self.show_relationships(self.selected_person, "Children"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Grandchildren",
            command=lambda: self.show_relationships(
                self.selected_person, "Grandchildren"
            ),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Immediate Family",
            command=lambda: self.show_relationships(
                self.selected_person, "Immediate Family"
            ),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Show Extended Family",
            command=lambda: self.show_relationships(
                self.selected_person, "Extended Family"
            ),
        ).pack(fill=tk.X)

        # Statistics section
        ttk.Label(content_frame, text="Statistics", font=("Arial", 10, "bold")).pack(
            fill=tk.X, pady=(10, 5)
        )
        ttk.Button(
            content_frame,
            text="Average Age",
            command=lambda: self.show_statistics("Average Age"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Death Age",
            command=lambda: self.show_statistics("Death Age"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Children Count",
            command=lambda: self.show_statistics("Children Count"),
        ).pack(fill=tk.X)
        ttk.Button(
            content_frame,
            text="Average Children",
            command=lambda: self.show_statistics("Average Children"),
        ).pack(fill=tk.X)

        # Add Calendar section before Exit button
        ttk.Label(content_frame, text="Calendar", font=("Arial", 10, "bold")).pack(
            fill=tk.X, pady=(10, 5)
        )
        ttk.Button(
            content_frame, text="Show Family Calendar", command=self.show_calendar
        ).pack(fill=tk.X)

        # Exit button
        ttk.Button(content_frame, text="Exit", command=self.exit_program).pack(
            fill=tk.X, pady=(10, 0)
        )

        # Update scroll region when content size changes
        def _configure_canvas(event):
            """allows canvas configuration"""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the canvas window
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())

        content_frame.bind("<Configure>", _configure_canvas)

        # Update mousewheel binding
        def _on_mousewheel(event):
            """when wheel mouse scrolls"""
            widget = event.widget
            if widget == canvas:  # Only scroll if mouse is over the canvas
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind mousewheel only when mouse enters/leaves the canvas
        canvas.bind(
            "<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel)
        )
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Bind frame resizing
        def _on_frame_configure(event):
            canvas.configure(width=frame.winfo_width() - scrollbar.winfo_width())

        frame.bind("<Configure>", _on_frame_configure)

        # Add theme selector at the top
        self.theme_label = ttk.Label(
            content_frame, text="Theme", font=("Arial", 10, "bold")
        )
        self.theme_label.pack(fill=tk.X, pady=(0, 5))
        self.theme_frame = ttk.Frame(content_frame)
        self.theme_frame.pack(fill=tk.X, pady=2)
        for theme in self.themes.keys():
            ttk.Button(
                self.theme_frame,
                text=theme,
                command=lambda t=theme: self.apply_theme(t),
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def _create_right_frame_content(self, frame):
        """makes the right frame"""
        canvas_container = ttk.Frame(frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        self.tree_canvas = tk.Canvas(
            canvas_container, bg="#2b2b2b", highlightthickness=0
        )
        v_scrollbar = ttk.Scrollbar(
            canvas_container, orient="vertical", command=self.tree_canvas.yview
        )
        h_scrollbar = ttk.Scrollbar(
            canvas_container, orient="horizontal", command=self.tree_canvas.xview
        )

        self.tree_canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        self.tree_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Update mousewheel bindings for tree canvas
        def _on_mousewheel_y(event):
            self.tree_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_x(event):
            if event.state & 0x1:  # Check if Shift is pressed
                self.tree_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                self.tree_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind mousewheel only when mouse enters/leaves the tree canvas
        self.tree_canvas.bind(
            "<Enter>",
            lambda e: self.tree_canvas.bind_all("<MouseWheel>", _on_mousewheel_x),
        )
        self.tree_canvas.bind(
            "<Leave>", lambda e: self.tree_canvas.unbind_all("<MouseWheel>")
        )

        # Remove the old bindings
        # self.tree_canvas.bind('<MouseWheel>', self._on_mousewheel_y)
        # self.tree_canvas.bind('<Shift-MouseWheel>', self._on_mousewheel_x)

    def on_select_person(self, event):
        """when a person is selected"""
        selection = self.family_listbox.curselection()
        if selection:
            try:
                index = selection[0]
                self.selected_person = self.family[index]
                self.tree_visualizer.draw_tree(self.tree_canvas, self.selected_person)
            except Exception as e:
                print(f"Debug - Selection error: {str(e)}")
                self.selected_person = None

    def add_person_dialog(self):
        """adds a person dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Person")

        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Person type selection
        ttk.Label(form_frame, text="Person Type:").pack(fill=tk.X)
        person_type = tk.StringVar(value="Parent")
        ttk.Radiobutton(
            form_frame, text="Parent", variable=person_type, value="Parent"
        ).pack()
        ttk.Radiobutton(
            form_frame, text="Child", variable=person_type, value="Child"
        ).pack()
        ttk.Radiobutton(
            form_frame, text="Partner", variable=person_type, value="Partner"
        ).pack()

        # Name entry
        ttk.Label(form_frame, text="Name:").pack(fill=tk.X)
        name_entry = ttk.Entry(form_frame)
        name_entry.pack(fill=tk.X)

        # Ethnicity entry
        ttk.Label(form_frame, text="Ethnicity:").pack(fill=tk.X)
        ethnicity_entry = ttk.Entry(form_frame)
        ethnicity_entry.pack(fill=tk.X)

        # Date of birth
        ttk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):").pack(fill=tk.X)
        dob_entry = ttk.Entry(form_frame)
        dob_entry.pack(fill=tk.X)

        # Living status
        is_alive_var = tk.BooleanVar(value=True)
        death_entry = ttk.Entry(form_frame)

        def toggle_death_date():
            """allow for death date"""
            if is_alive_var.get():
                death_entry.configure(state="disabled")
                death_entry.delete(0, tk.END)
            else:
                death_entry.configure(state="normal")

        alive_check = ttk.Checkbutton(
            form_frame,
            text="Is Alive",
            variable=is_alive_var,
            command=toggle_death_date,
        )
        alive_check.pack(fill=tk.X)

        # Death date
        ttk.Label(form_frame, text="Date of Death (YYYY-MM-DD):").pack(fill=tk.X)
        death_entry.pack(fill=tk.X)
        death_entry.configure(state="disabled")

        def validate_and_submit():
            """make sure the input is correct"""
            try:
                name = name_entry.get().strip()
                if not name:
                    raise ValueError("Name is required")
                ethnicity = ethnicity_entry.get().strip()
                if not ethnicity:
                    raise ValueError("Ethnicity is required")
                person_class = {"Parent": Parent, "Child": Child, "Partner": Partner}[
                    person_type.get()
                ]
                dob = dob_entry.get().strip() or None

                # Create person first
                new_person = person_class(
                    name=name, dob=dob, is_alive=is_alive_var.get(), ethnicity=ethnicity
                )

                # Set death date after creation if person is not alive
                if not is_alive_var.get():
                    death_date = death_entry.get().strip()
                    if death_date:
                        new_person.death_date = death_date

                self.family.append(new_person)
                dialog.destroy()
                self.refresh_family_list()
                messagebox.showinfo(
                    "Success", f"Added {person_type.get()} {name} to family tree!"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add person: {str(e)}")

        ttk.Button(form_frame, text="Add Person", command=validate_and_submit).pack(
            pady=10
        )
        ttk.Button(form_frame, text="Cancel", command=dialog.destroy).pack()

    def add_relationship_dialog(self):
        """add a relationship"""
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Relationship")

        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            form_frame, text=f"Add relationship for: {self.selected_person.name}"
        ).pack(fill=tk.X)

        # Relationship type selection
        ttk.Label(form_frame, text="Relationship Type:").pack(fill=tk.X)
        rel_type = tk.StringVar(value="Parent")
        ttk.Radiobutton(
            form_frame, text="Parent", variable=rel_type, value="Parent"
        ).pack()
        ttk.Radiobutton(
            form_frame, text="Child", variable=rel_type, value="Child"
        ).pack()
        ttk.Radiobutton(
            form_frame, text="Partner", variable=rel_type, value="Partner"
        ).pack()

        # Related person selection
        ttk.Label(form_frame, text="Related Person:").pack(fill=tk.X)
        related_person = tk.StringVar()
        person_list = ttk.Combobox(form_frame, textvariable=related_person)
        person_list["values"] = [
            person.name for person in self.family if person != self.selected_person
        ]
        person_list.pack(fill=tk.X)

        def add_relationship():
            """inner func to add a person"""
            try:
                if not related_person.get():
                    raise ValueError("Please select a related person")

                related = next(p for p in self.family if p.name == related_person.get())
                relationship_type = rel_type.get()

                if relationship_type == "Parent":
                    self.selected_person.add_parent(related)
                elif relationship_type == "Child":
                    self.selected_person.add_child(related)
                elif relationship_type == "Partner":
                    self.selected_person.add_partner(related)

                dialog.destroy()
                self.refresh_family_list()
                messagebox.showinfo("Success", "Relationship added successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add relationship: {str(e)}")

        ttk.Button(form_frame, text="Add Relationship", command=add_relationship).pack(
            pady=10
        )
        ttk.Button(form_frame, text="Cancel", command=dialog.destroy).pack()

    def show_relationships(self, person, relationship_type):
        """shows a persons relationship type"""
        if not person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        try:
            message = f"{relationship_type} of {person.name}:\n\n"

            if relationship_type == "Parents":
                relatives = person.parents
            elif relationship_type == "Grandparents":
                relatives = self.stats.get_grandparents(person)
            elif relationship_type == "Children":
                relatives = person.children if hasattr(person, "children") else []
            elif relationship_type == "Grandchildren":
                relatives = self.stats.get_grandchildren(person)
            elif relationship_type == "Siblings":
                # Get siblings through shared parents
                siblings = set()
                if hasattr(person, "parents"):
                    for parent in person.parents:
                        for child in parent.children:
                            if child != person:  # Don't include self
                                siblings.add(child)
                relatives = list(siblings)
            elif relationship_type == "Immediate Family":
                relatives = list(self.stats.get_immediate_family(person))
            elif relationship_type == "Extended Family":
                # Get all extended family members using stats methods
                extended_family = set()
                extended_family.update(self.stats.get_grandparents(person))
                extended_family.update(self.stats.get_grandchildren(person))
                extended_family.update(self.stats.get_aunts_uncles(person))
                extended_family.update(self.stats.get_nieces_nephews(person))
                extended_family.update(self.stats.get_cousins(person))
                relatives = list(extended_family)
            else:
                relatives = []

            if relatives:
                for relative in relatives:
                    message += f"- {relative.name}\n"
            else:
                message += "None found"

            messagebox.showinfo(relationship_type, message)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get relationships: {str(e)}")

    def show_statistics(self, stat_type):
        """display any stats needed"""
        try:
            if stat_type == "Children Count":
                message = "Individual Child Count:\n\n"
                for person in self.family:
                    if hasattr(person, "children") and person.children:
                        child_count = len(person.children)
                        message += f'{person.name} : {child_count} child{"ren" if child_count > 1 else ""}.\n'
                    else:
                        message += f"{person.name} : 0 children\n"
                messagebox.showinfo("Children Count", message)

            elif stat_type == "Average Age":
                avg_age = self.stats.calc_avage()
                if avg_age is not None:
                    messagebox.showinfo(
                        "Statistics", f"Average age: {avg_age:.1f} years"
                    )
                else:
                    messagebox.showinfo("Statistics", "No age data available")

            elif stat_type == "Death Age":
                avg_death_age = self.stats.calc_davage()
                if avg_death_age is not None:
                    messagebox.showinfo(
                        "Statistics", f"Average age at death: {avg_death_age:.1f} years"
                    )
                else:
                    messagebox.showinfo("Statistics", "No death age data available")

            elif stat_type == "Average Children":
                # Use a set to avoid counting children multiple times
                unique_children = set()
                for person in self.family:
                    if hasattr(person, "children"):
                        unique_children.update(person.children)

                total_children = len(unique_children)
                total_people = len(self.family)

                if total_people > 0:
                    avg = total_children / total_people
                    messagebox.showinfo(
                        "Statistics",
                        f"Average children per person: {avg:.2f}\n"
                        f"Total unique children: {total_children}\n"
                        f"Total people: {total_people}",
                    )
                else:
                    messagebox.showinfo(
                        "Statistics", "No people found in the family tree"
                    )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate {stat_type}: {str(e)}")

    def save_family(self):
        """save the family to the yaml"""
        try:
            yaml_lib.yaml_export(self.family)
            messagebox.showinfo("Success", "Family tree saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save family tree: {str(e)}")

    def load_family(self):
        """load family from save file"""
        try:
            # Open file dialog for selecting a YAML file
            file_path = filedialog.askopenfilename(
                initialdir="saves",
                title="Select Family Tree File",
                filetypes=[("YAML files", "*.yaml")],
            )

            # Only proceed if user selected a file
            if file_path:
                self.family = yaml_lib.yaml_import(file_path)
                self.stats = FamilyTreeStatistics(self.family)
                self.refresh_family_list()
                messagebox.showinfo("Success", "Family tree loaded successfully!")
            else:
                return  # User cancelled file selection

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load family tree: {str(e)}")

    def new_family(self):
        """create a new family"""
        if messagebox.askyesno(
            "New Family Tree",
            "Are you sure you want to create a new family tree? Any unsaved changes will be lost.",
        ):
            self.family = []
            self.stats = FamilyTreeStatistics(self.family)
            self.refresh_family_list()
            messagebox.showinfo("Success", "New family tree created!")

    def refresh_family_list(self):
        """clear current family"""
        """Refresh the family list display, sorted by date of birth."""
        self.family_listbox.delete(0, tk.END)

        # Sort family by date of birth
        sorted_family = sorted(
            self.family,
            key=lambda person: person.dob if hasattr(person, "dob") else "9999-99-99",
        )

        # Update the family list to maintain the sorted order
        self.family = sorted_family

        # Display sorted list
        for person in self.family:
            # Display birth date alongside name if available
            display_text = f"{person.name}"
            if hasattr(person, "dob") and person.dob:
                display_text += f" ({person.dob})"
            self.family_listbox.insert(tk.END, display_text)

        # Select first person and display their tree
        if self.family:
            self.family_listbox.select_set(0)
            self.selected_person = self.family[0]
            self.tree_visualizer.draw_tree(self.tree_canvas, self.selected_person)

    def exit_program(self):
        """Handle program exit with save confirmation."""
        response = messagebox.askyesnocancel(
            "Exit",
            "Would you like to save your family tree before exiting?",
            icon="warning",
        )

        if response is None:  # Cancel was clicked
            return
        elif response:  # Yes was clicked
            try:
                yaml_lib.yaml_export(self.family)
                messagebox.showinfo("Success", "Family tree saved successfully!")
                self.root.quit()
            except Exception as e:
                error_response = messagebox.askyesno(
                    "Error",
                    f"Failed to save family tree: {str(e)}\n\nExit anyway?",
                    icon="error",
                )
                if error_response:
                    self.root.quit()
        else:  # No was clicked
            self.root.quit()

    def _on_mousewheel_y(self, event):
        """when the mouse moves on the y axis"""
        self.tree_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_x(self, event):
        """when the mouse moves on the x axis"""
        self.tree_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _canvas_zoom(self, factor):
        """Apply zoom while maintaining center."""
        if not self.selected_person:
            return

        # Store current view center
        canvas_width = self.tree_canvas.winfo_width()
        canvas_height = self.tree_canvas.winfo_height()
        scroll_x = self.tree_canvas.xview()
        scroll_y = self.tree_canvas.yview()
        center_x = (scroll_x[0] + scroll_x[1]) / 2
        center_y = (scroll_y[0] + scroll_y[1]) / 2

        # Update visualizer dimensions
        self.tree_visualizer.cell_width = int(self.tree_visualizer.cell_width * factor)
        self.tree_visualizer.cell_height = int(
            self.tree_visualizer.cell_height * factor
        )
        self.tree_visualizer.node_radius = int(
            self.tree_visualizer.node_radius * factor
        )
        self.tree_visualizer.current_scale *= factor

        # Redraw tree
        self.tree_visualizer.draw_tree(self.tree_canvas, self.selected_person)

        # Restore view center
        self.tree_canvas.update_idletasks()
        self.tree_canvas.xview_moveto(
            center_x - (canvas_width / (2 * self.tree_canvas.winfo_width()))
        )
        self.tree_canvas.yview_moveto(
            center_y - (canvas_height / (2 * self.tree_canvas.winfo_height()))
        )

    def apply_theme(self, theme_name):
        """allow the user to choose a custom theme"""
        # Hide theme selection UI
        self.theme_label.pack_forget()
        self.theme_frame.pack_forget()

        theme = self.themes[theme_name]
        self.current_theme = theme_name

        # Configure root and style
        self.root.configure(bg=theme["bg"])
        style = ttk.Style()

        # Create/update theme
        style.theme_create(
            "customtheme",
            parent="alt",
            settings={
                "TFrame": {"configure": {"background": theme["bg"]}},
                "TLabel": {
                    "configure": {
                        "background": theme["bg"],
                        "foreground": theme["text"],
                    }
                },
                "TButton": {
                    "configure": {
                        "background": theme["button_bg"],
                        "foreground": theme["button_fg"],
                        "padding": [10, 5],
                        "relief": "raised",
                    },
                    "map": {
                        "background": [
                            ("active", theme["button_active"]),
                            ("pressed", theme["button_pressed"]),
                            ("!disabled", theme["button_bg"]),
                        ],
                        "foreground": [("!disabled", theme["button_fg"])],
                    },
                },
            },
        )

        style.theme_use("customtheme")

        # Update listbox colors
        if hasattr(self, "family_listbox"):
            self.family_listbox.configure(
                bg=theme["listbox_bg"],
                fg=theme["listbox_fg"],
                selectbackground=theme["listbox_select_bg"],
                selectforeground=theme["button_fg"],
            )

        # Update canvas colors
        if hasattr(self, "tree_canvas"):
            self.tree_canvas.configure(bg=theme["bg"])

        # Update tree visualizer colors if it exists
        if hasattr(self, "tree_visualizer"):
            self.tree_visualizer.node_colors = {
                "bg": theme["node_bg"],
                "outline": theme["node_outline"],
                "text": theme["text"],
                "secondary_text": theme["secondary_text"],
            }
            # Redraw tree if there's a selected person
            if self.selected_person:
                self.tree_visualizer.draw_tree(self.tree_canvas, self.selected_person)

    def show_calendar(self):
        """Display the family calendar in a new window."""
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Family Calendar")
        calendar_window.geometry("800x600")

        # Configure calendar window with current theme
        calendar_window.configure(bg=self.themes[self.current_theme]["bg"])

        # Create main frame for calendar
        cal_frame = ttk.Frame(calendar_window, padding="10")
        cal_frame.pack(fill=tk.BOTH, expand=True)

        # Calendar display area
        calendar_text = tk.Text(
            cal_frame,
            wrap=tk.WORD,
            bg=self.themes[self.current_theme]["bg"],
            fg=self.themes[self.current_theme]["text"],
            font=("Courier", 10),
            height=30,
            width=80,
        )
        calendar_text.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            cal_frame, orient=tk.VERTICAL, command=calendar_text.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        calendar_text.configure(yscrollcommand=scrollbar.set)

        # Navigation frame
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        current_month = datetime.now().month
        current_year = datetime.now().year

        def update_calendar(month, year):
            """show new text when a person clicks a button"""
            calendar_text.delete(1.0, tk.END)
            important_dates = []

            # Convert family members to the format expected by calendar functions
            for person in self.family:
                if hasattr(person, "dob") and person.dob and person.dob.lower() != "na":
                    try:
                        dob_date = datetime.strptime(person.dob, "%Y-%m-%d")
                        death_date = None
                        if (
                            hasattr(person, "death_date")
                            and person.death_date
                            and person.death_date.lower() != "na"
                        ):
                            death_date = datetime.strptime(
                                person.death_date, "%Y-%m-%d"
                            )
                        important_dates.append(
                            {
                                "name": person.name,
                                "month": dob_date.month,
                                "day": dob_date.day,
                                "dob": dob_date,
                                "death_date": death_date,
                            }
                        )
                    except ValueError:
                        continue

            # Get birthdays for current month
            birthdays = get_birthdays_in_month(important_dates, month, year)

            # Generate calendar display
            cal_lines = generate_month_calendar(year, month, list(birthdays.keys()))

            # Display calendar
            for line in cal_lines:
                calendar_text.insert(tk.END, line + "\n")

            calendar_text.insert(tk.END, "\nBirthdays:\n")

            # Display birthdays
            for day in sorted(birthdays.keys()):
                for person in birthdays[day]:
                    birthday_line = format_birthday_line(day, person, month)
                    calendar_text.insert(tk.END, birthday_line + "\n")

        def prev_month():
            """calculate the previous month"""
            nonlocal current_month, current_year
            current_month -= 1
            if current_month < 1:
                current_month = 12
                current_year -= 1
            update_calendar(current_month, current_year)

        def next_month():
            """calculate the next month"""
            nonlocal current_month, current_year
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
            update_calendar(current_month, current_year)

        # Navigation buttons
        ttk.Button(nav_frame, text="Previous Month", command=prev_month).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(nav_frame, text="Next Month", command=next_month).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(nav_frame, text="Close", command=calendar_window.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Initial calendar display
        update_calendar(current_month, current_year)


if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"], check=True)