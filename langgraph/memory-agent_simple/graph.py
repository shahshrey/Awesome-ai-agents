"""Memory agent graph implementation."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from langgraph.graph import END, StateGraph, add_messages
from langgraph.store.base import BaseStore
from pydantic import BaseModel, Field
from typing_extensions import Annotated

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = (
    "You are a helpful and friendly chatbot. Get to know the user! "
    "Ask questions! Be spontaneous! "
    "{user_info}\n\n"
    "System Time: {time}\n"
)
llm = init_chat_model(model="gpt-4o-mini", model_provider="openai")

# ====================================================================
# State
# ====================================================================

class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]

# ====================================================================
# Schema
# ====================================================================

class SaveOrUpdateMemoryToolInput(BaseModel):
    content: str = Field(description="The main content of the memory.")
    additional_context: str = Field(description="Additional context for the memory.")
    existing_memory_id: Optional[uuid.UUID] = None


# ====================================================================
# Tools
# ====================================================================

@tool
async def save_or_update_memory(
    memory_input: SaveOrUpdateMemoryToolInput,
    *,
    config: Annotated[RunnableConfig, InjectedToolArg],
    store: Annotated[BaseStore, InjectedToolArg],
):
    """Upsert a memory in the database.

    If a memory conflicts with an existing one, then just UPDATE the
    existing one by passing in existing_memory_id - don't create two memories
    that are the same. If the user corrects a memory, UPDATE it.

    Always store the memory in the database after the user provides
    any new information.

    Args:
        memory_input: The memory input containing content and context.
        existing_memory_id: ONLY PROVIDE IF UPDATING AN EXISTING MEMORY.
        The memory to overwrite.
    """
    # Generate or use existing memory ID
    memory_id = memory_input.existing_memory_id or uuid.uuid4()

    user_id = config.get("configurable", {}).get("user_id", "default")
    if not user_id:
        user_id = "default"

    await store.aput(
        namespace=("memories", user_id),
        key=str(memory_id),
        value={
            "content": memory_input.content,
            "additional_context": memory_input.additional_context,
        },
    )

    return f"Stored memory {memory_id}"




# ====================================================================
# Nodes
# ====================================================================


async def generate_response(
    state: AgentState, config: RunnableConfig, *, store: BaseStore  
) -> dict:
    """Call the language model with context from stored memories."""

    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id", "default")
    system_prompt_template = configurable.get(
        "system_prompt", SYSTEM_PROMPT_TEMPLATE
    )

    recent_messages = state.messages[-3:]
    memories = await store.asearch(
        ("memories", user_id),
        query=str([message.content for message in recent_messages]),
        limit=10,
    )

    if memories:
        formatted_memories = "\n".join(
            [f"[{memory.key}]: {memory.value} "
             f"(similarity: {memory.score})"
             for memory in memories]
        )
        user_info = f"""
<memories>
{formatted_memories}
</memories>
"""
    else:
        user_info = ""

    system_prompt = system_prompt_template.format(
        user_info=user_info, time=datetime.now().isoformat()
    )
    input_messages = [
        {"role": "system", "content": system_prompt}
    ] + state.messages

    llm_with_tools = llm.bind_tools(
        [save_or_update_memory],
    )
    response_message = await llm_with_tools.ainvoke(input_messages)
    return {"messages": [response_message]}


async def handle_tool_calls(
    state: AgentState, config: RunnableConfig, *, store: BaseStore
):
    last_message = state.messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return {"messages": []}

    saved_memories = await asyncio.gather(
        *[
            save_or_update_memory.ainvoke(
                tool_call["args"] | {"store": store},
                config=config
            )
            for tool_call in tool_calls
        ]
    )

    tool_results = [
        ToolMessage(
            content=result,
            tool_call_id=tool_call["id"],
        )
        for result, tool_call in zip(saved_memories, tool_calls)
    ]

    return {"messages": tool_results}
       

def decide_next_step(state: AgentState):
    """Determine the next step based on the presence of tool calls."""
    last_message = state.messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "handle_tool_calls"
    return END

# ====================================================================
# Graph
# ====================================================================


builder = StateGraph(AgentState)

builder.add_node(generate_response)
builder.add_node(handle_tool_calls)

builder.add_edge("__start__", "generate_response")
builder.add_conditional_edges(
    "generate_response", decide_next_step, ["handle_tool_calls", END]
)
builder.add_edge("handle_tool_calls", "generate_response")

graph = builder.compile()
graph.name = "MemoryAgent"

__all__ = ["graph", "AgentState"]
