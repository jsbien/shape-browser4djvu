class Shape:
    def __init__(self, row):
        self.id = row["id"]
        self.parent_id = row["parent_id"]
        self.width = row["width"]
        self.height = row["height"]

        # REQUIRED for renderer
        self.bits = row["bits"]

        self.children = []
        self.parent = None

        self.depth = 0
        self.sibling_index = 0

        self.usage_count = 0
        self.subtree_count = 0
        self.occurrences = []

class Occurrence:
    def __init__(self, blit_row):
        self.shape_id = blit_row["shape_id"]
        self.page_number = blit_row.get("page", blit_row.get("page_number"))
        self.x = blit_row.get("x", 0)
        self.y = blit_row.get("y", 0)


class ShapeModel:
    def __init__(self, shape_rows, blit_rows):
        # ----------------------------------------
        # Create shape objects
        # ----------------------------------------
        self.shapes = {}

        for row in shape_rows:
            shape = Shape(row)
            self.shapes[shape.id] = shape

        # ----------------------------------------
        # Build parent-child relationships
        # ----------------------------------------
        for shape in self.shapes.values():
            if shape.parent_id and shape.parent_id in self.shapes:
                parent = self.shapes[shape.parent_id]
                shape.parent = parent
                parent.children.append(shape)

        # ----------------------------------------
        # Identify roots
        # ----------------------------------------
        self.root_shapes = [
            shape for shape in self.shapes.values()
            if shape.parent is None
        ]

        # ----------------------------------------
        # Compute depth
        # ----------------------------------------
        for root in self.root_shapes:
            self._assign_depth(root, depth=0)

        # ----------------------------------------
        # Attach occurrences
        # ----------------------------------------
        for row in blit_rows:
            occ = Occurrence(row)
            if occ.shape_id in self.shapes:
                shape = self.shapes[occ.shape_id]
                shape.occurrences.append(occ)
                shape.usage_count += 1

        # ----------------------------------------
        # Compute subtree usage counts
        # ----------------------------------------
        for root in self.root_shapes:
            self._compute_subtree_count(root)

        # ----------------------------------------
        # Assign sibling indices
        # ----------------------------------------
        self._assign_sibling_indices()

    # --------------------------------------------
    # Depth assignment (DFS)
    # --------------------------------------------
    def _assign_depth(self, shape, depth):
        shape.depth = depth
        for child in shape.children:
            self._assign_depth(child, depth + 1)

    # --------------------------------------------
    # Subtree count (post-order traversal)
    # --------------------------------------------
    def _compute_subtree_count(self, shape):
        total = shape.usage_count

        for child in shape.children:
            total += self._compute_subtree_count(child)

        shape.subtree_count = total
        return total

    # --------------------------------------------
    # Sibling index assignment
    # --------------------------------------------
    def _assign_sibling_indices(self):
        # Roots
        for i, root in enumerate(self.root_shapes):
            root.sibling_index = i + 1

        # Children
        for shape in self.shapes.values():
            if shape.children:
                for i, child in enumerate(shape.children):
                    child.sibling_index = i + 1
