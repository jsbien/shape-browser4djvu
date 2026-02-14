import tkinter as tk
from tkinter import ttk, messagebox


PROGRAM_NAME = "Shape Browser"


class ShapeBrowserGUI:
    def __init__(
        self,
        root,
        model,
        renderer,
        tile_size,
        database_name,
        version,
        build_timestamp,
    ):
        self.root = root
        self.model = model
        self.renderer = renderer
        self.tile_size = tile_size
        self.database_name = database_name
        self.version = version
        self.build_timestamp = build_timestamp

        self.all_shapes = sorted(
            self.model.shapes.values(),
            key=lambda s: s.height,
            reverse=True,
        )

        self.filtered_shapes = self.all_shapes

        self.columns = 6
        self.shape_positions = {}
        self.index_by_shape_id = {}
        self.current_index = None
        self.current_highlight = None

        # Subtree mode (single level)
        self.current_subtree_root = None

        self.root.title(f"{PROGRAM_NAME} {self.version}")

        self._build_menu()
        self._build_layout()

        self.depth_max_entry.insert(0, "0")
        self._apply_filters()

        self._bind_keys()
        self._update_info_bar()

        self.root.focus_set()

    # -------------------------------------------------
    # Menu
    # -------------------------------------------------

    def _build_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _show_about(self):
        messagebox.showinfo(
            "About",
            f"{PROGRAM_NAME}\nVersion: {self.version}\nBuild: {self.build_timestamp}",
        )

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    def _build_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Top info bar
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(side="top", fill="x")

        self.info_label = ttk.Label(self.info_frame, text="")
        self.info_label.pack(side="left", padx=5)

        self.back_button = ttk.Button(
            self.info_frame,
            text="Back",
            command=self._exit_subtree_mode,
        )

        # Full filter row (restored)
        self.filter_frame = ttk.Frame(self.main_frame)
        self.filter_frame.pack(side="top", fill="x", pady=4)

        # Direct range
        ttk.Label(self.filter_frame, text="Direct:").pack(side="left")
        self.direct_min = ttk.Entry(self.filter_frame, width=4)
        self.direct_min.pack(side="left")
        ttk.Label(self.filter_frame, text="-").pack(side="left")
        self.direct_max = ttk.Entry(self.filter_frame, width=4)
        self.direct_max.pack(side="left")

        # Subtree range
        ttk.Label(self.filter_frame, text=" Subtree:").pack(side="left")
        self.subtree_min = ttk.Entry(self.filter_frame, width=4)
        self.subtree_min.pack(side="left")
        ttk.Label(self.filter_frame, text="-").pack(side="left")
        self.subtree_max = ttk.Entry(self.filter_frame, width=4)
        self.subtree_max.pack(side="left")

        # Height range
        ttk.Label(self.filter_frame, text=" Height:").pack(side="left")
        self.height_min = ttk.Entry(self.filter_frame, width=4)
        self.height_min.pack(side="left")
        ttk.Label(self.filter_frame, text="-").pack(side="left")
        self.height_max = ttk.Entry(self.filter_frame, width=4)
        self.height_max.pack(side="left")

        # Ratio range
        ttk.Label(self.filter_frame, text=" Ratio (H/W):").pack(side="left")
        self.ratio_min = ttk.Entry(self.filter_frame, width=4)
        self.ratio_min.pack(side="left")
        ttk.Label(self.filter_frame, text="-").pack(side="left")
        self.ratio_max = ttk.Entry(self.filter_frame, width=4)
        self.ratio_max.pack(side="left")

        # Max depth
        ttk.Label(self.filter_frame, text=" Max depth:").pack(side="left")
        self.depth_max_entry = ttk.Entry(self.filter_frame, width=4)
        self.depth_max_entry.pack(side="left")

        self.apply_button = ttk.Button(
            self.filter_frame,
            text="Apply",
            command=self._apply_filters,
        )
        self.apply_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(
            self.filter_frame,
            text="Clear",
            command=self._clear_filters,
        )
        self.clear_button.pack(side="left")

        # Canvas
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Side panel
        self.side_panel = ttk.Frame(self.root, width=300)
        self.side_panel.pack(side="right", fill="y")

        self.metadata_label = ttk.Label(
            self.side_panel,
            text="Select a shape",
            justify="left",
        )
        self.metadata_label.pack(anchor="nw", padx=10, pady=10)

    # -------------------------------------------------
    # Subtree logic
    # -------------------------------------------------

    def _collect_subtree_nodes(self, root_shape):
        result = []

        def dfs(node):
            result.append(node)
            for child in node.children:
                dfs(child)

        dfs(root_shape)
        return result

    def _enter_subtree_mode(self, root_shape):
        if self.current_subtree_root is not None:
            return

        self.current_subtree_root = root_shape
        self.back_button.pack(side="right", padx=5)

        self.filtered_shapes = self._collect_subtree_nodes(root_shape)
        self.current_index = None
        self.current_highlight = None

        self._draw_all_shapes()
        self._update_info_bar()

    def _exit_subtree_mode(self):
        self.current_subtree_root = None
        self.back_button.pack_forget()
        self._apply_filters()

    # -------------------------------------------------
    # Filters (original logic preserved)
    # -------------------------------------------------

    def _apply_filters(self):
        if self.current_subtree_root is not None:
            return

        value = self.depth_max_entry.get().strip()

        if value:
            try:
                depth_max = int(value)
            except ValueError:
                depth_max = None
        else:
            depth_max = None

        filtered = []

        for shape in self.all_shapes:
            if depth_max is not None and shape.depth > depth_max:
                continue
            filtered.append(shape)

        self.filtered_shapes = filtered
        self._draw_all_shapes()
        self._update_info_bar()

    def _clear_filters(self):
        if self.current_subtree_root is not None:
            return

        self.depth_max_entry.delete(0, tk.END)
        self.filtered_shapes = self.all_shapes
        self._draw_all_shapes()
        self._update_info_bar()

    # -------------------------------------------------
    # Info bar
    # -------------------------------------------------

    def _update_info_bar(self):
        total = len(self.all_shapes)
        shown = len(self.filtered_shapes)

        if self.current_subtree_root:
            text = (
                f"{PROGRAM_NAME} {self.version} "
                f"({self.build_timestamp}) | "
                f"Subtree of {self.current_subtree_root.id} | "
                f"Nodes: {shown}"
            )
        else:
            text = (
                f"{PROGRAM_NAME} {self.version} "
                f"({self.build_timestamp}) | "
                f"DB: {self.database_name} | "
                f"Showing: {shown} / {total}"
            )

        self.info_label.config(text=text)

    # -------------------------------------------------
    # Drawing
    # -------------------------------------------------

    def _draw_all_shapes(self):
        self.canvas.delete("all")
        self._image_refs = []

        tile = self.tile_size
        columns = self.columns

        self.shape_positions.clear()
        self.index_by_shape_id.clear()

        for index, shape in enumerate(self.filtered_shapes):
            row = index // columns
            col = index % columns

            self.shape_positions[shape.id] = (row, col)
            self.index_by_shape_id[shape.id] = index

            x = col * tile + tile // 2
            y = row * tile + tile // 2

            tk_image = self.renderer.get_tk_image(shape, tile)
            self._image_refs.append(tk_image)

            item = self.canvas.create_image(x, y, image=tk_image)

            parent_text = shape.parent_id if shape.parent_id is not None else "-"
            badge_text = f"{shape.depth}.{shape.sibling_index} (p:{parent_text})"

            text_id = self.canvas.create_text(
                x - tile // 2 + 4,
                y - tile // 2 + 4,
                anchor="nw",
                text=badge_text,
                font=("TkDefaultFont", 8),
                fill="black",
            )

            bbox = self.canvas.bbox(text_id)
            rect_id = self.canvas.create_rectangle(
                bbox,
                fill="white",
                outline=""
            )
            self.canvas.tag_raise(text_id, rect_id)

            self.canvas.tag_bind(
                item,
                "<Button-1>",
                lambda e, s=shape: self._on_click(e, s),
            )

        total_rows = (len(self.filtered_shapes) + columns - 1) // columns
        self.canvas.configure(
            scrollregion=(0, 0, columns * tile, total_rows * tile)
        )

    # -------------------------------------------------
    # Click handling
    # -------------------------------------------------

    def _on_click(self, event, shape):
        if event.state & 0x0004:
            self._enter_subtree_mode(shape)
        else:
            self._select_shape(shape)

    def _select_shape(self, shape):
        self.current_index = self.index_by_shape_id[shape.id]
        self._highlight_shape(shape)
        self._update_side_panel(shape)

    # -------------------------------------------------
    # Highlight & panel
    # -------------------------------------------------

    def _highlight_shape(self, shape):
        tile = self.tile_size

        if self.current_highlight is not None:
            self.canvas.delete(self.current_highlight)

        row, col = self.shape_positions[shape.id]

        self.current_highlight = self.canvas.create_rectangle(
            col * tile,
            row * tile,
            col * tile + tile,
            row * tile + tile,
            outline="red",
            width=2,
        )

    def _update_side_panel(self, shape):
        ratio = shape.height / shape.width if shape.width else 0

        metadata = (
            f"Shape ID: {shape.id}\n"
            f"Parent ID: {shape.parent_id}\n"
            f"Size: {shape.width} x {shape.height}\n"
            f"Ratio: {ratio:.3f}\n"
            f"Depth: {shape.depth}\n"
            f"Sibling index: {shape.sibling_index}\n"
            f"Usage: {shape.usage_count}\n"
            f"Subtree usage: {shape.subtree_count}\n"
            f"Children: {len(shape.children)}\n"
        )

        self.metadata_label.config(text=metadata)

    # -------------------------------------------------
    # Keyboard navigation
    # -------------------------------------------------

    def _bind_keys(self):
        self.root.bind("<Left>", self._move_left)
        self.root.bind("<Right>", self._move_right)
        self.root.bind("<Up>", self._move_up)
        self.root.bind("<Down>", self._move_down)

    def _move_left(self, event=None):
        if self.current_index is None:
            return
        if self.current_index % self.columns > 0:
            self._select_by_index(self.current_index - 1)

    def _move_right(self, event=None):
        if self.current_index is None:
            return
        if self.current_index < len(self.filtered_shapes) - 1:
            if self.current_index % self.columns < self.columns - 1:
                self._select_by_index(self.current_index + 1)

    def _move_up(self, event=None):
        if self.current_index is None:
            return
        target = self.current_index - self.columns
        if target >= 0:
            self._select_by_index(target)

    def _move_down(self, event=None):
        if self.current_index is None:
            return
        target = self.current_index + self.columns
        if target < len(self.filtered_shapes):
            self._select_by_index(target)

    def _select_by_index(self, index):
        shape = self.filtered_shapes[index]
        self.current_index = index
        self._highlight_shape(shape)
        self._update_side_panel(shape)
