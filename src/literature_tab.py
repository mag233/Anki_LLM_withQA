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

# 缓存chunks读取
@st.cache_data(show_spinner=False)
def cached_load_all_chunks(chunks_folder):
    from literature import load_all_chunks
    return load_all_chunks(chunks_folder)

def render_literature_tab(PROJECTS_DIR):
    st.header("Literature Review & QA")

    # Step 1: 项目选择
    st.markdown("### Step 1: Select Project")
    st.info("Select a project to perform literature review and QA. Please make sure you have already uploaded and processed your PDFs in the RAG tab.")
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    selected_project = st.selectbox(
        "Select Project for Literature Review:",
        options=projects,
        key="literature_project"
    )

    if not selected_project:
        st.warning("Please select a project")
        return

    # 各路径
    project_path = os.path.join(PROJECTS_DIR, selected_project)
    chroma_db_folder = os.path.join(project_path, "vectorstore", "chroma_db")
    chunks_folder = os.path.join(project_path, "processed", "chunks")

    # 检查数据库文件夹
    if not os.path.exists(chroma_db_folder):
        st.warning("Please generate embeddings for this project first (see RAG tab).")
        return

    # Step 2: 输入检索问题
    st.markdown("### Step 2: Enter Your Query")
    st.info("Describe your research question or information need. The system will help you standardize and optimize your query for better retrieval.")
    optimize_prompt = st.checkbox("进行检索意图优化（Prompt Optimization）", value=True)
    if 'litrev_last_query' not in st.session_state:
        st.session_state['litrev_last_query'] = ""
    if 'litrev_std_query' not in st.session_state:
        st.session_state['litrev_std_query'] = ""
    query = st.text_input("Enter Your Query:")

    std_query = ""
    if optimize_prompt:
        # 只在query变化时调用LLM优化
        if query and st.session_state['litrev_last_query'] != query:
            with st.spinner("正在优化检索意图（Prompt Optimization in progress）..."):
                std_query = standardize_query(query)
            st.session_state['litrev_last_query'] = query
            st.session_state['litrev_std_query'] = std_query
        elif query:
            std_query = st.session_state['litrev_std_query']
        if std_query:
            st.info(f"优化后的检索意图（Optimized Prompt）: {std_query}")
    else:
        std_query = query

    # Step 3: 编辑摘要模板
    st.markdown("### Step 3: Customize Summarization Template")
    st.info("You can customize the output format for the summary. The template supports sections and academic writing style.")

    col1, col2 = st.columns(2)
    default_template_structured = """Provide a summary with the following sections:
1. Introduction
2. Key Findings
3. Challenges
4. Future Directions
5. Conclusion
6. Key data or Examples
7. References
"""
    default_template_direct = """Provide a direct, concise answer to the query above, using only the information from the context. 
If the answer is not explicitly available, say "Not enough information in the provided context."
"""

    with col1:
        st.markdown("**Structured Literature Review**")
        template_structured = st.text_area("Structured Template", default_template_structured, height=200, key="structured_template")
    with col2:
        st.markdown("**Direct Answer**")
        template_direct = st.text_area("Direct Answer Template", default_template_direct, height=200, key="direct_template")

    # 用户选择使用哪个模板
    template_option = st.radio(
        "Choose summary template style:",
        options=["Structured", "Direct Answer"],
        index=0,
        horizontal=True
    )
    custom_template = template_structured if template_option == "Structured" else template_direct

    # Step 4: 检索参数设置与检索
    st.markdown("### Step 4: Retrieval Settings & Run Retrieval")
    st.info("Adjust the retrieval parameters. If you get no results, try increasing the maximum distance threshold.")
    relevance_threshold = st.slider(
        "Set Minimum Similarity Score (Relevance Threshold):",
        min_value=0.0, max_value=1.1, value=0.85, step=0.01,
        help="Higher values mean stricter match (more similar). If you get no results, try lowering this value."
    )
    num_chunks = st.slider("Select Number of Chunks to Retrieve:", min_value=5, max_value=50, value=15)

    # 检索操作
    if std_query and st.button("Run Retrieval"):
        st.info("Retrieving relevant chunks...")
        print(f"[INFO] search params: query={std_query}, top_k={num_chunks}, db={chroma_db_folder}, relevance_threshold={relevance_threshold}")
        db = initialize_chroma(chroma_db_folder)
        results = search(std_query, num_chunks, db, relevance_threshold)
        print(f"[INFO] search returned {len(results)} results")
        st.success(str(len(results)) + " Chunks Found")
        # 只在按钮点击时读取chunks
        all_chunks = cached_load_all_chunks(chunks_folder)
        # 查找匹配
        chunk_texts = []
        for result in results:
            chunk_id = result["chunk_id"]
            entry = find_chunk_by_id(all_chunks, chunk_id)
            if entry:
                chunk_texts.append(build_chunk_text(entry))
            else:
                chunk_texts.append({
                    "chunk_id": chunk_id,
                    "chunk_text": "[Not found]",
                    "source": "unknown",
                    "doi": "",
                    "title": "",
                    "author": "",
                    "journal": "",
                    "year": "",
                    "keywords": ""
                })
        st.session_state.chunks = chunk_texts

    # Step 5: 生成摘要
    st.markdown("### Step 5: Summarize Retrieved Chunks")
    st.info("Generate a structured summary based on the retrieved content and your template.")
    model_choice = st.radio(
        "Select Model:",
        options=[
            "gpt-4o",
            "gpt-4o-mini"
        ]
    )
    col_temp, col_tokens = st.columns(2)
    with col_temp:
        temperature = st.slider(
            "Temperature (Creativity):",
            min_value=0.0, max_value=2.0, value=0.7, step=0.1,
            help="Higher values produce more creative output. Typical range: 0.2~1.0"
        )
    with col_tokens:
        max_tokens = st.number_input(
            "Max Tokens:",
            min_value=500, max_value=128000, value=3000, step=500,
            help="Maximum number of tokens in the summary output."
        )
    log_metrics = st.checkbox("Log Token Consumption and Processing Time")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    if 'chunks' in st.session_state and st.button("Generate Summary"):
        chunks = st.session_state.chunks
        if chunks:
            st.info("Summarizing Retrieved Chunks...")
            # 动态拼接prompt
            dynamic_template = custom_template.format(context="{context}", query=std_query)
            basic_prompt = """You are given the following excerpts from research papers:

{context}

And here is the query you want to summarize, use only the information in the context.
Generate reference according formal academic writing style [Chicago style], include DOI whenever available.
#####{query}#####
"""
            final_prompt = basic_prompt.format(context="{context}", query=std_query, delimiter="#####") + dynamic_template
            summary, processing_time, token_consumption = summarize_chunks(
                chunks, final_prompt, model=model_choice, api_key=api_key,
                max_tokens=max_tokens, base_url=base_url, log_metrics=log_metrics, temperature=temperature
            )
            if summary:
                st.write(summary)
                if log_metrics:
                    st.write(f"Processing Time: {processing_time} seconds")
                    st.write(f"Total Tokens: {token_consumption}")
            else:
                st.warning("Summary generation failed, please check your input and template.")
        else:
            st.warning("No chunks found for summarization. Please run retrieval first.")

