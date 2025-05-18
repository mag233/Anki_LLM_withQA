import openai  # type: ignore
import os
import time
from typing import Optional, Dict, Any, Tuple, List, Union

# 设置默认API基础URL
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_QWEN_BASE_URL = "https://dashscope.aliyuncs.com/v1"

# 获取环境变量中的API配置
base_url = os.getenv("OPENAI_API_BASE", DEFAULT_OPENAI_BASE_URL)
api_key = os.getenv("OPENAI_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")

# 导入提示词模板
try:
    from format_template import SUMMARIZE_PROMPT
except ImportError:
    # 如果导入失败，提供一个默认的提示词模板
    SUMMARIZE_PROMPT = """Please standardize and structure the following user query while keeping the core idea:
    
    {user_query}
    
    Provide a clear, structured version of this query."""

# 模型配置
MODEL_CONFIGS = {
    "openai": {
        "default_model": "gpt-4o-mini",
        "base_url": DEFAULT_OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY"
    },
    "qwen": {
        "default_model": "qwen-max",
        "base_url": DEFAULT_QWEN_BASE_URL,
        "api_key_env": "QWEN_API_KEY"
    }
}


def get_model_provider(model: str) -> str:
    """
    根据模型名称确定模型提供商
    
    Args:
        model: 模型名称
        
    Returns:
        str: 模型提供商名称('openai'或'qwen')
    """
    if model.startswith(("gpt-", "claude-")):
        return "openai"
    elif model.startswith("qwen"):
        return "qwen"
    else:
        # 默认使用OpenAI
        return "openai"


def get_client(provider: str, api_key: Optional[str] = None, base_url: Optional[str] = None) -> Any:
    """
    根据提供商获取对应的API客户端
    
    Args:
        provider: 模型提供商('openai'或'qwen')
        api_key: API密钥，如果为None则从环境变量获取
        base_url: API基础URL，如果为None则使用默认值
    
    Returns:
        API客户端实例
    """
    config = MODEL_CONFIGS.get(provider, MODEL_CONFIGS["openai"])
    
    # 如果未提供参数，则从环境变量获取
    if api_key is None:
        api_key = os.getenv(config["api_key_env"])
    
    if base_url is None:
        base_url = os.getenv(f"{provider.upper()}_API_BASE", config["base_url"])
    
    return openai.OpenAI(api_key=api_key, base_url=base_url)


def standardize_query_with_llm(user_query: str, model: str = None) -> str:
    """
    使用LLM来标准化和结构化用户的查询。
    这将保留用户的想法，但将其转化为清晰、结构化的问题。
    
    Args:
        user_query: 用户的原始查询文本
        model: 要使用的LLM模型
    
    Returns:
        str: 标准化后的查询文本
    """
    if not user_query or not isinstance(user_query, str):
        return ""
    
    prompt = SUMMARIZE_PROMPT.format(user_query=user_query)
    model = model or "gpt-4o-mini"  # fallback to default if not specified
    improved_query = call_llm_with_prompt(
        prompt, 
        model=model, 
        max_tokens=300
    )
    
    print("==== Standardized Query by LLM ====")
    print(improved_query)
    return improved_query.strip()


def summarize_chunks(chunks: List[Dict[str, Any]],
                    prompt_template: str,
                    model: str = "gpt-4o-mini",
                    api_key: Optional[str] = None,
                    max_tokens: int = 12800,
                    base_url: Optional[str] = None,
                    log_metrics: bool = False,
                    temperature: float = 0.8) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    使用LLM对文本块进行摘要
    
    Args:
        chunks: 包含文本和元数据的文本块列表
        prompt_template: 摘要提示模板，需要包含{context}占位符
        model: 要使用的LLM模型
        api_key: API密钥，如果为None则从环境变量获取
        max_tokens: 生成摘要的最大令牌数
        base_url: API基础URL，如果为None则使用默认值
        log_metrics: 是否记录处理时间和令牌消耗
        temperature: 模型温度参数
    
    Returns:
        Tuple[Optional[str], Optional[str], Optional[int]]: 
            (摘要文本, 处理时间(秒), 令牌消耗)，如果出错则返回(None, None, None)
    """
    # 防御性检查：跳过空的chunks
    if not chunks or not isinstance(chunks, list):
        print("No chunks provided for summarization.")
        return None, None, None

    # 过滤掉内容为空或 '[Not found]' 的chunk
    valid_chunks = [c for c in chunks if c.get("chunk_text") and c.get("chunk_text") != "[Not found]"]
    if not valid_chunks:
        print("No valid chunks with content for summarization.")
        return None, None, None

    # 获取模型提供商并初始化客户端
    provider = get_model_provider(model)
    client = get_client(provider, api_key, base_url)
    
    delimiter = "#####"
    try:
        # 打印块元数据以便调试
        for i, chunk in enumerate(valid_chunks):
            print(f"Chunk Metadata {i+1}: {chunk}")

        # 使用所有可用元数据为每个块组成上下文
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

        # 调试：打印最终传入LLM的内容
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
            temperature=temperature,
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
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    max_tokens: int = 1280,
    temperature: float = 0.5
) -> str:
    """
    调用LLM生成内容，返回LLM的原始输出（如csv表格）。
    
    Args:
        prompt: 提示词
        model: 要使用的LLM模型
        api_key: API密钥，如果为None则从环境变量获取
        base_url: API基础URL，如果为None则使用默认值
        max_tokens: 生成的最大令牌数
        temperature: 模型温度参数
    
    Returns:
        str: LLM生成的内容
    """
    # 获取模型提供商并初始化客户端
    provider = get_model_provider(model)
    client = get_client(provider, api_key, base_url)
    
    delimiter = "#####"
    
    try:
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
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"Error generating response: {str(e)}"
