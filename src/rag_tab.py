# rag_tab.py
import os
import json
import streamlit as st
from preprocess import process_documents
from embed import create_or_update_embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

def render_rag_tab(PROJECTS_DIR):
    st.header("RAG: 项目与文件管理")

    # —— 项目选择与新建 —— 
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    idx = 1 if projects else 0
    selected = st.selectbox("选择项目：", ["新建项目"] + projects, index=idx, key="rag_project")

    if selected == "新建项目":
        nm = st.text_input("请输入新项目名称：")
        if st.button("创建项目") and nm:
            p = os.path.join(PROJECTS_DIR, nm)
            os.makedirs(os.path.join(p, "raw_pdfs"), exist_ok=True)
            os.makedirs(os.path.join(p, "processed", "chunks"), exist_ok=True)
            os.makedirs(os.path.join(p, "vectorstore", "chroma_db"), exist_ok=True)
            st.success(f"项目 '{nm}' 创建成功！")
            st.experimental_rerun()

    # 确保有已选项目
    if selected and selected != "新建项目":
        # 路径
        base        = os.path.join(PROJECTS_DIR, selected)
        raw_dir     = os.path.join(base, "raw_pdfs")
        proc_dir    = os.path.join(base, "processed")
        chunks_dir  = os.path.join(proc_dir, "chunks")
        db_dir      = os.path.join(base, "vectorstore", "chroma_db")
        manifest_fp = os.path.join(proc_dir, "manifest.json")

        # 确保目录
        for d in [raw_dir, chunks_dir, db_dir]:
            os.makedirs(d, exist_ok=True)

        # —— 步骤1：上传文件 —— 
        st.markdown("### 步骤1：上传文件")
        ups = st.file_uploader(
            "上传 PDF/MD/DOCX/XLSX/HTML",
            type=["pdf","md","docx","xlsx","html"], accept_multiple_files=True
        )
        new_files = []
        if ups:
            exist = set(os.listdir(raw_dir))
            for f in ups:
                if f.name in exist:
                    st.warning(f"'{f.name}' 已存在。")
                else:
                    with open(os.path.join(raw_dir, f.name), "wb") as fw:
                        fw.write(f.getbuffer())
                    new_files.append(f.name)
            if new_files:
                st.success("已上传: " + ", ".join(new_files))
            else:
                st.info("无新文件。")
        else:
            st.caption("请上传文件。")

        # —— 各类数据展示（仪表板） —— 
        st.divider()
        st.markdown("#### 当前分块 & 嵌入 状态")
        embed_model = os.getenv("EMBED_MODEL", "text-embedding-3-large")
        st.info(f"嵌入模型: **{embed_model}**")

        # chunks 数量
        chunk_count = sum(
            len(json.load(open(os.path.join(chunks_dir, fn), "r", encoding="utf-8")))
            for fn in os.listdir(chunks_dir) if fn.endswith("_chunks.json")
        )
        st.info(f"当前分块总数: **{chunk_count}**")

        # embeddings 数量
        try:
            db = Chroma(
                persist_directory=db_dir,
                embedding_function=OpenAIEmbeddings(model=embed_model),
                collection_name="literature_chunks"
            )
            embed_count = len(db._collection.get()["ids"])
        except:
            embed_count = 0
        st.info(f"当前 embeddings 数量: **{embed_count}**")

        # 进度条
        prog = (embed_count / chunk_count) if chunk_count else 0.0
        st.progress(prog, text="嵌入进度（已入库/分块）")

        # manifest 表格
        st.markdown("#### 📄 文件处理状态 (manifest)")
        if os.path.exists(manifest_fp):
            mf = json.load(open(manifest_fp, "r", encoding="utf-8"))
            rows = []
            for fn, m in mf.items():
                stem = os.path.splitext(fn)[0]
                rows.append({
                    "文件": fn,
                    "分块数": m.get("n_chunks", "-"),
                    "分块方式": m.get("chunk_method", "-"),  # 新增
                    "最后处理": m.get("last_processed", "-")
                })
            st.dataframe(
                rows,
                hide_index=True,
                use_container_width=True,
                height=350  # 固定高度，支持滚动
            )
        else:
            st.info("暂无 manifest.json，尚未预处理。")

        # —— 步骤2：预处理文件（分块） —— 
        st.divider()
        st.markdown("### 步骤2：预处理文件（分块）")

        method = st.selectbox("分块方式：", ["按句子","按段落","按页","固定长度"], index=0)
        if method == "固定长度":
            size = st.number_input("分块长度（字符）", min_value=50, max_value=2000, value=400, step=50)
        else:
            size = None

        force = st.checkbox(
            "强制全部重新预处理（忽略 hash，适用于参数变更或修复）",
            value=False
        )

        if st.button("开始预处理"):
            try:
                process_documents(
                    raw_dir,
                    proc_dir,
                    extract_tables=True,
                    extract_images=True,
                    extract_meta=True,
                    chunking_method=method,
                    chunk_size=size or 400,
                    chunk_overlap=50,
                    force_reprocess=force
                )
                st.success("预处理完成！")
                # 预处理后强制刷新 manifest 和计数
                if os.path.exists(manifest_fp):
                    mf = json.load(open(manifest_fp, "r", encoding="utf-8"))
                else:
                    mf = {}
                chunk_count = sum(
                    len(json.load(open(os.path.join(chunks_dir, fn), "r", encoding="utf-8")))
                    for fn in os.listdir(chunks_dir) if fn.endswith("_chunks.json")
                )
                try:
                    db = Chroma(
                        persist_directory=db_dir,
                        embedding_function=OpenAIEmbeddings(model=embed_model),
                        collection_name="literature_chunks"
                    )
                    embed_count = len(db._collection.get()["ids"])
                except:
                    embed_count = 0
                st.info(f"当前分块总数: **{chunk_count}**")
                st.info(f"当前 embeddings 数量: **{embed_count}**")
                prog = (embed_count / chunk_count) if chunk_count else 0.0
                st.progress(prog, text="嵌入进度（已入库/分块）")
                # 重新显示 manifest 表格（预处理后刷新）
                rows = []
                for fn, m in mf.items():
                    stem = os.path.splitext(fn)[0]
                    rows.append({
                        "文件": fn,
                        "分块数": m.get("n_chunks", "-"),
                        "分块方式": m.get("chunk_method", "-"),  # 新增
                        "最后处理": m.get("last_processed", "-")
                    })
                st.dataframe(
                    rows,
                    hide_index=True,
                    use_container_width=True,
                    height=350  # 固定高度，支持滚动
                )
            except Exception as e:
                st.error(f"预处理失败: {e}")

        # —— 步骤3：生成/更新嵌入 —— 
        st.divider()
        st.markdown("### 步骤3：生成/更新嵌入")
        mode = st.radio("嵌入方式：", ["全部重新嵌入","仅新增分块"], index=0)
        stems = {os.path.splitext(f)[0] for f in new_files}
        if st.button("生成嵌入"):
            duplicate_ids = []
            try:
                only = stems if mode.endswith("新增分块") else None
                try:
                    create_or_update_embeddings(chunks_dir, db_dir, only_files=only)
                    st.success("嵌入完成！")
                except ValueError as ve:
                    msg = str(ve)
                    if "Expected IDs to be unique" in msg:
                        # 提取重复ID
                        import re
                        dup_match = re.findall(r"found duplicates of: ([^ ]+)", msg)
                        duplicate_ids.extend(dup_match)
                        st.warning(f"检测到重复ID，已跳过: {', '.join(duplicate_ids)}")
                        print(f"[Embed] Duplicate IDs skipped: {duplicate_ids}")
                        st.info("部分分块因ID重复未被嵌入，其余已完成。")
                    else:
                        st.error(f"嵌入失败: {ve}")
                except Exception as e:
                    st.error(f"嵌入失败: {e}")
            except Exception as e:
                st.error(f"嵌入失败: {e}")

        # —— Manifest 健康检查 —— 
        st.divider()
        st.markdown("#### 📊 Manifest 健康检查")
        if os.path.exists(manifest_fp):
            mf = json.load(open(manifest_fp, "r", encoding="utf-8"))
            missing = [k for k, v in mf.items() if v.get("n_chunks", 0) == 0]
            if missing:
                st.warning(f"未生成分块的文件: {', '.join(missing)}")
            else:
                st.success("所有文件均已分块。")
