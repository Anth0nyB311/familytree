"""Family Tree GUI Module.

This module provides the graphical user interface for managing and
visualizing family trees. It includes functionality for creating,
editing, and displaying family relationships.
"""

# Standard library imports
import os
import sys
import io
from collections import defaultdict
from datetime import datetime
from math import floor

# Third-party imports
import tkinter as tk
from tkinter import messagebox, ttk

# Local application imports
from family_lib import Parent, Child, Partner
from main import FamilyTree, FamilyTreeStatistics
import yaml_lib


class FamilyTreeVisualizer:
    """Handles the visual representation of the family tree."""

    def __init__(self):
        """Initialize the visualizer with grid-based layout."""
        self.cell_width = 250
        self.cell_height = 150
        self.node_radius = 45
        self.grid = {}
        self.positions = {}
        self.level_count = {}

    def draw_tree(self, canvas, root_person):
        """Draw the family tree on the canvas.
        
        Args:
            canvas: tkinter Canvas to draw on
            root_person: Person object to use as tree root
        """
        if not root_person:
            return

        self._reset_state()
        self._assign_grid_positions(root_person, 0, 0)
        self._calculate_dimensions(canvas)
        self._draw_tree_elements(canvas, root_person)

    def _reset_state(self):
        """Reset the visualizer's state."""
        self.grid = {}
        self.positions = {}
        self.level_count = {}

    def _calculate_dimensions(self, canvas):
        """Calculate and set canvas dimensions."""
        if not self.grid:
            return

        max_row = max(row for row, _ in self.grid.keys())
        max_col = max(col for _, col in self.grid.keys())
        
        self._calculate_canvas_positions()
        canvas.delete("all")
        
        canvas_width = (max_col + 2) * self.cell_width + 100
        canvas_height = (max_row + 2) * self.cell_height + 100
        canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

    def _draw_tree_elements(self, canvas, root_person):
        """Draw all tree elements.
        
        Args:
            canvas: tkinter Canvas to draw on
            root_person: Person object to use as tree root
        """
        self._draw_connections(canvas, root_person)
        for person, (x, y) in self.positions.items():
            self._draw_node(canvas, person, x, y)


