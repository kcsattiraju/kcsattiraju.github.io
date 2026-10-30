
import hashlib
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_config import (
    DOCUMENTS_DIR,
    generate_embedding,
    get_collection
)


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def extract_pdf_pages(pdf_path: Path):
    """Extract text while retaining page numbers."""

    reader = PdfReader(str(pdf_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


def ingest_pdf(pdf_path: Path):
    """Split, embed and index one PDF."""

    print(f"\nProcessing: {pdf_path.name}")

    pages = extract_pdf_pages(pdf_path)

    if not pages:
        print("No extractable text found. Skipping.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    collection = get_collection()
    indexed_count = 0

    for page in pages:
        chunks = splitter.split_text(page["text"])

        for chunk_number, chunk in enumerate(chunks):

            # Stable ID for repeated ingestion
            identifier = hashlib.sha256(
                (
                    pdf_path.name
                    + str(page["page"])
                    + str(chunk_number)
                ).encode("utf-8")
            ).hexdigest()

            embedding = generate_embedding(chunk)

            collection.upsert(
                ids=[identifier],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": pdf_path.name,
                    "page": page["page"],
                    "chunk": chunk_number
                }]
            )

            indexed_count += 1

    print(f"Indexed {indexed_count} chunks.")


def main():
    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    if not pdf_files:
        print(
            "No PDF files found in documents/."
        )
        return

    for pdf_path in pdf_files:
        ingest_pdf(pdf_path)

    print("\nDocument ingestion complete.")


if __name__ == "__main__":
    main()
