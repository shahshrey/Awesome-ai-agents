import asyncio
import os
import json
from typing import Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage, AnyMessage, HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# ─── 1. Configuration ────────────────────────────────────────────────────────────────
MODEL_NAME = "gpt-4o"
DB_URI = "postgresql://postgres:postgres@localhost:5435/postgres"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Disable noisy HTTP logs
for log_name in ["httpx", "httpcore"]:
    logging.getLogger(log_name).setLevel(logging.WARNING)

TOOLS_SYSTEM_PROMPT = """You are a company research assistant that specializes in gathering comprehensive information about businesses.

Your capabilities include:
1. Searching the web for company information using Tavily search
2. Extracting content from company websites and other URLs
3. Analyzing and summarizing company data including:
   - Company overview and history
   - Products and services
   - Market position and competitors
   - Financial information (if publicly available)
   - Recent news and developments
   - Key personnel and leadership
   - Company culture and values

When researching a company:
- Start with a broad search if only the company name is provided
- If a URL is provided, extract information from that specific page first
- Use multiple searches to gather comprehensive information
- Cross-reference information from multiple sources
- Present findings in a clear, organized manner

Be thorough but concise in your research. Focus on providing actionable insights."""

# ─── 2. State Definition ─────────────────────────────────────────────────────────────
class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages] = Field(default=[])

# ─── 3. Tools ────────────────────────────────────────────────────────────────────────
@tool
async def web_search(query: str) -> str:
    """Search the web for information using Tavily."""
    try:
        logger.info(f"Searching web for: {query}")
        # Run the synchronous Tavily client in a thread to avoid blocking
        import asyncio
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth="advanced",
            max_results=5
        )
        
        # Format the results for better readability
        formatted_results = []
        for idx, result in enumerate(response.get('results', []), 1):
            formatted_result = {
                "title": result.get('title', 'No title'),
                "url": result.get('url', 'No URL'),
                "content": result.get('content', 'No content available')
            }
            formatted_results.append(formatted_result)
        
        logger.info(f"Found {len(formatted_results)} search results")
        return json.dumps(formatted_results, indent=2)
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return f"Error searching the web: {str(e)}"

@tool
async def extract_url_content(url: str) -> str:
    """Extract and parse content from a given URL."""
    try:
        logger.info(f"Extracting content from URL: {url}")
        
        # Use async httpx client
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "meta", "link"]):
                element.decompose()
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract metadata
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else "No title"
            
            metadata = {
                "title": title,
                "description": "",
                "url": url
            }
            
            # Try to get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and hasattr(meta_desc, 'attrs'):
                desc_content = meta_desc.attrs.get('content', '')
                if isinstance(desc_content, str):
                    metadata["description"] = desc_content
            
            # Limit content length to avoid token limits
            max_length = 5000
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "... [Content truncated]"
            
            result = {
                "metadata": metadata,
                "content": text_content
            }
            
            logger.info(f"Successfully extracted {len(text_content)} characters from URL")
            return json.dumps(result, indent=2)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error extracting URL content: {str(e)}")
        return f"HTTP error {e.response.status_code}: Could not access the URL"
    except Exception as e:
        logger.error(f"Error extracting URL content: {str(e)}")
        return f"Error extracting content from URL: {str(e)}"

@tool
async def search_company_info(company_name: str, info_type: str = "general") -> str:
    """Search for specific types of company information.
    
    Args:
        company_name: The name of the company to research
        info_type: Type of information to search for. Options include:
            - general: General company information
            - financial: Financial data and performance
            - news: Recent news and developments
            - leadership: Key personnel and executives
            - products: Products and services
            - competitors: Market position and competitors
    """
    try:
        logger.info(f"Searching {info_type} information for: {company_name}")
        
        # Construct search query based on info type
        query_map = {
            "general": f"{company_name} company overview profile",
            "financial": f"{company_name} revenue financial performance earnings",
            "news": f"{company_name} latest news recent developments",
            "leadership": f"{company_name} CEO executives leadership team",
            "products": f"{company_name} products services offerings",
            "competitors": f"{company_name} competitors market share industry position"
        }
        
        query = query_map.get(info_type, f"{company_name} {info_type}")
        
        # Run the synchronous Tavily client in a thread to avoid blocking
        import asyncio
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth="advanced",
            max_results=3
        )
        
        # Format results with context
        formatted_results = {
            "search_type": info_type,
            "company": company_name,
            "results": []
        }
        
        for result in response.get('results', []):
            formatted_results["results"].append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "content": result.get('content', '')
            })
        
        logger.info(f"Found {len(formatted_results['results'])} results for {info_type} search")
        return json.dumps(formatted_results, indent=2)
        
    except Exception as e:
        logger.error(f"Error in company info search: {str(e)}")
        return f"Error searching for {info_type} information: {str(e)}"

