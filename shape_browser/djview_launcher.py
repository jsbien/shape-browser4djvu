import subprocess
import logging

LOG_FILE = "shape_browser_djview.log"


class DjViewLauncher:
    def __init__(self, document_path):
        self.document_path = document_path
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger("DjViewLauncher")
        self.logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if GUI creates multiple instances
        if not self.logger.handlers:
            file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s\n%(message)s\n")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    # -------------------------------------------------
    # Page mode: highlight all occurrences
    # -------------------------------------------------

    def open_occurrences(self, page_number, shape, occurrences):
        """
        Open djview4 and highlight all occurrences of the shape on given page.
        """
        page_1based = page_number + 1

        highlights = []
        for occ in occurrences:
            x = occ.x
            y = occ.y
            w = shape.width
            h = shape.height
            highlights.append(f"highlight={x},{y},{w},{h}")

        query = f"djvuopts=&page={page_1based}&" + "&".join(highlights)
        url = f"file://{self.document_path}?{query}"

        self._log_launch(
            shape=shape,
            page_number=page_number,
            page_1based=page_1based,
            occurrences=occurrences,
            highlights=highlights,
            url=url,
        )

        subprocess.Popen(["djview4", url])

    # -------------------------------------------------
    # Structured logging
    # -------------------------------------------------

    def _log_launch(
        self,
        shape,
        page_number,
        page_1based,
        occurrences,
        highlights,
        url,
    ):
        lines = []

        lines.append("=" * 60)
        lines.append("DjView Launch Mode: PAGE")
        lines.append(f"Document: {self.document_path}")
        lines.append("")
        lines.append("Shape metadata:")
        lines.append(f"  Shape ID: {shape.id}")
        lines.append(f"  Parent ID: {shape.parent_id}")
        lines.append(f"  Depth: {shape.depth}")
        lines.append(f"  Sibling index: {shape.sibling_index}")
        lines.append(f"  Size: {shape.width} x {shape.height}")
        lines.append(f"  Usage count: {shape.usage_count}")
        lines.append(f"  Subtree usage: {shape.subtree_count}")
        lines.append("")
        lines.append(f"DB page (0-based): {page_number}")
        lines.append(f"DjView page (1-based): {page_1based}")
        lines.append("")
        lines.append("Occurrences:")

        for i, occ in enumerate(occurrences, 1):
            lines.append(
                f"  #{i}: x={occ.x} y={occ.y} "
                f"w={shape.width} h={shape.height}"
            )

        lines.append("")
        lines.append("Highlight parameters:")
        for h in highlights:
            lines.append(f"  {h}")

        lines.append("")
        lines.append("Final URL:")
        lines.append(url)
        lines.append("=" * 60)
        lines.append("")

        self.logger.info("\n".join(lines))
        
