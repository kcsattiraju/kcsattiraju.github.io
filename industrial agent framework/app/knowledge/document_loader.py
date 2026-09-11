from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str) -> list[dict]:
    """
    Load a PDF page-by-page.

    Returns:
        List of dictionaries containing:
        - text
        - source filename
        - page number
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    reader = PdfReader(str(path))

    documents = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text()

        if not text:
            continue

        text = text.strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": path.name,
                "page": page_number,
            }
        )

    return documents