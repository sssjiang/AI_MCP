from mcp.server.fastmcp import FastMCP
from pubmed import search_pubmed

# Create an MCP server
mcp = FastMCP("PubMed")


@mcp.prompt()
def convert_to_pubmed_query(query: str) -> str:
    """
    Convert natural language query to PubMed advanced search syntax using NLP
    
    Args:
        query (str): Natural language query in Chinese or English
        
    Returns:
        str: PubMed advanced search syntax
    """
    # 使用自然语言处理来理解查询意图和字段
    prompt = f"""
    请将以下自然语言查询转换为PubMed高级检索式。查询可以是中文或英文。
    请识别查询中的字段（如作者、标题、期刊等）和搜索词，并生成合适的PubMed检索式。
    
    查询: {query}
    
    请返回转换后的PubMed检索式，格式为: 搜索词[字段]
    例如:
    - 输入: "查找作者是Smith的文章"
    - 输出: "Smith[AU]"
    
    请只返回检索式，不要其他解释。
    """
    return prompt
@mcp.tool()
def search_pubmed_articles(query: str, api_key: str = None) -> str:
    """
    Search PubMed articles using PubMed advanced search syntax
    
    Args:
        query (str): PubMed advanced search syntax
        api_key (str, optional): NCBI API key for higher rate limits
        
    Returns:
        str: JSON string containing search results
    """
    return search_pubmed(query, 3, api_key)

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