from __future__ import annotations

import hashlib

import streamlit as st

from rag_app.core import answer_question, build_index, extract_pdf_pages


st.set_page_config(page_title="University PDF Assistant", page_icon="🎓", layout="wide")
st.title("🎓 University PDF Assistant")
st.caption("Answers are grounded in the PDFs you add. Check the cited document and page before relying on an answer.")

with st.sidebar:
    st.header("Documents and retrieval")
    uploads = st.file_uploader("Upload one or more text-based PDFs", type=["pdf"], accept_multiple_files=True)
    strategy = st.selectbox("Chunking strategy", ["parent_child", "sections", "fixed"],
                            format_func={"parent_child": "Parent-child (hierarchical)",
                                          "sections": "Section-aware", "fixed": "Fixed-size baseline"}.get)
    top_k = st.slider("Retrieved chunks", min_value=1, max_value=10, value=5)
    index_button = st.button("Index / refresh PDFs", type="primary", disabled=not uploads)
    st.caption("Scanned PDFs without selectable text need OCR before upload. Documents are indexed locally by this app.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "index_key" not in st.session_state:
    st.session_state.index_key = None

upload_key = None
if uploads:
    digest = hashlib.sha256()
    for uploaded in uploads:
        digest.update(uploaded.name.encode("utf-8"))
        digest.update(uploaded.getvalue())
    upload_key = (digest.hexdigest(), strategy)
    if st.session_state.index_key != upload_key:
        st.session_state.pop("rag_index", None)
        st.session_state.messages = []

if index_button and uploads:
    try:
        pages = []
        for uploaded in uploads:
            pages.extend(extract_pdf_pages(uploaded.getvalue(), uploaded.name))
        with st.spinner("Creating local embeddings and indexing the PDFs..."):
            st.session_state.rag_index = build_index(pages, strategy=strategy)
        st.session_state.index_key = upload_key
        st.success(f"Indexed {len(uploads)} PDF(s), {len(pages)} pages, "
                   f"{st.session_state.rag_index.chunk_count} chunks.")
    except Exception as exc:
        st.error(f"Could not index PDFs: {exc}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Retrieved evidence"):
                for source in message["sources"]:
                    st.markdown(f"**{source['citation']}**")
                    st.write(source["excerpt"])

if prompt := st.chat_input("Ask a question about the uploaded university documents"):
    if "rag_index" not in st.session_state or st.session_state.index_key != upload_key:
        st.warning("Upload PDFs and select **Index / refresh PDFs** first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching the uploaded PDFs and drafting a cited answer..."):
                try:
                    answer, sources = answer_question(st.session_state.rag_index, prompt, k=top_k)
                    st.markdown(answer)
                    source_rows = []
                    for i, doc in enumerate(sources, start=1):
                        citation = f"[S{i}] {doc.metadata.get('source', 'PDF')}, page {doc.metadata.get('page', '?')}"
                        source_rows.append({"citation": citation, "excerpt": doc.page_content})
                    with st.expander("Retrieved evidence"):
                        for row in source_rows:
                            st.markdown(f"**{row['citation']}**")
                            st.write(row["excerpt"])
                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": source_rows})
                except Exception as exc:
                    message = f"The local RAG service could not answer: {exc}"
                    st.error(message)
                    st.session_state.messages.append({"role": "assistant", "content": message})
