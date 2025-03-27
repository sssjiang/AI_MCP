from mcp.server.fastmcp import FastMCP
from pubmed import search_pubmed
import requests
import os
# Create an MCP server
mcp = FastMCP("PubMed")



def convert_to_pubmed_query(query: str) -> str:
    """
    Convert natural language query to PubMed advanced search syntax using NLP
    
    Args:
        query (str): Natural language query in Chinese or English
        
    Returns:
        str: PubMed advanced search syntax
    """
    # 构建提示词
    prompt = f"""
    请将以下自然语言查询转换为PubMed高级检索式。查询可以是中文或英文。
    请识别查询中的字段（如作者、标题、期刊等）、搜索词和时间限制，并生成合适的PubMed检索式。
    
    对于时间相关的查询（如"近五年"），请转换为具体的年份范围，如("2020"[PDAT]:"2025"[PDAT])。
    对于疾病和治疗方法，尽量使用MeSH术语并添加适当的字段标识符。
    
    查询: {query}
    
    请返回转换后的PubMed检索式，格式为: 搜索词[字段]
    例如:
    - 输入: "查找作者是Smith的文章"
    - 输出: "Smith[AU]"
    
    - 输入: "找到近五年关于新冠肺炎和免疫治疗的文章"
    - 输出: ("COVID-19"[MeSH] OR "SARS-CoV-2"[MeSH]) AND "immunotherapy"[MeSH] AND ("2020"[PDAT]:"2025"[PDAT])
    
    请只返回检索式，不要其他解释。
    """
    
    # 调用DashScope API
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": os.getenv("LLM_API_KEY"),
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-plux",  # 或其他您使用的模型
        "messages": [
            {"role": "system", "content": "你是一个专业的医学文献检索助手，擅长将自然语言转换为PubMed检索式。"},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    # 提取生成的检索式
    pubmed_query = result["choices"][0]["message"]["content"].strip()
    print(pubmed_query)
    return pubmed_query 
  

@mcp.tool()
def search_pubmed_with_natural_language(content: str,api_key: str = None) -> str:
    pubmed_query=convert_to_pubmed_query(content)
    """
    Search PubMed articles using the original natural content
    
    Args:
        content (str): the original natural content
        max_results (int): Maximum number of results to return (default: 3)
        api_key (str, optional): NCBI API key for higher rate limits
        
    Returns:
        str: JSON string containing search results
    """
    return search_pubmed(pubmed_query, 3, api_key)



# Add a dynamic resource for getting article details
@mcp.resource("article://{pmid}")
def get_article_details(pmid: str) -> str:
    """
    Get details for a specific PubMed article by PMID
    
    Args:
        pmid (str): PubMed ID of the article
        
    Returns:
        str: JSON string containing article details
    """
    return search_pubmed(f"{pmid}[PMID]", max_results=1) 

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')