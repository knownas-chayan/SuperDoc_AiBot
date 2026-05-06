#  SecureDoc — Private QA Bot

A fully local, private PDF question-answering bot.
No cloud. No data leaks. Everything runs on your machine.

##  How to Use

1. **Upload a PDF** using the sidebar
2. Click **"Index Document"** — this embeds it into ChromaDB locally
3. **Ask questions** in the chat box
4. Get answers with **page citations** ✅

---

##  Project Structure

```
securedoc/
├── app.py            ← Streamlit UI
├── rag_engine.py     ← ChromaDB + Ollama RAG logic
├── pdf_loader.py     ← PDF reading & chunking
├── requirements.txt  ← Python packages
└── chroma_db/        ← Auto-created vector database (local)
```

---

##  Configuration

In `rag_engine.py` you can change:

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama3` | Any model you've pulled in Ollama |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `TOP_K` | `5` | Number of chunks retrieved per query |

---

##  Privacy Guarantee

- ChromaDB stores all vectors **locally** in `./chroma_db/`
- Ollama runs the LLM **on your GPU** — no API calls
- Zero internet traffic after initial model download
