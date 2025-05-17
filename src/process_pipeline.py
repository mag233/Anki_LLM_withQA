import os
import json
import streamlit as st
from preprocess import preprocess_pdfs
from embed import create_embeddings
from retrieve import search
from summarize import summarize_chunks

# Paths for processing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploaded_pdfs")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed_data")
EMBEDDINGS_FILE = os.path.join(PROCESSED_FOLDER, "embeddings.npy")
METADATA_FILE = os.path.join(PROCESSED_FOLDER, "metadata.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Streamlit UI
st.title("LLM Pipeline with Midpoint (Embeddings)")

# Step 1: Preprocessing PDFs
st.header("Step 1: Preprocessing PDFs")
uploaded_files = st.file_uploader("Upload PDFs:", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
    st.success(f"Uploaded {len(uploaded_files)} PDF(s).")

if st.button("Run Preprocessing"):
    st.info("Preprocessing PDFs...")
    preprocess_pdfs(UPLOAD_FOLDER, PROCESSED_FOLDER)
    st.success("Preprocessing complete! Chunks saved.")

# Step 2: Embedding Generation
st.header("Step 2: Generate Embeddings")
if st.button("Generate Embeddings"):
    processed_file = os.path.join(PROCESSED_FOLDER, "processed_chunks.json")
    st.info("Generating embeddings...")
    create_embeddings(processed_file, EMBEDDINGS_FILE, METADATA_FILE)
    st.success("Embeddings generated and saved!")

# Step 3: Query for Retrieval and Summarization
st.header("Step 3: Query and Summarization")
query = st.text_input("Enter your query:")

if query and st.button("Run Retrieval and Summarization"):
    st.info("Retrieving relevant chunks...")
    top_k = 5
    results = search(query, top_k=top_k)

    # Load metadata to fetch chunk text
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    chunks = []
    for result in results:
        chunk_id = result["chunk_id"]
        for entry in metadata:
            if entry["chunk_id"] == chunk_id:
                chunks.append({"chunk_text": entry["chunk_text"]})
                break

    # Summarize retrieved chunks
    st.info("Summarizing retrieved chunks...")
    prompt_template = (
        "You are given the following excerpts from research papers:\n\n"
        "{context}\n\n"
        "Please create a structured literature review with the following sections:\n"
        "1. Introduction\n"
        "2. Key Findings\n"
        "3. Challenges\n"
        "4. Future Directions\n"
        "Ensure each section is concise and captures the main points from the excerpts."
    )
    if chunks:
        summary = summarize_chunks(chunks, prompt_template)
        st.success("Summarization complete!")
        st.text_area("Generated Summary", summary, height=300)
    else:
        st.warning("No relevant chunks found for the query.")
