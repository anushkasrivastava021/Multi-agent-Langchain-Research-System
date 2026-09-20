from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web and return the results."""
    results=tavily.search(query=query,max_results=5)
    out=[]
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")

    return "\n----\n".join(out)


@tool
def web_scrape(url: str) -> str:
    """Scrape and extract clean, readable main content from a specific URL. 
    Use this when you need deep context from a specific webpage."""
    
    # Anti-bot detection mitigation
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Fetch the raw HTML with a strict timeout so the agent doesn't hang
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        extracted_text = None

        # STRATEGY 1: Trafilatura (The cleanest article extraction)
        extracted_text = trafilatura.extract(
            html_content, 
            include_comments=False, 
            include_tables=False, 
            no_fallback=True
        )

        # STRATEGY 2: Readability + BeautifulSoup (Semantic fallback)
        if not extracted_text:
            doc = Document(html_content)
            article_html = doc.summary()
            soup = BeautifulSoup(article_html, "html.parser")
            extracted_text = soup.get_text(separator="\n")

        # STRATEGY 3: Raw BeautifulSoup (Brute-force last resort)
        if not extracted_text or len(extracted_text.strip()) < 50:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Obliterate non-content tags before extracting text
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.extract()
                
            extracted_text = soup.get_text(separator="\n")

        # FINAL CLEANUP: Regex structural formatting
        if extracted_text:
            # Condense multiple blank lines into standard paragraph breaks
            clean_text = re.sub(r'\n{3,}', '\n\n', extracted_text).strip()
            
            # Cap the output to protect the LLM context window (roughly 1500-2000 tokens)
            return clean_text[:8000]
        else:
            return f"Error: Content extraction failed. The webpage at {url} might be a dynamic JavaScript application."

    except requests.exceptions.RequestException as e:
        return f"Network Error while accessing {url}: {str(e)}"
    except Exception as e:
        return f"Parsing Error on {url}: {str(e)}"