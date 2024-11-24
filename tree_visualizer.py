"""Tree visualization module for family tree display."""

class FamilyTreeVisualizer:
    """Handles the visual representation of the family tree."""

    def __init__(self):
        """Initialize the visualizer with grid-based layout."""
        self.cell_width = 180
        self.cell_height = 100
        self.node_radius = 45
        self.base_font_size = 11
        self.base_date_font_size = 9
        self.current_scale = 1.0
        self.grid = {}
        self.positions = {}
        self.level_count = {}
        self.visited = set()
        self.margin = 20
        self.node_colors = {
            "bg": "#404040",
            "outline": "#606060",
            "text": "#ffffff",
            "secondary_text": "#cccccc"
        }

    def draw_tree(self, canvas, root_person):
        """Draw the family tree on the canvas."""
        # ... (existing draw_tree code) 