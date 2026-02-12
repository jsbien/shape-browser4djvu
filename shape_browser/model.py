class Shape:
    def __init__(self, shape_row):
        self.id = shape_row["id"]
        self.parent_id = shape_row["parent_id"]
        self.width = shape_row["width"]
        self.height = shape_row["height"]
        self.depth = shape_row.get("depth", 0)

        # Direct occurrence count (will be filled later)
        self.usage_count = 0

        # Subtree occurrence count (computed later)
        self.subtree_count = 0

        # Tree structure
        self.children = []

        # Occurrence list
        self.occurrences = []


class Occurrence:
    def __init__(self, blit_row):
        self.shape_id = blit_row["shape_id"]
        self.page_number = blit_row["page"]


class ShapeModel:
    def __init__(self, shapes_rows, blits_rows):
        # Build Shape objects
        self.shapes = {}
        for row in shapes_rows:
            shape = Shape(row)
            self.shapes[shape.id] = shape

        # Attach occurrences and compute direct usage_count
        for row in blits_rows:
            occ = Occurrence(row)
            shape = self.shapes.get(occ.shape_id)
            if shape:
                shape.occurrences.append(occ)
                shape.usage_count += 1

        # Build hierarchy
        self.root_shapes = []
        self._build_tree()

        # Compute subtree counts
        self._compute_subtree_counts()

    # -------------------------------------------------
    # Tree construction
    # -------------------------------------------------

    def _build_tree(self):
        for shape in self.shapes.values():
            if shape.parent_id and shape.parent_id in self.shapes:
                parent = self.shapes[shape.parent_id]
                parent.children.append(shape)
            else:
                self.root_shapes.append(shape)

    # -------------------------------------------------
    # Subtree occurrence computation
    # -------------------------------------------------

    def _compute_subtree_counts(self):
        for root in self.root_shapes:
            self._compute_subtree(root)

    def _compute_subtree(self, shape):
        total = shape.usage_count

        for child in shape.children:
            total += self._compute_subtree(child)

        shape.subtree_count = total
        return total

    # -------------------------------------------------
    # Access helpers
    # -------------------------------------------------

    def get_all_shapes(self):
        return list(self.shapes.values())

    def get_root_shapes(self):
        return self.root_shapes
