import re
import json
from typing import Dict, Any, List, Optional, Tuple
import structlog

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from data_models import PaperMetadata, PaperAnalysis, Citation


logger = structlog.get_logger()

DEFAULT_MODEL = "gpt-5-mini"


def create_paper_extractor_agent(api_key: str) -> Agent:
    logger.info("creating_paper_extractor_agent")
    
    try:
        agent = Agent(
            name="Paper Extractor",
            role="Extract and parse paper content from PDFs and URLs",
            model=OpenAIChat(id=DEFAULT_MODEL, api_key=api_key),
            instructions=[
                "Extract structured information from academic papers",
                "Identify title, authors, abstract, and key sections",
                "Parse references and citations",
                "Handle various paper formats gracefully",
            ],
            markdown=True,
        )
        logger.info("paper_extractor_agent_created")
        return agent
        
    except Exception as e:
        logger.error("failed_to_create_paper_extractor", error=str(e))
        raise


def create_analysis_agent(api_key: str) -> Agent:
    logger.info("creating_analysis_agent")
    
    try:
        agent = Agent(
            name="Analysis Agent",
            role="Perform comprehensive analysis of paper content",
            model=OpenAIChat(id=DEFAULT_MODEL, api_key=api_key),
            instructions=[
                "Generate executive summaries that capture the essence of the paper",
                "Identify and explain key findings and contributions",
                "Break down methodology in accessible terms",
                "Identify limitations and future work opportunities",
                "Explain technical jargon for broader audience",
                "Return analysis in structured JSON format following PaperAnalysis schema",
            ],
            markdown=True,
        )
        logger.info("analysis_agent_created")
        return agent
        
    except Exception as e:
        logger.error("failed_to_create_analysis_agent", error=str(e))
        raise


def create_citation_agent(api_key: str) -> Agent:
    logger.info("creating_citation_agent")
    
    try:
        agent = Agent(
            name="Citation Agent",
            role="Manage citations and find related work",
            model=OpenAIChat(id=DEFAULT_MODEL, api_key=api_key),
            instructions=[
                "Extract and format citations from papers",
                "Analyze references within the paper content",
                "Generate proper BibTeX entries",
                "Identify key works cited in the field",
                "Return citations in structured JSON format following Citation schema",
            ],
            markdown=True,
        )
        logger.info("citation_agent_created")
        return agent
        
    except Exception as e:
        logger.error("failed_to_create_citation_agent", error=str(e))
        raise


def create_visualization_agent(api_key: str) -> Agent:
    logger.info("creating_visualization_agent")
    
    try:
        agent = Agent(
            name="Visualization Agent",
            role="Create diagrams and visual representations",
            model=OpenAIChat(id=DEFAULT_MODEL, api_key=api_key),
            instructions=[
                "Generate Mermaid diagrams for concepts",
                "Create relationship maps between ideas",
                "Visualize paper structure and flow",
                "Design clear, informative diagrams",
            ],
            markdown=True,
        )
        logger.info("visualization_agent_created")
        return agent
        
    except Exception as e:
        logger.error("failed_to_create_visualization_agent", error=str(e))
        raise


def create_agent_team(api_key: str) -> Agent:
    logger.info("creating_agent_team")
    
    try:
        extractor = create_paper_extractor_agent(api_key)
        analyzer = create_analysis_agent(api_key)
        citation = create_citation_agent(api_key)
        visualizer = create_visualization_agent(api_key)
        
        team = Agent(
            team=[extractor, analyzer, citation, visualizer],
            name="Research Paper Analysis Team",
            model=OpenAIChat(id=DEFAULT_MODEL, api_key=api_key),
            instructions=[
                "Coordinate analysis across all agents",
                "Ensure comprehensive paper understanding",
                "Generate actionable insights for researchers",
            ],
            show_tool_calls=True,
            markdown=True,
        )
        
        logger.info("agent_team_created", team_size=4)
        return team
        
    except Exception as e:
        logger.error("failed_to_create_agent_team", error=str(e))
        raise


