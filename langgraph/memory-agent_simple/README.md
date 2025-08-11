## Memory Agent (LangGraph)

A small, tool-aware chatbot that persistently remembers user facts and context. It retrieves relevant memories on every turn and lets the model decide when to upsert new or corrected memories.

### Highlights
- **Tool-aware chat**: The model can call `save_or_update_memory` to upsert user memories.
- **Semantic recall**: The last 3 user/AI messages are used as the search query to retrieve similar memories for grounding.
- **Reactive loop**: `generate_response → handle_tool_calls → generate_response` until no further tool calls are needed.
- **Pluggable store**: Uses the LangGraph Store configured in `langgraph.json` with OpenAI embeddings for similarity search.

### What’s included
- `graph.py`: Compiled LangGraph with two nodes and a single tool.
- `langgraph.json`: LangGraph CLI config, including the store index embeddings.
- `.env.example`: Example environment file with placeholders.

### How it works
- The system prompt is built from a template and augmented with retrieved memories.
- The model `gpt-4o-mini` is bound to the tool `save_or_update_memory`.
- If the model decides to write or correct a memory, it emits a tool call; the graph executes it and loops.
- Memories are stored under the namespace `("memories", user_id)` where `user_id` is read from the graph config (`config.configurable.user_id`) and defaults to `default`.

### Tool schema
- `save_or_update_memory(memory_input: SaveOrUpdateMemoryToolInput)`
- `SaveOrUpdateMemoryToolInput` fields:
  - `content: str`
  - `additional_context: str`
  - `existing_memory_id: Optional[UUID]`

When `existing_memory_id` is provided, the tool updates that memory; otherwise, it creates a new one.

### Retrieval strategy
- On each turn, the graph queries the store using a joined string of the last three message contents and returns up to 10 similar memories.
- The retrieved memories are formatted and injected into the system message for grounding.

### Requirements
- Python 3.11
- An OpenAI API key

### Setup
1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Provide credentials

```bash
cp .env.example .env
```
Set `OPENAI_API_KEY` in your shell or in `.env`.

### Run the dev server

```bash
langgraph dev
```

- API: http://127.0.0.1:2024
- Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Docs: http://127.0.0.1:2024/docs

### Interact via Python

```python
from graph import graph
from langchain_core.messages import HumanMessage

state = {"messages": [HumanMessage(content="Hi! I am Alex. I live in Berlin.")]} 
config = {"configurable": {"user_id": "alex"}}
result = graph.invoke(state, config=config)
print(result["messages"][-1].content)
```

### Interact via cURL

```bash
curl -s -X POST \
  http://127.0.0.1:2024/invoke/agent \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"messages": [{"type": "human", "content": "Hi! I am Alex. I live in Berlin."}]},
    "config": {"configurable": {"user_id": "alex"}}
  }'
```

### Interact via Studio
- Start the dev server.
- Open the Studio link.
- Select the `agent` graph and send a message.
- Optionally set `configurable.user_id` to separate user memory namespaces.

### Configuration
- Model: `gpt-4o-mini` in `graph.py`.
- Store: `langgraph.json` sets an index with `dims: 1536` and `embed: openai:text-embedding-3-small`.
- Prompt: You can pass a custom system prompt via `config={"configurable": {"system_prompt": "..."}}`.

### Memory behavior
- Namespace: `( "memories", user_id )`
- Key: a UUID string, generated unless `existing_memory_id` is provided
- Value: `{ "content": str, "additional_context": str }`

### Troubleshooting
- If the model never calls the tool, provide clearer, memory-worthy info in your message.
- If memories are not retrieved, confirm `OPENAI_API_KEY` is set and the embedding model is available.
- If you change the embedding model, ensure `dims` in `langgraph.json` matches the model’s vector size.
