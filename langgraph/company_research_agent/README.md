# Company Research Agent

A LangGraph-based React-pattern agent that performs comprehensive company research using web search and URL content extraction.

## Features

- **Web Search**: Uses Tavily API to search for company information across the web
- **URL Content Extraction**: Extracts and parses content from provided URLs
- **Specialized Company Research**: Targeted searches for different types of company information:
  - Company overview and history
  - Financial performance
  - Recent news and developments
  - Leadership and executives
  - Products and services
  - Market position and competitors
- **Intelligent Research Flow**: Automatically decides which tools to use based on user queries
- **Comprehensive Summaries**: Provides organized, actionable insights from multiple sources

## Prerequisites

1. Python 3.10 or higher
2. PostgreSQL database running on `localhost:5435`
3. API Keys:
   - OpenAI API key
   - Tavily API key

## Installation

1. Clone this repository and navigate to the project directory

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

5. Ensure PostgreSQL is running on `localhost:5435` with:
   - Username: `postgres`
   - Password: `postgres`
   - Database: `postgres`

## Usage

### Running with LangGraph Studio

The easiest way to interact with the agent is through LangGraph Studio:

```bash
langgraph dev
```

This will start the development server and provide you with:
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs

### Running Directly

You can run the agent directly:

```bash
python company_research_agent.py
```

The default example researches Apple Inc., but you can modify the `main()` function to research any company.

### Running Example Scripts

A comprehensive example script is provided to demonstrate different use cases:

```bash
python example_usage.py
```

This script demonstrates:
- Researching companies by name (Tesla)
- Analyzing companies from their website URL (NVIDIA)
- Researching startups and newer companies (OpenAI)
- Comparing multiple companies (Google vs Microsoft cloud services)

### Example Queries

1. **Research by company name**:
   ```
   "Research Microsoft Corporation and provide information about their cloud services, recent acquisitions, and financial performance."
   ```

2. **Research from a URL**:
   ```
   "Please analyze this company from their website: https://www.tesla.com and tell me about their latest products and innovations."
   ```

3. **Comprehensive company analysis**:
   ```
   "I need a complete analysis of Amazon including:
   - Business segments and revenue breakdown
   - Leadership team
   - Recent strategic initiatives
   - Competitive landscape
   - Financial health"
   ```

## Architecture

This agent uses the React (Reason-Act) pattern with the following components:

- **State Management**: Tracks conversation history using LangGraph's message system
- **Tools**:
  - `web_search`: General web search using Tavily
  - `extract_url_content`: Extracts and parses content from URLs
  - `search_company_info`: Specialized searches for different aspects of company information
- **Decision Making**: The LLM decides which tools to use based on the user's query
- **Persistence**: Uses PostgreSQL for conversation history and checkpointing

## Troubleshooting

1. **PostgreSQL Connection Error**: 
   - Ensure PostgreSQL is running on the correct port (5435)
   - Check credentials match those in the code

2. **API Key Errors**:
   - Verify your `.env` file exists and contains valid API keys
   - Ensure the keys have appropriate permissions

3. **Tool Execution Errors**:
   - Check internet connectivity for web searches
   - Some websites may block automated access; the agent will handle these gracefully

## Customization

You can extend the agent by:

1. **Adding new tools**: Create new `@tool` decorated functions
2. **Modifying the system prompt**: Update `TOOLS_SYSTEM_PROMPT` to change behavior
3. **Adding new information types**: Extend the `info_type` options in `search_company_info`

## License

This project is provided as-is for educational and research purposes. 