import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import json
def search_pubmed(query, max_results=3, api_key=None):
    """
    使用PubMed E-utilities API检索文献
    
    参数:
    query (str): PubMed检索词
    max_results (int): 返回的最大结果数 (默认: 3)
    api_key (str, optional): NCBI API密钥，可提高请求速率限制
    
    返回:
    list: 包含检索结果的字典列表
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # 步骤1: 使用esearch获取符合查询的PMID列表
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "usehistory": "y",
        "retmode": "xml"
    }
    
    if api_key:
        search_params["api_key"] = api_key
    
    search_response = requests.get(search_url, params=search_params)
    search_root = ET.fromstring(search_response.content)
    
    # 获取WebEnv和QueryKey用于后续请求
    web_env = search_root.find("WebEnv").text
    query_key = search_root.find("QueryKey").text
    
    # 获取找到的文章总数
    count = int(search_root.find("Count").text)
    print(f"找到 {count} 篇相关文章，显示前 {min(count, max_results)} 篇")
    
    # 步骤2: 使用efetch获取详细信息
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": web_env,
        "retmax": max_results,
        "retmode": "xml",
        "rettype": "abstract"
    }
    
    if api_key:
        fetch_params["api_key"] = api_key
    
    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_root = ET.fromstring(fetch_response.content)
    
    # 步骤3: 解析结果
    results = []
    articles = fetch_root.findall(".//PubmedArticle")
    
    for article in articles:
        try:
            # 提取PMID
            pmid = article.find(".//PMID").text
            
            # 提取标题
            title_element = article.find(".//ArticleTitle")
            title = title_element.text if title_element is not None else "无标题"
            
            # 提取作者
            authors = []
            author_list = article.findall(".//Author")
            for author in author_list:
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                if last_name is not None and fore_name is not None:
                    authors.append(f"{last_name.text} {fore_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)
            
            # 提取期刊信息
            journal_element = article.find(".//Journal/Title")
            journal = journal_element.text if journal_element is not None else "未知期刊"
            
            # 提取发表日期
            pub_date = None
            year_element = article.find(".//PubDate/Year")
            month_element = article.find(".//PubDate/Month")
            day_element = article.find(".//PubDate/Day")
            
            if year_element is not None:
                pub_date = year_element.text
                if month_element is not None:
                    pub_date += f" {month_element.text}"
                    if day_element is not None:
                        pub_date += f" {day_element.text}"
            
            # 提取摘要
            abstract_elements = article.findall(".//AbstractText")
            abstract = " ".join([elem.text for elem in abstract_elements if elem.text]) if abstract_elements else "无摘要"
            
            # 添加到结果列表
            results.append({
                "pmid": pmid,
                "title": title,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
                "abstract": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
        except Exception as e:
            print(f"解析文章时出错: {e}")
    # json string 
    return json.dumps(results, indent=4, ensure_ascii=False)


# 使用示例
if __name__ == "__main__":
    query = "cancer immunotherapy"
    results = search_pubmed(query, max_results=3)
    print(results)
