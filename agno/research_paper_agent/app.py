import streamlit as st
from datetime import datetime
from typing import Dict, Any
import structlog

from data_models import PaperMetadata
from agent import (
    create_agent_team,
    analyze_paper,
)
from utils import (
    extract_text_from_pdf,
    extract_arxiv_id,
    fetch_arxiv_metadata,
    fetch_arxiv_pdf_content,
    search_arxiv_papers,
    generate_bibtex
)

logger = structlog.get_logger()

PAGE_TITLE = "Research Paper Analysis Agent"
PAGE_ICON = "📚"
LAYOUT = "wide"


def initialize_session_state() -> None:
    logger.info("initializing_session_state")
    
    defaults = {
        "openai_key": "",
        "papers_analyzed": [],
        "analysis_results": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            logger.debug("session_state_initialized", key=key)


def setup_sidebar() -> None:
    logger.info("setting_up_sidebar")
    
    with st.sidebar:
        st.title("🔧 Configuration")
        
        st.session_state.openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_key,
            type="password",
            help="Required for paper analysis",
        )
        
        st.divider()
        st.subheader("📊 Analysis History")
        
        if not st.session_state.papers_analyzed:
            st.info("No papers analyzed yet")
            return
            
        for i, paper in enumerate(st.session_state.papers_analyzed):
            if st.button(f"📄 {paper['title'][:30]}...", key=f"history_{i}"):
                st.session_state.analysis_results = paper["results"]
                logger.info("loaded_paper_from_history", title=paper['title'][:30])
                st.rerun()


def display_analysis_results(results: Dict[str, Any]) -> None:
    logger.info("displaying_analysis_results")
    
    tabs = st.tabs([
        "📊 Summary",
        "🔍 Detailed Analysis",
        "📚 Citations",
        "🗺️ Visualization",
        "📋 Export",
    ])
    
    structured_analysis = results.get("structured_analysis")
    citations = results.get("citations", [])
    visualization = results.get("visualization", "")
    
    with tabs[0]:
        _display_summary_tab(results, structured_analysis)
    
    with tabs[1]:
        _display_detailed_analysis_tab(structured_analysis, results)
    
    with tabs[2]:
        _display_citations_tab(citations)
    
    with tabs[3]:
        _display_visualization_tab(visualization)
    
    with tabs[4]:
        _display_export_tab(results, structured_analysis, citations)


def _display_summary_tab(results: Dict[str, Any], structured_analysis: Any) -> None:
    st.subheader("Executive Summary")
    
    if structured_analysis:
        st.write(structured_analysis.executive_summary)
        
        st.subheader("Key Findings")
        for finding in structured_analysis.key_findings:
            st.write(f"• {finding}")
    
    if not results.get("metadata"):
        return
        
    meta = results["metadata"]
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Authors", len(meta.authors))
        st.metric("Publication", meta.venue or "arXiv")
    
    with col2:
        st.metric("Date", meta.publication_date or "Unknown")
        if meta.arxiv_id:
            st.metric("arXiv ID", meta.arxiv_id)


def _display_detailed_analysis_tab(structured_analysis: Any, results: Dict[str, Any]) -> None:
    st.subheader("Comprehensive Analysis")
    
    if not structured_analysis:
        st.markdown(results.get("raw_analysis", "No analysis available"))
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Methodology")
        st.write(structured_analysis.methodology)
        
        st.subheader("Technical Terms")
        for term, definition in structured_analysis.technical_terms.items():
            st.write(f"**{term}**: {definition}")
    
    with col2:
        st.subheader("Limitations")
        for limitation in structured_analysis.limitations:
            st.write(f"• {limitation}")
        
        st.subheader("Future Work")
        for work in structured_analysis.future_work:
            st.write(f"• {work}")


def _display_citations_tab(citations: list) -> None:
    st.subheader("Citations and References")
    
    if not citations:
        st.info("No citations extracted yet")
        return
        
    for i, citation in enumerate(citations, 1):
        st.write(f"**{i}.** {citation.title}")
        
        authors_str = (
            ", ".join(citation.authors)
            if citation.authors
            else "Unknown authors"
        )
        
        venue_year = (
            f"{citation.venue} ({citation.year})"
            if citation.venue and citation.year
            else "Unknown venue/year"
        )
        
        st.write(f"   *{authors_str}* - {venue_year}")
        st.write("---")


def _display_visualization_tab(visualization: str) -> None:
    st.subheader("Concept Map")
    
    if not visualization or not visualization.strip():
        st.info("No visualization generated yet")
        return
        
    st.code(visualization, language="mermaid")


def _display_export_tab(results: Dict[str, Any], structured_analysis: Any, citations: list) -> None:
    st.subheader("Export Options")
    
    if results.get("metadata"):
        st.text_area(
            "BibTeX Entry",
            generate_bibtex(results["metadata"]),
            height=200
        )
    
    if st.button("📥 Download Analysis (Markdown)"):
        _generate_and_download_markdown(results, structured_analysis, citations)


