# Import required libraries
import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from lang_utils import get_text  # ✅ 多语言模块

# Load environment variables
load_dotenv()

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #the parent directory of src
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Streamlit page config
st.set_page_config(
    page_title="LLM Paper Analysis Suite",
    page_icon="📚",
    layout="wide"
)

# ================= ✅ UI 样式优化 =================
st.markdown(
    """
    <style>
    html, body, .main {
        font-family: "Helvetica", sans-serif;
        background-color: #f7f9fc;
    }
    .stApp {
        max-width: 1400px;
        margin: auto;
        padding-top: 1rem;
    }
    
    /* 隐藏 Expander/Collapsible 箭头 */
    [data-testid="collapsedControl"] { display: none !important; }
    /* 隐藏全局 Sidebar Toggle 按钮 */
    button[aria-label="Toggle sidebar"],
    button[data-testid="sidebarToggle"] { display: none !important; }
    /* 如果你想默认折叠侧边栏 */
    .css-18e3th9 { visibility: hidden !important; }

    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.05rem;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        margin-right: 0.5rem;
        border-radius: 0.6rem 0.6rem 0 0;
        background-color: #e3eaf4;
        color: #1f1f1f;
        border: none;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(90deg, #8ec5fc 0%, #e0c3fc 100%);
        color: #000;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff;
        border-radius: 0 0 0.6rem 0.6rem;
        padding: 2rem 2rem 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= ✅ LOGO与语言切换 =================
# 使用三列布局，logo放中间
col1, col_logo, col_lang = st.columns([2,4,1])

with col_logo:
    logo_path = os.path.join(PROJECT_ROOT, "assets/logo.png")
    st.image(logo_path, width=400)
with col_lang:
    lang = st.selectbox(
        label="",  # 不显示 label，只显示下拉箭头
        options=["English", "中文"],
        key="lang_select",
        help="切换中英文界面"
    )
text = get_text(lang)


# ================= ✅ 顶部标题区块 =================
if lang == "中文":
    html = """
<div style="display:flex;align-items:center;gap:1.2rem;margin:1rem 0 2rem 0;">
  
  <div>
    <div style="font-size:2.1rem;font-weight:700;">📚 LLM-RAG学习工具</div>
    <div style="font-size:1.05rem;color:#555;">
      一个整合文献阅读、智能问答与卡片复习的学习助手
    </div>
  </div>
</div>
    """
    st.markdown(html, unsafe_allow_html=True)
else:
    html = """
<div style="display:flex;align-items:center;gap:1.2rem;margin:1rem 0 2rem 0;">
  <div>
    <div style="font-size:2.1rem;font-weight:700;">📚 LLM-RAG Learning Kit</div>
    <div style="font-size:1.05rem;color:#555;">
      An intelligent assistant for literature review, Q&A, and spaced repetition
    </div>
  </div>
</div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ================= ✅ 标签加载与传参 =================
if "tab_funcs" not in st.session_state:
    from rag_tab import render_rag_tab
    from literature_tab import render_literature_tab
    from anki_tab import render_anki_tab
    st.session_state.tab_funcs = [
        render_rag_tab,
        render_literature_tab,
        render_anki_tab
    ]

tab_labels = [
    text["tab_titles"]["RAG"],
    text["tab_titles"]["Literature"],
    text["tab_titles"]["Anki"]
]

tabs = st.tabs(tab_labels)
for i, tab in enumerate(tabs):
    with tab:
        st.session_state.tab_funcs[i](PROJECTS_DIR, lang)
