from pathlib import Path
import re
import logging
import sys
from langchain.document_loaders import (
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    TextLoader
)

# ——— 支持的文件类型及 Loader ———
SUPPORTED_EXTENSIONS = {
    ".pdf": PyMuPDFLoader,
    ".doc": UnstructuredWordDocumentLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".md": UnstructuredMarkdownLoader,
    ".markdown": UnstructuredMarkdownLoader,
    ".html": UnstructuredHTMLLoader,
    ".htm": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".text": TextLoader,
}

# ——— 日志配置：stderr INFO+；stdout DEBUG+ ———
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
for h in logger.handlers[:]:
    logger.removeHandler(h)

stderr_hdl = logging.StreamHandler(sys.stderr)
stderr_hdl.setLevel(logging.INFO)
stderr_hdl.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
logger.addHandler(stderr_hdl)

stdout_hdl = logging.StreamHandler(sys.stdout)
stdout_hdl.setLevel(logging.DEBUG)
stdout_hdl.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
logger.addHandler(stdout_hdl)
# ———————————————————————————————————————
def unify_spaces(text: str) -> str:
    """
    把各种空白都变成普通空格，然后压缩多空格。
    """
    # 1. 把常见的非 ASCII 空白都替换成普通空格
    #    U+3000 全角空格, U+00A0 不换行空格, U+2002–U+200A 各种窄空格
    text = text.replace('\u3000', ' ')
    text = text.replace('\u00A0', ' ')
    for cp in range(0x2002, 0x200B):
        text = text.replace(chr(cp), ' ')
    # 2. 将所有控制字符和罕见空白也替换为普通空格
    text = re.sub(r'[\t\v\f\u2028\u2029]', ' ', text)
    # 3. 最后把连续多个空格压成一个
    text = re.sub(r' {2,}', ' ', text)
    return text

def normalize_whitespace(text: str) -> str:
    """
    规范化各种空白和断行：
      1) 去掉全角空格、零宽空格等奇怪空白
      2) 合并超过 2 行换行为段落分隔
      3) 将非段落分隔的单换行替换为空格
      4) 把被断开的单词（word-\\nword）拼回
      5) 去掉每行首尾空白
      6) 把连续超过1个的空格合成1个
    """
    # 1) 删除全角空格、零宽空格
    text = text.replace('\u3000', ' ').replace('\u200b', '')
    # 2) 合并 3+ 连续换行为 2 行（保留段落分隔）
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 3) 非段落分隔的单换行 -> 空格
    text = re.sub(r'(?<!\n)(?<![。！？.!?])\n(?!\n)', ' ', text)
    # 4) 拼回被连字符拆分的单词
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # 5) 每行去除行首行尾空白
    lines = [ln.strip() for ln in text.split('\n')]
    # 6) 合并超过1个的普通空格
    lines = [re.sub(r' {2,}', ' ', ln) for ln in lines]
    return "\n".join(lines)


def remove_authors_from_intro(text: str) -> str:
    """
    删除开始的作者/单位信息：
      1) 匹配“前言”或“目录”行
      2) 否则匹配“Abstract”/“摘要”/“Introduction”
    """
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        if re.match(r'^\s*前言\b', line) or re.match(r'^\s*目\s*录\b', line):
            logging.debug(f"[Authors] 匹配到第{idx}行“{line.strip()}”，删除前{idx}行")
            return '\n'.join(lines[idx:])
    for idx, line in enumerate(lines):
        if re.search(r'\bAbstract\b|\b摘要\b|\bINTRODUCTION\b', line, re.IGNORECASE):
            logging.debug(f"[Authors] 匹配到第{idx}行“{line.strip()}”，删除前{idx}行")
            return '\n'.join(lines[idx:])
    logging.debug("[Authors] 未匹配到作者起点")
    return text

