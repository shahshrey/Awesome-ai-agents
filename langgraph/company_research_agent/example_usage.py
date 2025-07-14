import asyncio
from langchain_core.messages import HumanMessage
from company_research_agent import agent_builder
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def research_company_by_name():
    """Example: Research a company by name"""
    agent = agent_builder.compile()
    
    message = HumanMessage(content="""
    Research Tesla Inc. for me. Focus on:
    - Their electric vehicle lineup
    - Recent innovations and technology
    - Market position and competition
    - Environmental impact initiatives
    """)
    
    result = await agent.ainvoke(
        {"messages": [message]},
        config={"configurable": {"thread_id": 2}}
    )
    
    return result["messages"][-1].content

async def research_company_by_url():
    """Example: Research a company from their website URL"""
    agent = agent_builder.compile()
    
    message = HumanMessage(content="""
    Please analyze this company from their website: https://www.nvidia.com
    I want to know about their AI products, recent developments, and market leadership in GPU technology.
    """)
    
    result = await agent.ainvoke(
        {"messages": [message]},
        config={"configurable": {"thread_id": 3}}
    )
    
    return result["messages"][-1].content

async def research_startup():
    """Example: Research a startup or smaller company"""
    agent = agent_builder.compile()
    
    message = HumanMessage(content="""
    Research OpenAI for me. I need information about:
    - Their mission and founding story
    - Main AI products and services
    - Recent breakthroughs and research
    - Business model and partnerships
    """)
    
    result = await agent.ainvoke(
        {"messages": [message]},
        config={"configurable": {"thread_id": 4}}
    )
    
    return result["messages"][-1].content

async def compare_companies():
    """Example: Research for comparing companies"""
    agent = agent_builder.compile()
    
    message = HumanMessage(content="""
    Research both Google and Microsoft focusing on their cloud computing services.
    I need to understand their offerings, market share, and competitive advantages.
    """)
    
    result = await agent.ainvoke(
        {"messages": [message]},
        config={"configurable": {"thread_id": 5}}
    )
    
    return result["messages"][-1].content

async def main():
    """Run example queries"""
    print("Company Research Agent Examples\n" + "="*80 + "\n")
    
    # Example 1: Research by company name
    print("1. Researching Tesla by name...")
    print("-" * 40)
    try:
        tesla_research = await research_company_by_name()
        print(tesla_research)
    except Exception as e:
        logger.error(f"Error researching Tesla: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: Research by URL
    print("2. Researching NVIDIA from their website...")
    print("-" * 40)
    try:
        nvidia_research = await research_company_by_url()
        print(nvidia_research)
    except Exception as e:
        logger.error(f"Error researching NVIDIA: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Example 3: Research a startup
    print("3. Researching OpenAI...")
    print("-" * 40)
    try:
        openai_research = await research_startup()
        print(openai_research)
    except Exception as e:
        logger.error(f"Error researching OpenAI: {e}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 