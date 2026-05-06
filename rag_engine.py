import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import os

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="pdf_chunks")

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def ingest_chunks(chunks, filename):
    """Ingest chunks into ChromaDB."""
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    documents = [chunk['text'] for chunk in chunks]
    embeddings = embedder.encode(documents).tolist()
    metadatas = [chunk['metadata'] for chunk in chunks]
    metadatas = [{**m, 'filename': filename} for m in metadatas]
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(chunks)

def query_rag(question, top_k=5):
    """Query the RAG system."""
    # Embed question
    question_embedding = embedder.encode([question]).tolist()[0]
    
    # Search
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )
    
    # Prepare context
    context = "\n".join(results['documents'][0])
    
    # Generate answer using Ollama
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    try:
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        answer = response['message']['content']
    except Exception as e:
        answer = f"Error generating answer: {str(e)}. Please ensure Ollama is running with the 'llama3' model."
    
    # Prepare sources
    sources = []
    for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        sources.append({
            'file': meta['filename'],
            'page': meta['page'],
            'relevance': int((1 - dist) * 100)  # Rough relevance score
        })
    
    return {
        'answer': answer,
        'sources': sources
    }

def clear_database():
    """Clear the ChromaDB collection."""
    global collection
    client.delete_collection(name="pdf_chunks")
    collection = client.get_or_create_collection(name="pdf_chunks")

def get_indexed_count():
    """Get the number of indexed chunks."""
    return collection.count()