import PyPDF2
from io import BytesIO

def get_pdf_metadata(file_bytes):
    """Extract metadata from PDF bytes."""
    pdf_file = BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    metadata = pdf_reader.metadata
    return {
        'num_pages': num_pages,
        'title': metadata.get('/Title', 'Unknown'),
        'author': metadata.get('/Author', 'Unknown'),
        'subject': metadata.get('/Subject', 'Unknown'),
        'creator': metadata.get('/Creator', 'Unknown'),
    }

def load_pdf_chunks(file_bytes, chunk_size=1000):
    """Load PDF and split into text chunks."""
    pdf_file = BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    chunks = []
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text.strip():
            # Simple chunking by splitting text
            words = text.split()
            for i in range(0, len(words), chunk_size // 10):  # Rough estimate
                chunk = ' '.join(words[i:i + chunk_size // 10])
                if chunk.strip():
                    chunks.append({
                        'text': chunk,
                        'page': page_num + 1,
                        'metadata': {'page': page_num + 1}
                    })
    return chunks