from app.retrieval.document_loader import load_pdf
from app.retrieval.text_splitter import split_text


text = load_pdf(
    "data/documents/pump_manual.pdf"
)

chunks = split_text(text)

print("Number of chunks:", len(chunks))

for number, chunk in enumerate(
    chunks[:3],
    start=1
):
    print()
    print(f"===== CHUNK {number} =====")
    print(chunk)