def _generate_and_download_markdown(results: Dict[str, Any], structured_analysis: Any, citations: list) -> None:
    metadata = results.get("metadata")
    
    title = metadata.title if metadata else "Paper Analysis"
    authors = ", ".join(metadata.authors) if metadata else "Unknown"
    date = metadata.publication_date if metadata else "Unknown"
    
    analysis_md = f"""# {title}

## Metadata
- Authors: {authors}
- Date: {date}

## Executive Summary
{structured_analysis.executive_summary if structured_analysis else "No summary available"}

## Key Findings
{chr(10).join([f"- {finding}" for finding in structured_analysis.key_findings]) if structured_analysis else "No findings available"}

## Methodology
{structured_analysis.methodology if structured_analysis else "No methodology available"}

## Limitations
{chr(10).join([f"- {limitation}" for limitation in structured_analysis.limitations]) if structured_analysis else "No limitations available"}

## Future Work
{chr(10).join([f"- {work}" for work in structured_analysis.future_work]) if structured_analysis else "No future work available"}

## Citations
{chr(10).join([f"- {cite.title} ({cite.year})" for cite in citations]) if citations else "No citations available"}
"""
    
    st.download_button(
        label="Download",
        data=analysis_md,
        file_name=f"paper_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
    )
    
    logger.info("markdown_download_prepared", filename_timestamp=datetime.now().strftime('%Y%m%d_%H%M%S'))


def handle_pdf_upload(uploaded_file, agent_team) -> tuple:
    logger.info("handling_pdf_upload", filename=uploaded_file.name)
    
    with st.spinner("📄 Extracting text from PDF..."):
        content = extract_text_from_pdf(uploaded_file)
        
        if not content:
            st.error("Failed to extract text from PDF")
            return None, None
            
        st.success("✅ PDF text extracted successfully")
        
        metadata = PaperMetadata(
            title=uploaded_file.name.replace(".pdf", ""),
            authors=["Unknown"],
            abstract=content[:500],
            publication_date=None,
            venue=None,
            doi=None,
            arxiv_id=None,
        )
        
        return content, metadata


def handle_arxiv_url(paper_url: str) -> tuple:
    logger.info("handling_arxiv_url", url=paper_url)
    
    arxiv_id = extract_arxiv_id(paper_url)
    
    if not arxiv_id:
        st.error("Invalid arXiv URL format")
        return None, None
        
    with st.spinner("🌐 Fetching paper from arXiv..."):
        metadata = fetch_arxiv_metadata(arxiv_id)
        
        if not metadata:
            st.error("Failed to fetch paper metadata")
            return None, None
            
        st.success(f"✅ Found: {metadata.title}")
        
        content = fetch_arxiv_pdf_content(arxiv_id)
        
        if not content:
            st.error("Could not fetch PDF content")
            return None, None
            
        return content, metadata


def handle_search_query(search_query: str) -> None:
    logger.info("handling_search_query", query=search_query)
    
    with st.spinner("🔍 Searching arXiv for papers..."):
        papers = search_arxiv_papers(search_query, max_results=5)
        
        if not papers:
            st.error("No papers found for this search query")
            return
            
        st.info("📚 Found papers on arXiv:")
        
        for i, paper in enumerate(papers, 1):
            st.write(f"**{i}.** {paper['title']}")
            st.write(f"   📎 {paper['url']}")
            st.write("---")
        
        st.warning("💡 Copy one of the arXiv URLs above and paste it in the URL field to analyze")


def main() -> None:
    logger.info("starting_streamlit_app")
    
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT
    )
    
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.markdown("""
    Analyze academic papers with AI-powered insights. Upload a PDF or provide an arXiv link to get:
    - Executive summaries and key findings
    - Methodology breakdowns
    - Citation analysis
    - Visual concept maps
    """)
    
    initialize_session_state()
    setup_sidebar()
    
    if not st.session_state.openai_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to begin.")
        logger.warning("no_api_key_provided")
        return
    
    try:
        agent_team = create_agent_team(st.session_state.openai_key)
    except Exception as e:
        st.error(f"Failed to create agent team: {str(e)}")
        logger.error("agent_team_creation_failed", error=str(e))
        return
    
    st.subheader("📥 Input Paper")
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="Upload a research paper in PDF format"
        )
    
    with col2:
        paper_url = st.text_input(
            "Or paste arXiv/DOI URL",
            placeholder="https://arxiv.org/abs/2301.00001",
            help="Enter an arXiv URL or DOI",
        )
    
    search_query = st.text_input(
        "🔍 Or search for papers by topic",
        placeholder="quantum computing applications"
    )
    
    if st.button("🚀 Analyze Paper", type="primary", use_container_width=True):
        content = None
        metadata = None
        
        if uploaded_file:
            content, metadata = handle_pdf_upload(uploaded_file, agent_team)
            
        elif paper_url:
            content, metadata = handle_arxiv_url(paper_url)
            
        elif search_query:
            handle_search_query(search_query)
            return
        
        if content:
            with st.spinner("🧠 Analyzing paper... This may take a minute."):
                try:
                    results = analyze_paper(content, metadata, agent_team)
                    st.session_state.analysis_results = results
                    
                    if metadata:
                        st.session_state.papers_analyzed.append({
                            "title": metadata.title,
                            "timestamp": datetime.now(),
                            "results": results,
                        })
                        logger.info("paper_added_to_history", title=metadata.title)
                    
                    display_analysis_results(results)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    logger.error("analysis_failed", error=str(e))
        else:
            st.error("❌ No content to analyze. Please provide a valid input.")
    
    elif st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results)
    
    st.divider()
    st.caption("Built with Agno and OpenAI | Research Paper Analysis Agent v1.0")


if __name__ == "__main__":
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    main()
