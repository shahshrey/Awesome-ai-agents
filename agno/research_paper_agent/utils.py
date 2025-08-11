"""Utility functions for Research Paper Analysis"""

import re
import io
import requests
from typing import Optional
from datetime import datetime
import PyPDF2
import structlog

from data_models import PaperMetadata

# Initialize logger
logger = structlog.get_logger()

# Constants
ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_PDF_URL = "https://arxiv.org/pdf/{}.pdf"
MAX_CONTENT_LENGTH = 10000


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from uploaded PDF file
    
    Args:
        pdf_file: PDF file object or BytesIO stream
        
    Returns:
        Extracted text content from PDF
    """
    logger.info("extracting_text_from_pdf")
    
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            
        logger.info("pdf_extraction_successful", pages=len(pdf_reader.pages))
        return text
        
    except Exception as e:
        logger.error("pdf_extraction_failed", error=str(e))
        return ""


def extract_arxiv_id(url: str) -> Optional[str]:
    """
    Extract arXiv ID from URL
    
    Args:
        url: arXiv URL
        
    Returns:
        Extracted arXiv ID or None
    """
    logger.debug("extracting_arxiv_id", url=url)
    
    arxiv_pattern = r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)"
    match = re.search(arxiv_pattern, url)
    
    if not match:
        logger.warning("arxiv_id_not_found", url=url)
        return None
        
    arxiv_id = match.group(1)
    logger.info("arxiv_id_extracted", arxiv_id=arxiv_id)
    return arxiv_id


def fetch_arxiv_metadata(arxiv_id: str) -> Optional[PaperMetadata]:
    """
    Fetch paper metadata from arXiv API
    
    Args:
        arxiv_id: arXiv paper ID
        
    Returns:
        PaperMetadata object or None if fetch fails
    """
    logger.info("fetching_arxiv_metadata", arxiv_id=arxiv_id)
    
    try:
        url = f"{ARXIV_API_URL}?id_list={arxiv_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.error("arxiv_api_error", status_code=response.status_code)
            return None
            
        content = response.text
        
        # Extract fields using regex
        title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Unknown Title"
        
        abstract_match = re.search(r"<summary>(.*?)</summary>", content, re.DOTALL)
        abstract = abstract_match.group(1).strip() if abstract_match else ""
        
        # Extract authors
        authors = re.findall(r"<name>(.*?)</name>", content)
        
        # Extract publication date
        published_match = re.search(r"<published>(.*?)</published>", content)
        pub_date = published_match.group(1)[:10] if published_match else None
        
        metadata = PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            publication_date=pub_date,
            venue="arXiv",
            arxiv_id=arxiv_id,
            doi=None,
        )
        
        logger.info("arxiv_metadata_fetched", title=title, authors_count=len(authors))
        return metadata
        
    except requests.RequestException as e:
        logger.error("arxiv_fetch_network_error", error=str(e))
        return None
    except Exception as e:
        logger.error("arxiv_fetch_error", error=str(e))
        return None


def fetch_arxiv_pdf_content(arxiv_id: str) -> Optional[str]:
    """
    Fetch and extract text from arXiv PDF
    
    Args:
        arxiv_id: arXiv paper ID
        
    Returns:
        Extracted text content or None
    """
    logger.info("fetching_arxiv_pdf", arxiv_id=arxiv_id)
    
    try:
        pdf_url = ARXIV_PDF_URL.format(arxiv_id)
        response = requests.get(pdf_url, timeout=30)
        
        if response.status_code != 200:
            logger.error("arxiv_pdf_fetch_error", status_code=response.status_code)
            return None
            
        pdf_file = io.BytesIO(response.content)
        content = extract_text_from_pdf(pdf_file)
        
        logger.info("arxiv_pdf_fetched", content_length=len(content))
        return content
        
    except requests.RequestException as e:
        logger.error("arxiv_pdf_network_error", error=str(e))
        return None
    except Exception as e:
        logger.error("arxiv_pdf_error", error=str(e))
        return None


def search_arxiv_papers(query: str, max_results: int = 10) -> list:
    """
    Search for papers on arXiv
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of paper info dictionaries
    """
    logger.info("searching_arxiv", query=query, max_results=max_results)
    
    try:
        search_url = f"{ARXIV_API_URL}?search_query=all:{query}&start=0&max_results={max_results}"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code != 200:
            logger.error("arxiv_search_error", status_code=response.status_code)
            return []
            
        content = response.text
        entries = re.findall(r"<entry>(.*?)</entry>", content, re.DOTALL)
        
        papers = []
        for entry in entries:
            title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            id_match = re.search(r"<id>(.*?)</id>", entry)
            
            if not title_match or not id_match:
                continue
                
            title = title_match.group(1).strip()
            arxiv_url = id_match.group(1).strip()
            arxiv_id = arxiv_url.split("/")[-1]
            
            papers.append({
                "title": title,
                "url": arxiv_url,
                "arxiv_id": arxiv_id
            })
            
        logger.info("arxiv_search_complete", results_count=len(papers))
        return papers
        
    except requests.RequestException as e:
        logger.error("arxiv_search_network_error", error=str(e))
        return []
    except Exception as e:
        logger.error("arxiv_search_error", error=str(e))
        return []


def generate_bibtex(metadata: PaperMetadata) -> str:
    """
    Generate BibTeX entry for the paper
    
    Args:
        metadata: Paper metadata
        
    Returns:
        BibTeX formatted string
    """
    logger.debug("generating_bibtex", title=metadata.title)
    
    authors = " and ".join(metadata.authors) if metadata.authors else "Unknown"
    year = (
        metadata.publication_date[:4]
        if metadata.publication_date
        else str(datetime.now().year)
    )
    
    # Create a simple cite key
    first_author = metadata.authors[0].split()[-1] if metadata.authors else "Unknown"
    cite_key = f"{first_author.lower()}{year}"
    
    bibtex = f"""@article{{{cite_key},
    title = {{{metadata.title}}},
    author = {{{authors}}},
    year = {{{year}}},
    journal = {{{metadata.venue or "arXiv"}}},"""
    
    if metadata.arxiv_id:
        bibtex += f"\n    eprint = {{{metadata.arxiv_id}}},"
    if metadata.doi:
        bibtex += f"\n    doi = {{{metadata.doi}}},"
    
    bibtex += "\n}"
    
    logger.info("bibtex_generated", cite_key=cite_key)
    return bibtex


def truncate_content(content: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """
    Truncate content to specified length
    
    Args:
        content: Text content to truncate
        max_length: Maximum length
        
    Returns:
        Truncated content
    """
    if len(content) <= max_length:
        return content
        
    truncated = content[:max_length] + "..."
    logger.debug("content_truncated", original_length=len(content), truncated_length=max_length)
    return truncated
