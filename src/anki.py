import os
import json
import csv
import io
from typing import List
from retrieve import initialize_chroma, search
from embed import generate_embedding
from summarize import call_llm_with_prompt
from format_template import CARD_FORMAT_PROMPT

def standardize_query_with_llm_anki(user_query: str) -> str:
    """
    用LLM标准化Anki卡片的查询，聚焦学习方向和知识点，生成更易用的卡片生成提示。
    """
    if not user_query or not isinstance(user_query, str):
        return ""
    prompt = (
        "You are an expert educational assistant for Anki card creation. "
        "Given the following user input, clarify the learning direction, focus, and main topic, and rewrite it as a clear, structured prompt suitable for generating high-quality Anki flashcards. "
        "Emphasize what should be learned and the key points. "
        "Output only the improved prompt for Anki card generation, nothing else.\n\n"
        f"User input:\n{user_query}\n\nAnki card prompt:"
    )
    improved_query = call_llm_with_prompt(prompt, model="gpt-4o-mini", max_tokens=300)
    return improved_query.strip()

def get_relevant_texts(
    query: str,
    project_folder: str,
    top_k: int = 10,
    relevance_threshold: float = 1.5
) -> List[str]:
    """
    根据 query 检索相关文本块（Chroma embedding），返回 chunk_text 列表。
    """
    chroma_db_folder = os.path.join(project_folder, "vectorstore", "chroma_db")
    chunks_folder = os.path.join(project_folder, "processed", "chunks")

    # 初始化 Chroma DB
    db = initialize_chroma(chroma_db_folder)
    results = search(query, top_k, db, relevance_threshold)

    # 汇总所有chunks内容（跨文件），只返回匹配chunk_id的chunk_text
    all_chunks = []
    for file in os.listdir(chunks_folder):
        if file.endswith("_chunks.json"):
            with open(os.path.join(chunks_folder, file), "r", encoding="utf-8") as f:
                all_chunks.extend(json.load(f))

    texts = []
    for result in results:
        chunk_id = result["chunk_id"]
        entry = next((entry for entry in all_chunks if entry.get("chunk_id") == chunk_id), None)
        if entry:
            text = entry.get("chunk_text", "")
            if text:
                texts.append(text)
    return texts

def build_prompt(
    query: str,
    card_type: str,
    difficulty: str,
    detail_level: str,
    num_cards: int,
    texts: List[str]
) -> str:
    """
    构建LLM prompt，包含用户参数和检索文本，格式模板引用外部文件。
    """
    context = "\n".join(texts)
    prompt = CARD_FORMAT_PROMPT.format(
        card_type=card_type,
        difficulty=difficulty,
        detail_level=detail_level,
        num_cards=num_cards,
        query=query,
        context=context
    )
    return prompt

def generate_anki_cards_llm(
    query: str,
    project_folder: str,
    card_type: str = "qa",
    difficulty: str = "intermediate",
    detail_level: str = "moderate",
    num_cards: int = 5,
    top_k: int = 10,
    relevance_threshold: float = 1.5
) -> str:
    """
    主函数：检索文本，构建prompt，调用LLM生成卡片，直接返回LLM原始输出。
    """
    texts = get_relevant_texts(query, project_folder, top_k, relevance_threshold)
    if not texts:
        raise ValueError("No relevant texts found for the given query and threshold.")
    prompt = build_prompt(query, card_type, difficulty, detail_level, num_cards, texts)
    llm_response = call_llm_with_prompt(prompt)
    return llm_response

def export_llm_cards_to_csv(
    llm_response: str,
    output_path: str
) -> str:
    """
    将LLM输出（表格形式）保存为csv文件。
    """
    import csv
    import io
    from datetime import datetime

    if not llm_response.strip():
        raise ValueError("LLM response is empty, nothing to export.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"anki_cards_{timestamp}.csv"
    filepath = os.path.join(output_path, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        reader = csv.reader(io.StringIO(llm_response))
        writer = csv.writer(f)
        for row in reader:
            writer.writerow(row)
    return filepath

def parse_csv_to_table(csv_content: str):
    """
    解析LLM生成的CSV文本为表格，便于预览。
    """
    reader = csv.reader(io.StringIO(csv_content))
    return [row for row in reader if any(cell.strip() for cell in row)]