class FamilyTreeGUI:
    """GUI interface for the Family Tree application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = None
        self.tree_canvas = None
        self.family_listbox = None
        self.tree_visualizer = None
        self.selected_person = None
        self.family_tree = FamilyTree(None)  # Initialize with no save file
        self.zoom_scale = 1.0

    def display_family(self):
        """Display the main family tree interface."""
        self._setup_main_window()
        self._create_frames()
        self.refresh_family_list()
        self.root.mainloop()

    def _setup_main_window(self):
        """Set up the main application window."""
        self.root = tk.Tk()
        self.root.title("Family Tree Manager")
        self.root.geometry("1400x800")
        self.tree_visualizer = FamilyTreeVisualizer()

    def _create_frames(self):
        """Create and set up main GUI frames."""
        left_frame = self._create_left_frame()
        right_frame = self._create_right_frame()
        
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_left_frame(self):
        """Create and configure the left control panel.
        
        Returns:
            ttk.Frame: Configured left frame
        """
        left_frame = ttk.Frame(self.root, width=300)
        left_frame.pack_propagate(False)

        self._add_file_operations(left_frame)
        self._add_family_list(left_frame)
        self._add_person_management(left_frame)
        self._add_relationship_buttons(left_frame)
        self._add_statistics_buttons(left_frame)
        self._add_exit_button(left_frame)

        return left_frame

    def _add_file_operations(self, frame):
        """Add file operation buttons to frame.
        
        Args:
            frame: Parent frame for buttons
        """
        ttk.Label(
            frame,
            text="File Operations",
            font=('Arial', 10, 'bold')
        ).pack(fill=tk.X, pady=(0, 5))
        
        operations = [
            ("New Family Tree", self.new_family),
            ("Load Family Tree", self.load_family),
            ("Save Family Tree", self.save_family)
        ]
        
        for text, command in operations:
            ttk.Button(
                frame,
                text=text,
                command=command
            ).pack(fill=tk.X)

    def _add_family_list(self, frame):
        """Add family members listbox to frame.
        
        Args:
            frame: Parent frame for listbox
        """
        ttk.Label(
            frame,
            text="Family Members",
            font=('Arial', 10, 'bold')
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.family_listbox = tk.Listbox(frame, height=8)
        self.family_listbox.pack(fill=tk.X)
        self.family_listbox.bind('<<ListboxSelect>>', self.on_select_person)

    def _add_person_management(self, frame):
        """Add person management buttons to frame.
        
        Args:
            frame: Parent frame for buttons
        """
        ttk.Label(
            frame,
            text="Person Management",
            font=('Arial', 10, 'bold')
        ).pack(fill=tk.X, pady=(10, 5))
        
        management_buttons = [
            ("Add Person", self.add_person_dialog),
            ("Add Relationship", self.add_relationship_dialog)
        ]
        
        for text, command in management_buttons:
            ttk.Button(
                frame,
                text=text,
                command=command
            ).pack(fill=tk.X)

    def _add_relationship_buttons(self, frame):
        """Add relationship viewing buttons to frame.
        
        Args:
            frame: Parent frame for buttons
        """
        ttk.Label(
            frame,
            text="View Relationships",
            font=('Arial', 10, 'bold')
        ).pack(fill=tk.X, pady=(10, 5))
        
        relationships = ["Parents", "Siblings", "Children", "Extended Family"]
        
        for rel_type in relationships:
            ttk.Button(
                frame,
                text=f"Show {rel_type}",
                command=lambda t=rel_type: self.show_relationships(
                    self.selected_person,
                    t
                )
            ).pack(fill=tk.X)

    def _add_statistics_buttons(self, frame):
        """Add statistics buttons to frame.
        
        Args:
            frame: Parent frame for buttons
        """
        ttk.Label(
            frame,
            text="Statistics",
            font=('Arial', 10, 'bold')
        ).pack(fill=tk.X, pady=(10, 5))
        
        stats = [
            "Average Age",
            "Death Age",
            "Children Count",
            "Average Children"
        ]
        
        for stat_type in stats:
            ttk.Button(
                frame,
                text=stat_type,
                command=lambda t=stat_type: self.show_statistics(t)
            ).pack(fill=tk.X)

    def _create_right_frame(self):
        """Create and configure the right frame with canvas.
        
        Returns:
            ttk.Frame: Configured right frame
        """
        right_frame = ttk.Frame(self.root)
        canvas_container = ttk.Frame(right_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
        
        self._setup_canvas(canvas_container)
        return right_frame

    def _setup_canvas(self, container):
        """Setup the tree canvas with scrollbars.
        
        Args:
            container: Parent frame for canvas
        """
        self.tree_canvas = tk.Canvas(container, bg='white')
        v_scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.tree_canvas.yview
        )
        h_scrollbar = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=self.tree_canvas.xview
        )
        
        # Configure scrolling
        self.tree_canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Grid layout
        self.tree_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind mouse wheel
        self.tree_canvas.bind('<MouseWheel>', self._on_mousewheel_y)
        self.tree_canvas.bind('<Shift-MouseWheel>', self._on_mousewheel_x)

    def on_select_person(self, event):
        """Handle person selection from listbox.
        
        Args:
            event: Selection event
        """
        selection = self.family_listbox.curselection()
        if selection:
            try:
                index = selection[0]
                self.selected_person = self.family_tree.family[index]
                self.tree_visualizer.draw_tree(
                    self.tree_canvas,
                    self.selected_person
                )
            except Exception as e:
                print(f"Debug - Selection error: {str(e)}")
                self.selected_person = None

    def add_person_dialog(self):
        """Display dialog for adding a new person."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Person")
        
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields
        fields = self._create_person_form_fields(form_frame)
        
        # Add buttons
        self._add_dialog_buttons(
            form_frame,
            dialog,
            lambda: self._submit_person_form(fields, dialog)
        )

    def _create_person_form_fields(self, frame):
        """Create form fields for person dialog.
        
        Args:
            frame: Parent frame for form fields
            
        Returns:
            dict: Dictionary of form field variables
        """
        fields = {}
        
        # Person type selection
        fields['type'] = tk.StringVar(value="Parent")
        ttk.Label(frame, text="Person Type:").pack(fill=tk.X)
        for type_name in ["Parent", "Child", "Partner"]:
            ttk.Radiobutton(
                frame,
                text=type_name,
                variable=fields['type'],
                value=type_name
            ).pack()

        # Name entry
        ttk.Label(frame, text="Name:").pack(fill=tk.X)
        fields['name'] = ttk.Entry(frame)
        fields['name'].pack(fill=tk.X)
        
        return fields

    def _submit_person_form(self, fields, dialog):
        """Handle person form submission.
        
        Args:
            fields: Dictionary of form field variables
            dialog: Dialog window to close on success
        """
        try:
            name = fields['name'].get().strip()
            person_type = fields['type'].get()
            
            if not name:
                raise ValueError("Name is required")
            
            # Use FamilyTree's add_person method
            command = f"ADD {person_type} '{name}'"
            self.family_tree.add_remove_person(True, command)
            
            dialog.destroy()
            self.refresh_family_list()
            messagebox.showinfo(
                "Success",
                f"Added {person_type} {name} to family tree!"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add person: {str(e)}")
    def add_relationship_dialog(self):
        """Display dialog for adding relationships."""
        if not self.selected_person:
            messagebox.showerror("Error", "Please select a person first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Relationship")
        
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create relationship form
        fields = self._create_relationship_form(form_frame)
        
        # Add buttons
        self._add_dialog_buttons(
            form_frame,
            dialog,
            lambda: self._submit_relationship_form(fields, dialog)
        )

    def _create_relationship_form(self, frame):
        """Create form fields for relationship dialog.
        
        Args:
            frame: Parent frame for form fields
            
        Returns:
            dict: Dictionary of form field variables
        """
        fields = {}
        
        ttk.Label(
            frame,
            text=f"Add relationship for: {self.selected_person.name}"
        ).pack(fill=tk.X)
        
        # Relationship type selection
        fields['type'] = tk.StringVar(value="Parent")
        ttk.Label(frame, text="Relationship Type:").pack(fill=tk.X)
        for rel_type in ["Parent", "Child", "Partner"]:
            ttk.Radiobutton(
                frame,
                text=rel_type,
                variable=fields['type'],
                value=rel_type
            ).pack()

        # Related person selection
        ttk.Label(frame, text="Related Person:").pack(fill=tk.X)
        fields['related_person'] = tk.StringVar()
        person_list = ttk.Combobox(
            frame,
            textvariable=fields['related_person']
        )
        person_list['values'] = [
            person.name for person in self.family_tree.family
            if person != self.selected_person
        ]
        person_list.pack(fill=tk.X)
        
        return fields

    def _submit_relationship_form(self, fields, dialog):
        """Handle relationship form submission.
        
        Args:
            fields: Dictionary of form field variables
            dialog: Dialog window to close on success
        """
        try:
            related_person = fields['related_person'].get()
            rel_type = fields['type'].get()
            
            if not related_person:
                raise ValueError("Please select a related person")
            
            # Use FamilyTree's add_relationship method
            command = (
                f"ADD RELATIONSHIP '{self.selected_person.name}' "
                f"TO '{related_person}'"
            )
            self.family_tree.add_remove_relationship(True, command)
            
            dialog.destroy()
            self.refresh_family_list()
            messagebox.showinfo(
                "Success",
                "Relationship added successfully!"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add relationship: {str(e)}")

    def _add_dialog_buttons(self, frame, dialog, submit_command):
        """Add standard dialog buttons.
        
        Args:
            frame: Parent frame for buttons
            dialog: Dialog window to close on cancel
            submit_command: Function to call on submit
        """
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Submit",
            command=submit_command
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT)

    def show_birthdays(self):
        """Display birthdays for all family members."""
        try:
            output = io.StringIO()
            sys.stdout = output
            
            self.family_tree.get_birthdays("ALLBIRTHDAYS")
            
            sys.stdout = sys.__stdout__
            message = output.getvalue()
            output.close()
            
            if message.strip():
                messagebox.showinfo("Birthdays", message)
            else:
                messagebox.showinfo("Birthdays", "No birthdays recorded")
                
        except Exception as e:
            sys.stdout = sys.__stdout__
            messagebox.showerror("Error", f"Failed to get birthdays: {str(e)}")

    def save_family(self):
        """Save the family tree to file."""
        try:
            self.family_tree.save_family()
            messagebox.showinfo("Success", "Family tree saved successfully!")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save family tree: {str(e)}"
            )

    def load_family(self):
        """Load a family tree from file."""
        try:
            self.family_tree.load_family()
            self.refresh_family_list()
            messagebox.showinfo("Success", "Family tree loaded successfully!")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load family tree: {str(e)}"
            )

    def new_family(self):
        """Create a new empty family tree."""
        if messagebox.askyesno(
            "New Family Tree",
            "Are you sure you want to create a new family tree? "
            "Any unsaved changes will be lost."
        ):
            try:
                self.family_tree.new_family()
                self.refresh_family_list()
                messagebox.showinfo("Success", "New family tree created!")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to create new family tree: {str(e)}"
                )

    def refresh_family_list(self):
        """Update the family members listbox."""
        self.family_listbox.delete(0, tk.END)
        for person in self.family_tree.family:
            self.family_listbox.insert(tk.END, person.name)

    def exit_program(self):
        """Handle program exit with save option."""
        if messagebox.askyesno("Exit", "Do you want to save before exiting?"):
            self.save_family()
        self.root.quit()

    def _on_mousewheel_y(self, event):
        """Handle vertical scrolling.
        
        Args:
            event: Mouse wheel event
        """
        self.tree_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_x(self, event):
        """Handle horizontal scrolling.
        
        Args:
            event: Mouse wheel event
        """
        self.tree_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == "__main__":
    gui = FamilyTreeGUI()
    gui.display_family()