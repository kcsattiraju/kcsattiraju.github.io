def split_documents(
    documents: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[dict]:
    """
    Split page text into overlapping chunks while
    preserving source/page metadata.
    """

    chunks = []

    for document in documents:

        text = document["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append(
                    {
                        "text": chunk_text,
                        "source": document["source"],
                        "page": document["page"],
                    }
                )

            start += (
                chunk_size
                - chunk_overlap
            )

    return chunks