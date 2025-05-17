import openai # type: ignore
import os
import time

# Set custom base URL if needed
base_url = "https://xiaoai.plus/v1"
api_key =  os.getenv("OPENAI_API_KEY")

#client = openai.OpenAI(api_key=openai.api_key, base_url=openai.base_url)

def standardize_query_with_llm(user_query: str) -> str:
    """
    Use LLM to standardize and structure the user's query.
    This will keep the user's idea but turn it into a clear, structured question.
    """
    if not user_query or not isinstance(user_query, str):
        return ""
    prompt = (
        "You are an academic assistant. "
        "Given the following user input, rewrite it as a clear, structured, and specific question or query. "
        "Keep the user's original intent and important details. "
        "Output only the improved query, nothing else.\n\n"
        f"User input:\n{user_query}\n\nImproved query:"
    )
    improved_query = call_llm_with_prompt(prompt, model="gpt-4o-mini", max_tokens=300)
    print("==== Standardized Query by LLM ====")
    print(improved_query)
    return improved_query.strip()

def summarize_chunks(chunks,
                     prompt_template,
    model="gpt-4o-mini",
    api_key=None,
    max_tokens=12800,
    base_url="https://api.openai.com/v1",
    log_metrics=False,
    temperature=0.8):

    # Defensive: skip empty chunks
    if not chunks or not isinstance(chunks, list):
        print("No chunks provided for summarization.")
        return None, None, None

    # 过滤掉内容为空或 '[Not found]' 的chunk
    valid_chunks = [c for c in chunks if c.get("chunk_text") and c.get("chunk_text") != "[Not found]"]
    if not valid_chunks:
        print("No valid chunks with content for summarization.")
        return None, None, None

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    delimiter = "#####"
    try:
        # Print chunk metadata for debugging
        for i, chunk in enumerate(valid_chunks):
            print(f"Chunk Metadata {i+1}: {chunk}")

        # Compose context with all available metadata for each chunk
        def format_chunk(i, chunk):
            # 优先从 chunk['chunk_text'] 获取正文内容
            text = chunk.get("chunk_text", "")
            # 兼容部分chunk结构正文可能在 chunk['metadata']['text'] 的情况
            if not text and "metadata" in chunk and "text" in chunk["metadata"]:
                text = chunk["metadata"]["text"]
            meta = chunk
            ref = []
            if meta.get("title"): ref.append(f"Title: {meta['title']}")
            if meta.get("author"): ref.append(f"Author: {meta['author']}")
            if meta.get("journal"): ref.append(f"Journal: {meta['journal']}")
            if meta.get("year"): ref.append(f"Year: {meta['year']}")
            if meta.get("doi"): ref.append(f"DOI: {meta['doi']}")
            if meta.get("source"): ref.append(f"Source: {meta['source']}")
            ref_str = "; ".join(ref)
            return f"Chunk {i + 1}: {text}\n[{ref_str}]"

        context = "\n\n".join([format_chunk(i, chunk) for i, chunk in enumerate(valid_chunks)])
        prompt = prompt_template.format(context=context)

        # Debug: 打印最终传入LLM的内容
        print("==== LLM Prompt Preview ====")
        print(prompt)
        print("==== End of LLM Prompt ====")

        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a helpful assistant for summarizing research with citations. The customer service query will be delimited with {delimiter} characters. Do your best and summarize based on user's input in markdown format."},
                {"role": "user", "content": f"{delimiter}{prompt}{delimiter}"}
            ],
            temperature=0.5,
            max_tokens=max_tokens
        )
        end_time = time.time()

        processing_time = "{:.2f}".format(end_time - start_time)
        token_consumption = getattr(response.usage, "total_tokens", None)
        summary = response.choices[0].message.content

        if log_metrics:
            print(f"Processing Time: {processing_time} seconds")
            print(f"Total Tokens: {token_consumption}")

        return summary, processing_time, token_consumption
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None, None, None

def call_llm_with_prompt(
    prompt: str,
    model: str = "gpt-4o-mini",
    api_key: str = None,
    base_url: str = None,
    max_tokens: int = 1280,
    temperature: float = 0.5
) -> str:
    """
    调用LLM生成内容，返回LLM的原始输出（如csv表格）。
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    delimiter = "#####"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. The user input is delimited with {delimiter}."},
            {"role": "user", "content": f"{delimiter}{prompt}{delimiter}"}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