def parse_structured_analysis(
    analysis_text: str,
) -> Tuple[PaperAnalysis, List[Citation], str]:
    logger.info("parsing_structured_analysis", response_length=len(analysis_text))
    
    try:
        json_data = None
        json_match = re.search(r"```json\s*(.*?)\s*```", analysis_text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(1).strip()
                json_str = json_str.replace('\n\n', '\n')
                json_str = re.sub(r'",\s*}', '"}', json_str)
                json_str = re.sub(r'",\s*]', '"]', json_str)
                json_data = json.loads(json_str)
                logger.info("json_extracted_from_code_block")
            except json.JSONDecodeError as e:
                logger.warning("json_parse_failed_from_code_block", error=str(e))
        
        if not json_data:
            json_match = re.search(r'\{.*"analysis".*\}', analysis_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                    logger.info("json_extracted_directly")
                except json.JSONDecodeError as e:
                    logger.warning("json_parse_failed_direct", error=str(e))
        
        if not json_data:
            logger.warning("falling_back_to_text_extraction")
            return _extract_from_text(analysis_text)
        
        analysis_dict = json_data.get("analysis", {})
        if not analysis_dict:
            logger.warning("no_analysis_section_in_json")
            return _create_default_analysis()
            
        paper_analysis = PaperAnalysis(**analysis_dict)
        
        citations = []
        for cite_data in json_data.get("citations", []):
            try:
                citations.append(Citation(**cite_data))
            except Exception as e:
                logger.warning("citation_parse_error", error=str(e), citation=cite_data)
        
        visualization = json_data.get("visualization", "")
        
        logger.info(
            "analysis_parsed_successfully",
            findings_count=len(paper_analysis.key_findings),
            citations_count=len(citations)
        )
        return paper_analysis, citations, visualization
        
    except json.JSONDecodeError as e:
        logger.error("json_parse_error", error=str(e), position=e.pos if hasattr(e, 'pos') else None)
        return _extract_from_text(analysis_text)
    except Exception as e:
        logger.error("analysis_parse_error", error=str(e))
        return _create_default_analysis()


def _extract_from_text(analysis_text: str) -> Tuple[PaperAnalysis, List[Citation], str]:
    logger.info("extracting_analysis_from_text")
    
    try:
        summary = "No executive summary could be extracted."
        summary_match = re.search(r"(?:executive summary|summary)[:\s]+(.+?)(?:\n\n|$)", 
                                 analysis_text, re.IGNORECASE | re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()[:1000]
        
        findings = []
        findings_match = re.search(r"(?:key findings|findings)[:\s]+(.+?)(?:\n\n|$)", 
                                  analysis_text, re.IGNORECASE | re.DOTALL)
        if findings_match:
            findings_text = findings_match.group(1)
            findings = [f.strip() for f in re.findall(r"[-•*]\s*(.+)", findings_text)]
            if not findings:
                findings = [findings_text.strip()[:200]]
        
        if not findings:
            findings = ["Analysis completed but structured extraction failed"]
        
        methodology = "Methodology analysis not available in structured format."
        method_match = re.search(r"(?:methodology|methods)[:\s]+(.+?)(?:\n\n|$)", 
                                analysis_text, re.IGNORECASE | re.DOTALL)
        if method_match:
            methodology = method_match.group(1).strip()[:500]
        
        paper_analysis = PaperAnalysis(
            executive_summary=summary,
            key_findings=findings[:5],
            methodology=methodology,
            limitations=["Structured extraction of limitations was not successful"],
            future_work=["Structured extraction of future work was not successful"],
            technical_terms={}
        )
        
        logger.info("text_extraction_completed", 
                   summary_length=len(summary),
                   findings_count=len(findings))
        
        return paper_analysis, [], ""
        
    except Exception as e:
        logger.error("text_extraction_failed", error=str(e))
        return _create_default_analysis()


def _create_default_analysis() -> Tuple[PaperAnalysis, List[Citation], str]:
    logger.debug("creating_default_analysis")
    
    paper_analysis = PaperAnalysis(
        executive_summary="Analysis in progress...",
        key_findings=["Key findings being extracted..."],
        methodology="Methodology analysis in progress...",
        limitations=["Limitations being identified..."],
        future_work=["Future work suggestions being generated..."],
        technical_terms={},
    )
    
    return paper_analysis, [], ""


def analyze_paper(
    content: str, metadata: Optional[PaperMetadata], agent_team: Agent
) -> Dict[str, Any]:
    logger.info("analyzing_paper", has_metadata=metadata is not None)
    
    try:
        context = f"""
        Paper Metadata:
        Title: {metadata.title if metadata else "Unknown"}
        Authors: {", ".join(metadata.authors) if metadata else "Unknown"}
        Abstract: {metadata.abstract if metadata else "Not available"}
        
        Full Paper Content:
        {content}
        """
        
        analysis_prompt = _create_analysis_prompt(context)
        
        logger.info("requesting_agent_analysis")
        response = agent_team.run(analysis_prompt)
        
        paper_analysis, citations, visualization = parse_structured_analysis(
            response.content
        )
        
        results = {
            "raw_analysis": response.content,
            "structured_analysis": paper_analysis,
            "citations": citations,
            "visualization": visualization,
            "metadata": metadata,
        }
        
        logger.info(
            "paper_analysis_complete",
            has_structured_analysis=paper_analysis is not None,
            citations_count=len(citations)
        )
        return results
        
    except Exception as e:
        logger.error("paper_analysis_failed", error=str(e))
        raise


def _create_analysis_prompt(context: str) -> str:
    return f"""
    Please analyze this academic paper comprehensively and return the results in structured format:
    
    {context}
    
    Tasks:
    1. Analysis Agent: Generate structured analysis following PaperAnalysis schema
    2. Citation Agent: Extract important references following Citation schema  
    3. Visualization Agent: Create a Mermaid diagram showing main concepts
    
    Return your response in this JSON format:
    ```json
    {{
        "analysis": {{
            "executive_summary": "2-3 paragraph summary",
            "key_findings": ["finding1", "finding2", ...],
            "methodology": "methodology description", 
            "limitations": ["limitation1", "limitation2", ...],
            "future_work": ["suggestion1", "suggestion2", ...],
            "technical_terms": {{"term1": "definition1", "term2": "definition2"}}
        }},
        "citations": [
            {{"title": "Paper Title", "authors": ["Author1", "Author2"], "year": 2023, "venue": "Journal"}}
        ],
        "visualization": "mermaid diagram code here"
    }}
    ```
    """