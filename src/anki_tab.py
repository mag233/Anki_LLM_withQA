import os
import streamlit as st
from anki import (
    standardize_query_with_llm_anki,
    generate_anki_cards_llm,
    export_llm_cards_to_csv,
    parse_csv_to_table,
)
from lang_utils import get_text  # 新增

def render_anki_tab(PROJECTS_DIR, lang):
    text = get_text(lang)["anki_tab"]

    st.header(text["header"])

    # 1. 读取所有项目
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    if not projects:
        st.warning(text["no_projects"])
        return

    selected_project = st.selectbox(
        text["select_project"],
        options=projects,
        help=text["select_project_help"]
    )
    if not selected_project:
        st.warning(text["please_select_project"])
        return

    project_path = os.path.join(PROJECTS_DIR, selected_project)
    chunks_folder = os.path.join(project_path, "processed", "chunks")
    chroma_db_folder = os.path.join(project_path, "vectorstore", "chroma_db")

    if not (os.path.isdir(chunks_folder) and os.path.isdir(chroma_db_folder)):
        st.warning(text["preprocess_warning"])
        return

    st.info(text["using_llm"])

    col1, col2 = st.columns(2)
    with col1:
        card_type = st.radio(
            text["card_type"],
            [text["qa"], text["cloze"]],
            help=text["card_type_help"]
        ).lower()
        num_cards = st.slider(
            text["num_cards"],
            1, 25, 5,
            help=text["num_cards_help"]
        )
    with col2:
        difficulty = st.select_slider(
            text["difficulty"],
            text["difficulty_options"],
            value=text["difficulty_default"],
            help=text["difficulty_help"]
        )
        detail_level = st.select_slider(
            text["detail_level"],
            text["detail_level_options"],
            value=text["detail_level_default"],
            help=text["detail_level_help"]
        )

    query = st.text_area(
        text["query_input"],
        help=text["query_help"]
    )

    # 新增：prompt优化可选
    optimize_prompt = st.checkbox("优化检索意图（Prompt Optimization）", value=True)

    std_query = ""
    if query and st.session_state.get("anki_last_query") != query:
        std_query = standardize_query_with_llm_anki(query, optimize=optimize_prompt)
        st.session_state["anki_last_query"] = query
        st.session_state["anki_std_query"] = std_query
        st.session_state["anki_optimize_prompt"] = optimize_prompt
    elif query:
        std_query = st.session_state.get("anki_std_query", "")
        optimize_prompt = st.session_state.get("anki_optimize_prompt", True)

    col_k, col_rel = st.columns(2)
    with col_k:
        top_k = st.slider(
            text["top_k"],
            min_value=5, max_value=50, value=10,
            help=text["top_k_help"]
        )
    with col_rel:
        relevance_threshold = st.slider(
            text["relevance_threshold"],
            min_value=0.0, max_value=1.1, value=0.85, step=0.01,
            help=text["relevance_threshold_help"]
        )

    if st.button(text["retrieve_chunks"]):
        if not std_query:
            st.warning(text["please_enter_query"])
            return
        # 新增：打印优化后的标准化query
        st.info(f"标准化检索意图（Standardized Query）: {std_query}")
        from retrieve import initialize_chroma, search
        db = initialize_chroma(chroma_db_folder)
        results = search(std_query, top_k, db, relevance_threshold)
        st.session_state["anki_retrieved_chunks"] = results
        st.info(text["chunks_retrieved"].format(n=len(results)))
        # 新增：检索完成提示
        st.success("检索完成！")
        if results:
            for i, chunk in enumerate(results[:5]):
                st.markdown(text["chunk_id"].format(idx=i+1, src=chunk.get('source', '')))
                st.code(chunk.get("chunk_id", ""))
                st.text(chunk.get("distance", ""))
        else:
            st.info(text["no_chunks_found"])

    if st.button(text["generate_cards"]):
        retrieved_chunks = st.session_state.get("anki_retrieved_chunks", [])
        if not std_query:
            st.warning(text["please_enter_query"])
            return
        if not retrieved_chunks:
            st.warning(text["please_retrieve_chunks"])
            return
        try:
            with st.spinner(text["generating_cards"]):
                llm_response = generate_anki_cards_llm(
                    query=std_query,
                    project_folder=project_path,
                    card_type=card_type,
                    difficulty=difficulty,
                    detail_level=detail_level,
                    num_cards=num_cards,
                    top_k=top_k,
                    relevance_threshold=relevance_threshold,
                    optimize_prompt=optimize_prompt
                )
                st.subheader(text["llm_output"])
                rows = parse_csv_to_table(llm_response)
                if rows:
                    st.table(rows)
                else:
                    st.info(text["no_content_preview"])

                st.session_state["anki_llm_response"] = llm_response
        except Exception as e:
            st.error(text["error_generating"].format(err=e))

    llm_response = st.session_state.get("anki_llm_response", "")
    if llm_response:
        if st.button(text["export_csv"]):
            output_path = os.path.join(project_path, "anki_cards")
            os.makedirs(output_path, exist_ok=True)
            csv_path = export_llm_cards_to_csv(llm_response, output_path)
            st.success(text["csv_saved"].format(path=csv_path))
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            st.download_button(
                text["download_cards"],
                csv_data,
                file_name=os.path.basename(csv_path),
                mime='text/csv'
            )
