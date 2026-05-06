import streamlit as st
import time
from pdf_loader import load_pdf_chunks, get_pdf_metadata
from rag_engine import ingest_chunks, query_rag, clear_database, get_indexed_count

# ── Page config 
st.set_page_config(
    page_title="SecureDoc",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    /* Dark background */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        color: #e6edf3;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #21262d;
    }

    /* Chat message - user */
    .user-msg {
        background: #1f6feb22;
        border: 1px solid #1f6feb55;
        border-radius: 12px 12px 4px 12px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-left: 15%;
        font-family: 'Syne', sans-serif;
        color: #e6edf3;
        position: relative;
    }

    /* Chat message - assistant */
    .bot-msg {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 12px 12px 12px 4px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-right: 15%;
        font-family: 'Syne', sans-serif;
        color: #e6edf3;
    }

    /* Source badge */
    .source-badge {
        display: inline-block;
        background: #0d419d33;
        border: 1px solid #1f6feb55;
        border-radius: 6px;
        padding: 3px 10px;
        margin: 4px 4px 4px 0;
        font-size: 12px;
        font-family: 'Space Mono', monospace;
        color: #79c0ff;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        border: 2px dashed #21262d;
        border-radius: 12px;
        padding: 10px;
        background: #161b22;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb, #388bfd);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        padding: 10px 20px;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.85;
    }

    /* Danger button */
    .danger-btn > button {
        background: #21262d !important;
        border: 1px solid #f85149 !important;
        color: #f85149 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 14px;
    }

    /* Input box */
    .stTextInput > div > div > input {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #e6edf3;
        font-family: 'Syne', sans-serif;
    }

    /* Title */
    h1 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    /* Divider */
    hr {
        border-color: #21262d;
    }

    /* Success/info boxes */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px;
        font-family: 'Syne', sans-serif;
    }

    /* Scrollable chat area */
    .chat-container {
        max-height: 60vh;
        overflow-y: auto;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []


# ── Sidebar 
with st.sidebar:
    st.markdown("## SecureDoc")
    st.caption("Private QA Bot · 100% Local · Zero Cloud")
    st.divider()

    # Upload section
    st.markdown("### Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        if st.button("Index Document"):
            with st.spinner("Reading PDF..."):
                file_bytes = uploaded_file.read()
                meta = get_pdf_metadata(file_bytes)
                chunks = load_pdf_chunks(file_bytes)

            with st.spinner(f"Embedding {len(chunks)} chunks into ChromaDB..."):
                count = ingest_chunks(chunks, uploaded_file.name)
                if uploaded_file.name not in st.session_state.indexed_files:
                    st.session_state.indexed_files.append(uploaded_file.name)

            st.success(f"✅ Indexed {count} chunks from {meta['num_pages']} pages!")

    st.divider()

    # Stats
    st.markdown("### Index Stats")
    total_chunks = get_indexed_count()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chunks", total_chunks)
    with col2:
        st.metric("Files", len(st.session_state.indexed_files))

    if st.session_state.indexed_files:
        st.markdown("**Indexed files:**")
        for f in st.session_state.indexed_files:
            st.markdown(f"- 📄 `{f}`")

    st.divider()

    # Clear database
    st.markdown("### Danger Zone")
    with st.container():
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear All Data"):
            clear_database()
            st.session_state.indexed_files = []
            st.session_state.messages = []
            st.success("Database cleared!")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("All data stays on your machine.\nNo internet required after setup.")


# ── Main Area 
st.markdown("# SecureDoc")
st.markdown("**Ask questions about your private PDF documents. Everything runs locally.**")
st.divider()

# Chat history display
chat_area = st.container()
with chat_area:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-msg">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="bot-msg">🤖 {msg["content"]}</div>',
                unsafe_allow_html=True
            )
            # Show sources if present
            if msg.get("sources"):
                source_html = "".join([
                    f'<span class="source-badge">📄 {s["file"]} · p.{s["page"]} · {s["relevance"]}%</span>'
                    for s in msg["sources"]
                ])
                st.markdown(source_html, unsafe_allow_html=True)

st.divider()

# Input row
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "Ask a question",
        placeholder="e.g. What is the main topic of this document?",
        label_visibility="collapsed",
        key="user_input"
    )
with col_btn:
    send = st.button("Send →")

# Handle question
if (send or user_input) and user_input.strip():
    question = user_input.strip()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})

    # Get answer
    with st.spinner("🔍 Searching documents..."):
        result = query_rag(question)

    # Add bot message
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })

    # Rerun to refresh chat
    st.rerun()

# Empty state prompt
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #484f58;">
        <div style="font-size: 48px;">🔒</div>
        <div style="font-size: 20px; font-weight: 600; margin-top: 12px;">Upload a PDF to get started</div>
        <div style="font-size: 14px; margin-top: 8px;">Your documents never leave your machine</div>
    </div>
    """, unsafe_allow_html=True)
