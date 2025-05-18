import os
import json
import streamlit as st
from preprocess import process_documents
from retrieve import initialize_chroma, search
from embed import create_or_update_embeddings, generate_embedding
from summarize import summarize_chunks, call_llm_with_prompt
from literature import (
    standardize_query,
    load_all_chunks,
    find_chunk_by_id,
    build_chunk_text,
)
from lang_utils import get_text  # 新增

@st.cache_data(show_spinner=False)
def cached_load_all_chunks(chunks_folder):
    from literature import load_all_chunks
    return load_all_chunks(chunks_folder)

def render_literature_tab(PROJECTS_DIR, lang):
    text = get_text(lang)["literature_tab"]

    st.header(text["header"])

    # Step 1: 项目选择
    st.markdown(text["step1_title"])
    st.info(text["step1_info"])
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    selected_project = st.selectbox(
        text["select_project"],
        options=projects,
        key="literature_project"
    )

    if not selected_project:
        st.warning(text["no_project"])
        return

    # 各路径
    project_path = os.path.join(PROJECTS_DIR, selected_project)
    chroma_db_folder = os.path.join(project_path, "vectorstore", "chroma_db")
    chunks_folder = os.path.join(project_path, "processed", "chunks")

    if not os.path.exists(chroma_db_folder):
        st.warning(text["no_db_warning"])
        return

    # 模型选择
    st.markdown("### " + text["select_model"])
    col_model, col_temp = st.columns([2,1])
    with col_temp:
        temperature = st.slider(
            text["temperature"],
            min_value=0.0, max_value=2.0, value=0.7, step=0.1,
            help=text["temp_help"]
        )
    with col_model:
        previous_model = st.session_state.get('selected_model', None)
        model_choice = st.radio(
            text["select_model"],
            options=text["model_options"],
            horizontal=True
        )
        # 当模型改变时，清除之前的优化结果
        if previous_model != model_choice:
            st.session_state['litrev_last_query'] = ""
            st.session_state['litrev_std_query'] = ""
            st.session_state['selected_model'] = model_choice
            print(f"[Model] Model changed from {previous_model} to {model_choice}, clearing cached queries")
        
        print(f"[Model] Using model: {model_choice}, temperature: {temperature}")

    # Step 2: 输入检索问题
    st.markdown(text["step2_title"])
    st.info(text["step2_info"])
    optimize_prompt = st.checkbox(text["optimize_prompt"], value=True)

    # 输入框和优化按钮布局
    query_col, btn_col = st.columns([9, 1])
    with query_col:
        query = st.text_input(text["query_input"])
    with btn_col:
        optimize_btn = st.button("🔄 " + (text["optimized_prompt"].split(":")[0] if optimize_prompt else text["run_retrieval"].split(":")[0]))

    std_query = ""
    if optimize_prompt:
        if query and optimize_btn:
            with st.spinner(text["optimizing"]):
                print(f"[Prompt] Optimizing query using {model_choice} model...")
                print(f"[Prompt] Original query: {query}")
                std_query = standardize_query(query, model=model_choice)
                print(f"[Prompt] Optimized query: {std_query}")
                st.session_state['litrev_last_query'] = query
                st.session_state['litrev_std_query'] = std_query
                st.session_state['selected_model'] = model_choice
        elif query:
            std_query = st.session_state.get('litrev_std_query', "")
    else:
        std_query = query
        
    # 显示优化结果
    if std_query and optimize_prompt:
        st.info(("🤖 " + text["optimized_prompt"].split(":")[0] + f" ({model_choice}):\n\n{std_query}") if lang == "English" else f"🤖 {text['optimized_prompt'].split(':')[0]}（{model_choice}）:\n\n{std_query}")

    # Step 3: 编辑摘要模板
    st.markdown(text["step3_title"])
    st.info(text["step3_info"])

    col1, col2 = st.columns(2)
    default_template_structured = text["default_structured"]
    default_template_direct = text["default_direct"]

    with col1:
        st.markdown(text["structured_review"])
        template_structured = st.text_area(text["structured_template"], default_template_structured, height=200, key="structured_template")
    with col2:
        st.markdown(text["direct_answer"])
        template_direct = st.text_area(text["direct_template"], default_template_direct, height=200, key="direct_template")

    template_option = st.radio(
        text["choose_template"],
        options=[text["structured"], text["direct"]],
        index=0,
        horizontal=True
    )
    custom_template = template_structured if template_option == text["structured"] else template_direct

    # Step 4: 检索参数设置与检索
    st.markdown(text["step4_title"])
    st.info(text["step4_info"])
    relevance_threshold = st.slider(
        text["relevance_threshold"],
        min_value=0.0, max_value=1.1, value=0.85, step=0.01,
        help=text["relevance_help"]
    )
    num_chunks = st.slider(text["num_chunks"], min_value=5, max_value=50, value=15)

    if std_query and st.button(text["run_retrieval"]):
        st.info(text["retrieving"])
        print(f"[INFO] search params: query={std_query}, top_k={num_chunks}, db={chroma_db_folder}, relevance_threshold={relevance_threshold}")
        db = initialize_chroma(chroma_db_folder)
        results = search(std_query, num_chunks, db, relevance_threshold)
        print(f"[INFO] search returned {len(results)} results")
        st.success(text["chunks_found"].format(n=len(results)))
        all_chunks = cached_load_all_chunks(chunks_folder)
        chunk_texts = []
        for result in results:
            chunk_id = result["chunk_id"]
            entry = find_chunk_by_id(all_chunks, chunk_id)
            if entry:
                chunk_texts.append(build_chunk_text(entry))
            else:
                chunk_texts.append({
                    "chunk_id": chunk_id,
                    "chunk_text": "[Not found]" if lang == "English" else "未找到",
                    "source": "unknown" if lang == "English" else "未知",
                    "doi": "",
                    "title": "",
                    "author": "",
                    "journal": "",
                    "year": "",
                    "keywords": ""
                })
        st.session_state.chunks = chunk_texts

    # Step 5: 生成摘要
    st.markdown(text["step5_title"])
    st.info(text["step5_info"])
    
    # tokens setting only
    max_tokens = st.number_input(
        text["max_tokens"],
        min_value=500, max_value=128000, value=3000, step=500,
        help=text["max_tokens_help"]
    )
    log_metrics = st.checkbox(text["log_metrics"])
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    if 'chunks' in st.session_state and st.button(text["generate_summary"]):
        chunks = st.session_state.chunks
        if chunks:
            st.info(text["summarizing"])
            dynamic_template = custom_template.format(context="{context}", query=std_query)
            basic_prompt = text["basic_prompt"].format(context="{context}", query=std_query, delimiter="#####")
            final_prompt = basic_prompt + dynamic_template
            summary, processing_time, token_consumption = summarize_chunks(
                chunks, final_prompt, model=model_choice, api_key=api_key,
                max_tokens=max_tokens, base_url=base_url, log_metrics=log_metrics, temperature=temperature
            )
            if summary:
                st.write(summary)
                if log_metrics:
                    st.write(text["show_time"].format(time=processing_time))
                    st.write(text["show_tokens"].format(tokens=token_consumption))
            else:
                st.warning(text["summary_fail"])
        else:
            st.warning(text["no_chunks"])