def remove_references_section(
    text: str,
    min_ref_lines: int = 1,
    max_nonmatch_lines: int = 7
) -> str:
    """
    删除尾部参考文献区块：
      - 连续匹配到至少 min_ref_lines 条参考行后才开始截断
      - 匹配模式覆盖多种格式
      - 遇到 max_nonmatch_lines 条连续非匹配后停止
    """
    lines = text.split('\n')
    n = len(lines)
    matched = nonmatch = 0
    boundary = n

    # 扩展后的参考文献行正则：包括数字编号、年份分号、doi/URL、以及“Author et al.” 样式
    ref_re = re.compile(
    r"""(?x) ^\s*
    (?:
      \[\d+\]                         # [123]
    | \[J\]\.?                        # [J] 或 [J].
    | \[M\]\.?                        # [M] 或 [M].
    | \d{1,4}[\.）]\s+                # 123. 或 123)
    | \d{4}(?:年|;)\s*\d+             # 2020年22 或 2020;22
    | \d{4}[:,]\d{1,4}                # 2015:1234 或 2015,1234
    | doi[:：]\S+                     # doi:10.1000/xyz 或 doi：…
    | https?://\S+                    # http://...
    | [A-Za-z]{2,}(?:[A-Za-z0-9\-,']+),   # LindholmLH,CarlbergB,
    | [A-Z][A-Za-z0-9\-\’&, ]{10,}\.\s+[A-Z]  
        # Sprint Research Group. Randomized…
    | [\u4e00-\u9fa5]{2,}(?:,|，|、).{5,}?[\.。]\s*[\u4e00-\u9fa5A-Za-z]
        # 王继光,谢良地,牟建军,等.独特… 标式
    | .+?,\s*\d{4},\s*\d{1,4}:\d{1,5}(?:-\d{1,5})?  
        # 期刊名,YYYY,Vol:Pages(-Pages)
    )
    """,
    re.IGNORECASE
)




    logging.debug(f"[Refs] 文本共 {n} 行，开始自底向上扫描")
    for i in range(n - 1, -1, -1):
        line = lines[i]
        if ref_re.match(line):
            matched += 1
            nonmatch = 0
            logging.debug(f"[Refs] 匹配条目#{matched}: {line.strip()!r}")
            if matched >= min_ref_lines:
                boundary = i
        else:
            if matched >= min_ref_lines:
                nonmatch += 1
                logging.debug(f"[Refs] 非匹配#{nonmatch}: {line.strip()!r}")
                if nonmatch >= max_nonmatch_lines:
                    boundary = i + nonmatch
                    logging.debug(f"[Refs] 停止删除 at 行 {boundary}")
                    break
            # 尚未达到 min_ref_lines，继续向前扫描

    if boundary < n:
        logging.debug(f"[Refs] 删除行区间 [{boundary}, {n}) 共 {n - boundary} 行")
        return '\n'.join(lines[:boundary])
    else:
        logging.debug("[Refs] 未检测到符合要求的参考文献区块")
        return text

def clean_text_pipeline(text: str) -> str:
    logging.debug("=== 开始清洗管道 ===")
    text = unify_spaces(text)
    text = normalize_whitespace(text)
    text = remove_authors_from_intro(text)
    before = len(text.split('\n'))
    text = remove_references_section(text, min_ref_lines=2, max_nonmatch_lines=7)
    after = len(text.split('\n'))
    logging.debug(f"[Clean] 行数 {before} → {after}")
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\(\s*\d+\s*\)', '', text)
    text = re.sub(r'(?P<t>.+?)\s+\d{1,2}(?=[\.,]?$)', r'\1', text)
    logging.debug("[Clean] 脚注角标清洗完成")
    text = re.sub(r'^\s*(Page\s*\d+|第\s*\d+\s*页|\d+)\s*$',
                  '', text, flags=re.MULTILINE)
    logging.debug("[Clean] 页码行清洗完成")
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = '\n'.join([l for l in text.split('\n') if l.strip()])
    logging.debug("[Clean] 空行清洗完成")
    logging.debug("=== 清洗管道结束 ===")
    return text.strip()

def extract_documents_text(
    raw_dir: str = "raw_docs",
    extracted_folder: str = "output/extracted"
):
    raw_path = Path(raw_dir)
    out_path = Path(extracted_folder)
    out_path.mkdir(parents=True, exist_ok=True)

    for file in sorted(raw_path.iterdir()):
        logging.info(f"[Extract] 处理：{file.name}")
        ext = file.suffix.lower()
        loader_cls = SUPPORTED_EXTENSIONS.get(ext)
        if not loader_cls:
            logging.warning(f"[Extract] 跳过不支持：{file.name}")
            continue

        try:
            docs = loader_cls(str(file)).load()
        except Exception as e:
            logging.error(f"[Extract] 加载失败 {file.name}：{e}")
            continue

        merged = "\n".join(doc.page_content for doc in docs)
        logging.debug(f"[Extract] 合并长度：{len(merged)} 字符")
        cleaned = clean_text_pipeline(merged)

        out_file = out_path / f"{file.stem}.txt"
        out_file.write_text(cleaned, encoding="utf-8")
        logging.info(f"[Extract] 写出：{out_file}")
