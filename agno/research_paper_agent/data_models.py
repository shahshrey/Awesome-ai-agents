"""Data models for Research Paper Analysis"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for a research paper"""
    title: str = Field(description="Title of the paper")
    authors: List[str] = Field(description="List of author names")
    abstract: str = Field(description="Paper abstract")
    publication_date: Optional[str] = Field(description="Publication date")
    venue: Optional[str] = Field(description="Publication venue/journal")
    doi: Optional[str] = Field(description="DOI if available")
    arxiv_id: Optional[str] = Field(description="arXiv ID if available")


class PaperAnalysis(BaseModel):
    """Structured analysis results for a paper"""
    executive_summary: str = Field(description="2-3 paragraph executive summary")
    key_findings: List[str] = Field(
        description="List of key findings and contributions"
    )
    methodology: str = Field(description="Description of methodology used")
    limitations: List[str] = Field(description="Identified limitations")
    future_work: List[str] = Field(description="Suggested future work")
    technical_terms: Dict[str, str] = Field(
        description="Key technical terms and their explanations"
    )


class Citation(BaseModel):
    """Citation information"""
    title: str = Field(description="Citation title")
    authors: List[str] = Field(description="Citation authors")
    year: Optional[int] = Field(description="Publication year")
    venue: Optional[str] = Field(description="Publication venue")
