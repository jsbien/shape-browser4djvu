import subprocess
import re


class PageInfoProvider:
    """
    Extract page sizes from a DjVu document using `djvudump`.

    Assumption: `djvudump` is available (checked elsewhere). If it fails,
    we raise RuntimeError with a clear message.
    """

    def __init__(self, document_path: str):
        self.document_path = document_path
        self.page_sizes: dict[int, tuple[int, int]] = {}
        self._load_page_sizes()

    def _load_page_sizes(self) -> None:
        try:
            output = subprocess.check_output(
                ["djvudump", self.document_path],
                text=True,
                stderr=subprocess.STDOUT,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to run djvudump on {self.document_path}: {e}"
            )

        current_page = None

        for line in output.splitlines():
            # Page marker like: [P1], [P2], ...
            m_page = re.search(r"\[P(\d+)\]", line)
            if m_page:
                current_page = int(m_page.group(1)) - 1  # 0-based
                continue

            # Size line often contains "DjVu <W>x<H>"
            if current_page is not None and "DjVu" in line:
                m_size = re.search(r"DjVu\s+(\d+)x(\d+)", line)
                if m_size:
                    w = int(m_size.group(1))
                    h = int(m_size.group(2))
                    self.page_sizes[current_page] = (w, h)
                    current_page = None

        if not self.page_sizes:
            raise RuntimeError(
                f"No page size information parsed from djvudump output for {self.document_path}"
            )

    def get_page_size(self, page_number: int) -> tuple[int, int]:
        return self.page_sizes[page_number]

    def get_page_count(self) -> int:
        return len(self.page_sizes)
    
