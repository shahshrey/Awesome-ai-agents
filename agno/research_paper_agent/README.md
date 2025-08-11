# Research Paper Analysis Agent 📚

An AI-powered tool for analyzing academic papers using a team of specialized agents. Get comprehensive insights, summaries, and visualizations from research papers with just a few clicks.

## Features

### 🎯 Core Capabilities
- **Executive Summaries**: Generate concise summaries capturing the essence of papers
- **Key Findings Extraction**: Identify and highlight main contributions and discoveries
- **Methodology Analysis**: Break down research methods in accessible terms
- **Citation Management**: Extract references and generate BibTeX entries
- **Visual Concept Maps**: Create Mermaid diagrams showing relationships between concepts
- **Technical Term Glossary**: Explain complex jargon for broader audiences
- **Analysis History**: Track previously analyzed papers with session storage

### 🤖 Agent Team Architecture
The application uses an **Agent Team** pattern with four specialized agents:

1. **Paper Extractor Agent**: Handles PDF parsing, content extraction, and metadata identification
2. **Analysis Agent**: Performs deep analysis including executive summaries, key findings, methodology breakdown, limitations, and future work
3. **Citation Agent**: Manages references, extracts citations, and generates BibTeX entries
4. **Visualization Agent**: Creates Mermaid diagrams and visual representations of paper concepts

All agents coordinate through a main **Research Paper Analysis Team** orchestrator using GPT-4o.

### 📥 Multiple Input Methods
- **Upload PDF files**: Direct PDF upload with PyPDF2 text extraction
- **arXiv URLs**: Paste arXiv URLs (e.g., `https://arxiv.org/abs/2301.00001`) for automatic metadata and PDF fetching
- **Topic Search**: Search arXiv by keywords to discover papers (returns top 5 results with URLs to copy)

## Project Structure

```
research_paper_agent/
├── app.py              # Main Streamlit application UI
├── agent.py            # Agent creation and paper analysis logic
├── utils.py            # Utility functions (PDF extraction, arXiv fetching)
├── data_models.py      # Pydantic data models
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Setup

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (GPT-5-mini access required)

### Installation

1. cd to the project directory:
```bash
cd research_paper_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## Usage

### Getting Started
1. Enter your OpenAI API key in the sidebar
2. Choose your input method:
   - Upload a PDF file
   - Paste an arXiv URL  
   - Search for papers by topic/keywords

### Analysis Process
1. **Upload/Input**: Provide your paper through one of the input methods
2. **Processing**: The agent team analyzes the paper (takes 30-60 seconds)
3. **Review Results**: Explore the analysis through organized tabs:
   - 📊 **Summary**: Executive summary with paper metrics (authors, date, venue, arXiv ID)
   - 🔍 **Detailed Analysis**: Full comprehensive analysis from all agents
   - 📚 **Citations**: References and citation information 
   - 🗺️ **Visualization**: Mermaid concept maps (when generated)
   - 📋 **Export**: BibTeX entries and markdown download options

### Analysis History
- View previously analyzed papers in the sidebar
- Click on any paper to reload its analysis
- Session-based storage (resets on app restart)

### Export Options
- **BibTeX**: Automatically generated citation entries with proper formatting
- **Markdown**: Download complete analysis as a markdown file with timestamp
- **Mermaid Diagrams**: Visual concept maps displayed inline

## Example Use Cases

### For Graduate Students
- Quickly understand papers for literature reviews
- Extract key methodologies for research proposals
- Generate proper citations for thesis work
- Build concept maps for complex topics

### For Researchers
- Stay updated with latest developments in your field
- Compare methodologies across papers
- Identify research gaps and opportunities
- Extract technical details efficiently

### For Industry Professionals  
- Extract practical insights from academic research
- Understand technical papers without deep domain knowledge
- Find relevant research for product development
- Build knowledge base from academic literature

## API Configuration

The application requires an OpenAI API key with GPT-4o access:
- [OpenAI Platform](https://platform.openai.com/api-keys)

Enter your API key in the sidebar configuration panel. The key is stored only in your session and is not saved permanently.

## Technical Details

### Models Used
- **GPT-5-mini**: All agents use GPT-5-mini for consistency and quality
- **arXiv API**: Paper metadata and search functionality  
- **No external search tools**: Built-in arXiv integration only

### Libraries & Dependencies
- **Streamlit**: Web interface and UI components
- **PyPDF2**: PDF text extraction and parsing
- **Agno**: Agent framework for multi-agent coordination
- **Pydantic**: Data validation and structured models
- **Requests**: HTTP requests for arXiv API integration

### Data Models
- **PaperMetadata**: Structured paper information (title, authors, abstract, etc.)
- **PaperAnalysis**: Analysis results schema (summary, findings, methodology, etc.)
- **Citation**: Reference information structure

### Content Processing
- PDF content limited to first 10,000 characters for token management
- Automatic arXiv ID extraction from URLs
- Regex-based XML parsing for arXiv API responses
- Session state management for analysis history

## Limitations

- **PDF Quality**: Text extraction depends on PDF structure (not suitable for scanned images)
- **arXiv Only**: Search functionality limited to arXiv papers only
- **Session Storage**: Analysis history resets when application restarts
- **Rate Limits**: arXiv API may have rate limits for frequent requests
- **GPT-5-mini Required**: Requires OpenAI API access with GPT-5-mini model availability
