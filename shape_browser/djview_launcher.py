import subprocess


class DjViewLauncher:
    def __init__(self, document_path):
        self.document_path = document_path

    def open_occurrences(self, page_number, shape, occurrences):
        """
        Open djview4 and highlight all occurrences of the shape on given page.
        """

        # djview expects 1-based page numbers
        page = page_number + 1

        highlights = []
        for occ in occurrences:
            x = occ.x
            y = occ.y
            w = shape.width
            h = shape.height
            highlights.append(f"highlight={x},{y},{w},{h}")

        query = f"djvuopts=&page={page}&" + "&".join(highlights)
        url = f"file://{self.document_path}?{query}"

        subprocess.Popen(["djview4", url])
