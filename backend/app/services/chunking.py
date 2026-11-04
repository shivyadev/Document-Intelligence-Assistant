from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

def chunk_document(pages, filename, file_type):

    chunks = []
    chunk_index = 0

    for page_data in pages:
        text = page_data['text']

        if not text.strip():
            continue

        page_chunks = text_splitter.split_text(text)

        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "metadata": {
                    "filename": filename,
                    "file_type": file_type,
                    "page_number": page_data['page'],
                    "chunk_index": chunk_index,
                }
            })

            chunk_index += 1

    return chunks