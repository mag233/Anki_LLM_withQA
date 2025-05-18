import os
import json
from summarize import standardize_query_with_llm

def standardize_query(query, model=None):
    """Accepts optional model parameter to use specific model for query optimization"""
    if model:
        print(f"[Literature] Using {model} for query standardization")
    return standardize_query_with_llm(query, model=model)

def load_all_chunks(chunks_folder):
    """合并所有chunk文件，返回所有chunk的列表"""
    all_chunks = []
    for file in os.listdir(chunks_folder):
        if file.endswith("_chunks.json"):
            with open(os.path.join(chunks_folder, file), "r", encoding="utf-8") as f:
                all_chunks.extend(json.load(f))
    return all_chunks

def find_chunk_by_id(all_chunks, chunk_id):
    """根据chunk_id查找chunk内容"""
    entry = next((entry for entry in all_chunks if entry.get("chunk_id") == chunk_id), None)
    return entry

def build_chunk_text(entry):
    """根据chunk entry构建用于摘要的字典"""
    text = entry.get("chunk_text", "")
    if not text and "metadata" in entry and "text" in entry["metadata"]:
        text = entry["metadata"]["text"]
    meta = entry.get("metadata", {})
    return {
        "chunk_id": entry.get("chunk_id", ""),
        "chunk_text": text,
        "source": meta.get("source_file", meta.get("source", "unknown")),
        "doi": meta.get("doi", ""),
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "journal": meta.get("journal", ""),
        "year": meta.get("year", ""),
        "keywords": meta.get("keywords", "")
    }
