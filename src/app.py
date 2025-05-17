# Import required libraries
import os  # Operating system interface for file/directory operations
from dotenv import load_dotenv  # Load environment variables from .env file
import streamlit as st  # Web app framework for data apps

# Load environment variables (API keys, model settings, etc.)
load_dotenv()

# Setup application directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory containing this script
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")  # Define projects directory path
os.makedirs(PROJECTS_DIR, exist_ok=True)  # Create projects directory if it doesn't exist

# Streamlit page config and style
st.set_page_config(
    page_title="LLM Paper Analysis Suite",
    page_icon="📚",
    layout="wide"
)
st.markdown(
    """
    <style>
    .main {background-color: #f8f9fa;}
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        padding: 0.5rem 1.5rem;
        margin-right: 0.5rem;
        border-radius: 0.5rem 0.5rem 0 0;
        background-color: #e9ecef;
        color: #222;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%);
        color: #222;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #fff;
        border-radius: 0 0 0.5rem 0.5rem;
        padding: 2rem 2rem 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
        <span style="font-size:2.2rem;">📚 <b>LLM Paper Analysis Suite</b></span>
        <span style="font-size:1.1rem;color:#666;">Your all-in-one tool for literature review, RAG, and Anki card generation</span>
    </div>
    """,
    unsafe_allow_html=True
)

# 推荐做法：只在 app 启动时全局 import，所有 tab 共享
from langchain_community.embeddings import OpenAIEmbeddings

# 只在首次加载时 import 各 tab，避免每次切换重复 import
if "tab_funcs" not in st.session_state:
    from rag_tab import render_rag_tab
    from literature_tab import render_literature_tab
    from anki_tab import render_anki_tab
    st.session_state.tab_funcs = [
        render_rag_tab,
        render_literature_tab,
        render_anki_tab
    ]

tab_labels = ["RAG", "Literature Review PLUS Database Q&A", "Anki Cards"]
selected = st.tabs(tab_labels)

for i, tab in enumerate(selected):
    with tab:
        st.session_state.tab_funcs[i](PROJECTS_DIR)