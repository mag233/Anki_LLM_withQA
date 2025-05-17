# Import required libraries
import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from lang_utils import get_text  # ✅ 新增语言模块

# Load environment variables
load_dotenv()

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Streamlit page config
st.set_page_config(
    page_title="LLM Paper Analysis Suite",
    page_icon="📚",
    layout="wide"
)

# Load and show logo
logo_path = os.path.join(BASE_DIR, "logo.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=200)

# Language selector
lang = st.sidebar.selectbox("🌐 Language / 语言", ["English", "中文"])
text = get_text(lang)  # ✅ 获取语言字典

# Style and Title
st.markdown(
    '''
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
    ''',
    unsafe_allow_html=True
)

# 标题部分不变，仅条件显示
if lang == "中文":
    st.markdown(
        '''
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
            <span style="font-size:2.2rem;">📚 <b>LLM 论文分析套件</b></span>
            <span style="font-size:1.1rem;color:#666;">集文献综述、问答与 Anki 卡片于一体的学习助手</span>
        </div>
        ''',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '''
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
            <span style="font-size:2.2rem;">📚 <b>LLM Paper Analysis Suite</b></span>
            <span style="font-size:1.1rem;color:#666;">Your all-in-one tool for literature review, RAG, and Anki card generation</span>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Lazy load tabs only on first load
if "tab_funcs" not in st.session_state:
    from rag_tab import render_rag_tab
    from literature_tab import render_literature_tab
    from anki_tab import render_anki_tab
    st.session_state.tab_funcs = [
        render_rag_tab,
        render_literature_tab,
        render_anki_tab
    ]

# ✅ 替换 tab_labels 为统一语言控制
tab_labels = [
    text["tab_titles"]["RAG"],
    text["tab_titles"]["Literature"],
    text["tab_titles"]["Anki"]
]

selected = st.tabs(tab_labels)
for i, tab in enumerate(selected):
    with tab:
        st.session_state.tab_funcs[i](PROJECTS_DIR, lang)  # ✅ 传递 lang 参数
