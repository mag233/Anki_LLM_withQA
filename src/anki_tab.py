import os
import streamlit as st
from anki import (
    standardize_query_with_llm_anki,
    generate_anki_cards_llm,
    export_llm_cards_to_csv,
    parse_csv_to_table,
)

def render_anki_tab(PROJECTS_DIR):
    st.header("Generate Anki Cards")

    # 1. 读取所有项目
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    if not projects:
        st.warning("No projects found. Please create a project in the Literature Analysis tab first.")
        return

    selected_project = st.selectbox(
        "Select Project for Cards:",
        options=projects,
        help="Choose the project containing the documents you want to create cards from"
    )
    if not selected_project:
        st.warning("Please select a project")
        return

    project_path = os.path.join(PROJECTS_DIR, selected_project)
    chunks_folder = os.path.join(project_path, "processed", "chunks")
    chroma_db_folder = os.path.join(project_path, "vectorstore", "chroma_db")

    if not (os.path.isdir(chunks_folder) and os.path.isdir(chroma_db_folder)):
        st.warning("Please preprocess and embed documents in this project first (see RAG tab).")
        return

    st.info("Using LLM for high-quality card generation")

    col1, col2 = st.columns(2)
    with col1:
        card_type = st.radio(
            "Card Type:",
            ["Q&A", "Cloze"],
            help="Q&A creates question-answer pairs, Cloze creates fill-in-the-blank style cards"
        ).lower()
        num_cards = st.slider(
            "Number of Cards:",
            1, 25, 5,
            help="How many cards to generate"
        )
    with col2:
        difficulty = st.select_slider(
            "Difficulty:",
            ["beginner", "intermediate", "advanced", "expert"],
            value="intermediate",
            help="Adjusts the complexity level of the generated cards"
        )
        detail_level = st.select_slider(
            "Detail Level:",
            ["basic", "moderate", "detailed", "comprehensive"],
            value="moderate",
            help="Controls how much information to include in each card"
        )

    query = st.text_area(
        "Enter your query:",
        help="Enter the topic or concept you want to create cards for. The system will find relevant content from your documents."
    )

    std_query = ""
    if query and st.session_state.get("anki_last_query") != query:
        std_query = standardize_query_with_llm_anki(query)
        st.session_state["anki_last_query"] = query
        st.session_state["anki_std_query"] = std_query
    elif query:
        std_query = st.session_state.get("anki_std_query", "")

    col_k, col_rel = st.columns(2)
    with col_k:
        top_k = st.slider(
            "Top-K Chunks to Retrieve:",
            min_value=5, max_value=50, value=10,
            help="How many relevant chunks to retrieve for card generation"
        )
    with col_rel:
        relevance_threshold = st.slider(
            "Minimum Similarity Score (Relevance Threshold):",
            min_value=0.0, max_value=1.1, value=0.85, step=0.01,
            help="Higher values mean stricter match (more similar). If you get no results, try lowering this value."
        )

    if st.button("Retrieve Relevant Chunks"):
        if not std_query:
            st.warning("Please enter a query first")
            return
        from retrieve import initialize_chroma, search
        db = initialize_chroma(chroma_db_folder)
        results = search(std_query, top_k, db, relevance_threshold)
        st.session_state["anki_retrieved_chunks"] = results
        st.info(f"Retrieved {len(results)} relevant chunks.")
        if results:
            for i, chunk in enumerate(results[:5]):
                st.markdown(f"**Chunk {i+1}:** {chunk.get('source','')}")
                st.code(chunk.get("chunk_id", ""))
                st.text(chunk.get("distance", ""))
        else:
            st.info("No relevant chunks found. Try lowering the threshold or increasing Top-K.")

    if st.button("Generate Cards"):
        retrieved_chunks = st.session_state.get("anki_retrieved_chunks", [])
        if not std_query:
            st.warning("Please enter a query first")
            return
        if not retrieved_chunks:
            st.warning("Please retrieve relevant chunks first")
            return
        try:
            with st.spinner("Generating cards..."):
                llm_response = generate_anki_cards_llm(
                    query=std_query,
                    project_folder=project_path,
                    card_type=card_type,
                    difficulty=difficulty,
                    detail_level=detail_level,
                    num_cards=num_cards,
                    top_k=top_k,
                    relevance_threshold=relevance_threshold
                )
                st.subheader("LLM Output (CSV format):")
                rows = parse_csv_to_table(llm_response)
                if rows:
                    st.table(rows)
                else:
                    st.info("No content to preview.")

                st.session_state["anki_llm_response"] = llm_response
        except Exception as e:
            st.error(f"Error generating cards: {e}")

    llm_response = st.session_state.get("anki_llm_response", "")
    if llm_response:
        if st.button("Export to CSV"):
            output_path = os.path.join(project_path, "anki_cards")
            os.makedirs(output_path, exist_ok=True)
            csv_path = export_llm_cards_to_csv(llm_response, output_path)
            st.success(f"CSV file saved to: {csv_path}")
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            st.download_button(
                "Download Cards",
                csv_data,
                file_name=os.path.basename(csv_path),
                mime='text/csv'
            )
