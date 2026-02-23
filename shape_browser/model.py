class Shape:
    def __init__(self, row):
        self.id = row["id"]
        self.dictionary_id = row.get("dictionary_id")
        self.parent_id = row["parent_id"]
        self.width = row["width"]
        self.height = row["height"]

        # REQUIRED for renderer
        self.bits = row["bits"]

        # Derived / computed (lazy)
        self.children = []
        self.parent = None
        self.children_loaded = False

        self.depth = 0
        self.sibling_index = 0

        # Usage is required and comes from sb_shape_usage join
        self.usage_count = int(row.get("usage_count", 0))

        # Subtree usage: computed only for loaded subtree for now
        self.subtree_count = self.usage_count

        # Occurrences loaded lazily
        self.occurrences = None  # None = not loaded yet


class Occurrence:
    def __init__(self, blit_row):
        self.shape_id = blit_row["shape_id"]
        self.page_number = blit_row.get("page", blit_row.get("page_number"))
        self.x = blit_row["b_left"]
        self.y = blit_row["b_bottom"]


class ShapeModel:
    """
    Lazy, repository-backed shape model.

    This avoids loading all shapes/blits (needed for very large datasets).
    """

    def __init__(self, repo, document_id, root_rows):
        self.repo = repo
        self.document_id = document_id

        # Loaded shapes cache (shape_id -> Shape)
        self.shapes = {}

        # Root shapes (loaded at startup)
        self.root_shapes = []
        for row in root_rows:
            shape = Shape(row)
            self.shapes[shape.id] = shape
            self.root_shapes.append(shape)

        # Assign root indices and depth
        for i, root in enumerate(self.root_shapes):
            root.depth = 0
            root.sibling_index = i + 1

    # -----------------------------
    # Lazy loading
    # -----------------------------

    def ensure_children_loaded(self, shape):
        if shape.children_loaded:
            return

        # Fetch children within same dictionary and document
        child_rows = self.repo.fetch_child_shapes(
            self.document_id,
            shape.dictionary_id,
            shape.id,
        )

        children = []
        for i, row in enumerate(child_rows):
            child = self.shapes.get(row["id"])
            if child is None:
                child = Shape(row)
                self.shapes[child.id] = child

            child.parent = shape
            child.depth = shape.depth + 1
            child.sibling_index = i + 1
            children.append(child)

        shape.children = children
        shape.children_loaded = True

    def get_occurrences(self, shape):
        if shape.occurrences is not None:
            return shape.occurrences

        rows = self.repo.fetch_occurrences(self.document_id, shape.id)
        shape.occurrences = [Occurrence(r) for r in rows]
        return shape.occurrences

    # -----------------------------
    # Subtree support (lazy)
    # -----------------------------

    def collect_subtree(self, root_shape):
        """
        Return a list of shapes in the subtree of root_shape.

        Loads children lazily as needed.
        Also recomputes subtree_count for the loaded subtree.
        """
        result = []

        def dfs(node):
            result.append(node)
            self.ensure_children_loaded(node)
            for ch in node.children:
                dfs(ch)

        dfs(root_shape)

        # Recompute subtree counts for this loaded subtree only
        def post(node):
            self.ensure_children_loaded(node)
            total = node.usage_count
            for ch in node.children:
                total += post(ch)
            node.subtree_count = total
            return total

        post(root_shape)
        return result