# Collect all tools
GLOBAL_TOOLS = [web_search, extract_url_content, search_company_info]
TOOLS = {tool.name: tool for tool in GLOBAL_TOOLS}

# ─── 4. Node Functions ───────────────────────────────────────────────────────────────
async def call_tools_llm(state: AgentState):
    """Main LLM node that processes messages and decides on tool usage."""
    messages = state.messages
    system_message = SystemMessage(content=TOOLS_SYSTEM_PROMPT)
    messages = [system_message, *messages]
    
    tool_calling_model = ChatOpenAI(model=MODEL_NAME).bind_tools(GLOBAL_TOOLS)
    ai_message = await tool_calling_model.ainvoke(messages)
    
    return {"messages": [ai_message]}

async def invoke_tools(state: AgentState):
    """Execute tool calls requested by the LLM."""
    tool_messages = []
    tool_calls = state.messages[-1].tool_calls
    
    for t in tool_calls:
        if t["name"] not in TOOLS:
            result = "Invalid tool name."
        else:
            tool = TOOLS[t["name"]]
            logger.info(f"Invoking tool '{t['name']}' with args: {t['args']}")
            try:
                result = await tool.ainvoke(t["args"])
            except Exception as e:
                logger.error(f"Error invoking tool '{t['name']}': {str(e)}")
                result = f"Error executing tool: {str(e)}"
        
        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=t["id"],
                name=t["name"]
            )
        )
    
    return {"messages": tool_messages}

def determine_next_action(state: AgentState):
    """Determine whether to invoke tools or end the conversation."""
    last_message = state.messages[-1]
    
    # Check if the message has tool_calls and they are not empty
    if hasattr(last_message, "tool_calls") and getattr(last_message, "tool_calls", None):
        return "invoke_tools"
    else:
        return END

# ─── 5. Build Graph ──────────────────────────────────────────────────────────────────
def build_agent():
    """Construct the LangGraph agent."""
    agent = StateGraph(AgentState)
    
    # Add nodes
    agent.add_node("call_tools_llm", call_tools_llm)
    agent.add_node("invoke_tools", invoke_tools)
    
    # Set entry point
    agent.set_entry_point("call_tools_llm")
    
    # Add conditional edges
    agent.add_conditional_edges(
        "call_tools_llm",
        determine_next_action,
        {
            "invoke_tools": "invoke_tools",
            END: END,
        },
    )
    
    # Add edge from tools back to LLM
    agent.add_edge("invoke_tools", "call_tools_llm")
    
    return agent

# Build the agent
agent_builder = build_agent()

# ─── 6. Main Function ────────────────────────────────────────────────────────────────
async def main():
    """Main function to run the agent with example usage."""
    # Example usage - research a company
    message_content = """
Research Apple Inc. for me. I want to know about:
1. Company overview and history
2. Main products and services
3. Recent news and developments
4. Key leadership
5. Financial performance

Please provide a comprehensive summary.
"""
    
    messages_input = [
        HumanMessage(content=message_content)
    ]
    
    # Try to use PostgreSQL checkpointer if available, otherwise run without persistence
    try:
        async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
            # Ensure tables are created
            await checkpointer.setup()
            agent = agent_builder.compile(checkpointer=checkpointer)
            logger.info("Using PostgreSQL checkpointer for persistence")
            
            logger.info("Starting company research...")
            
            result = await agent.ainvoke(
                {"messages": messages_input},
                config={"configurable": {"thread_id": 1}},
            )
            
            if result["messages"]:
                print("\n" + "="*80)
                print("COMPANY RESEARCH RESULTS")
                print("="*80 + "\n")
                print(result["messages"][-1].content)
            else:
                print("No messages in the result.")
                
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL, running without persistence: {e}")
        agent = agent_builder.compile()
        
        logger.info("Starting company research...")
        
        result = await agent.ainvoke(
            {"messages": messages_input},
            config={"configurable": {"thread_id": 1}},
        )
        
        if result["messages"]:
            print("\n" + "="*80)
            print("COMPANY RESEARCH RESULTS")
            print("="*80 + "\n")
            print(result["messages"][-1].content)
        else:
            print("No messages in the result.")

if __name__ == "__main__":
    asyncio.run(main()) 