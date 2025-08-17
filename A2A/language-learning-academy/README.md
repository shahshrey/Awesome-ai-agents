# 🎓 Language Learning Academy - A2A Agent with LangGraph

An intelligent AI-powered language learning assistant built with **A2A (Agent-to-Agent) SDK** and **LangGraph** for advanced conversational learning experiences. This agent provides vocabulary lessons, grammar explanations, conversation practice, and interactive quizzes across multiple languages.

## 🌟 Features

- **📚 Vocabulary Lessons**: Learn new words and phrases with categorized vocabulary by difficulty level
- **📖 Grammar Lessons**: Master grammar rules, verb conjugations, and sentence structures
- **💬 Conversation Practice**: Practice real-world conversations with scenario-based dialogues
- **🧠 Interactive Quizzes**: Test your knowledge with customizable quizzes on vocabulary and grammar
- **🌍 Translation Services**: Context-aware translation between supported languages
- **🎯 Personalized Learning**: Adaptive teaching style for beginner, intermediate, and advanced levels
- **🔄 Streaming Responses**: Real-time streaming for interactive learning experiences
- **🎨 Web Interface**: Beautiful Streamlit-powered UI for seamless interaction

## 🏗️ Architecture

This agent combines several cutting-edge technologies:

- **A2A SDK**: Provides the agent framework and communication protocols
- **LangGraph**: Orchestrates complex language learning workflows with state management
- **LangChain**: Powers the LLM integrations and tool management
- **OpenAI GPT-4**: Advanced language model for natural language understanding
- **Streamlit**: Modern web interface for user interaction
- **Structured Logging**: Comprehensive logging with structlog

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv package manager
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd language-learning-academy
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export OPENAI_MODEL="gpt-4o"  # Optional, defaults to gpt-4o
   ```

### Running the Application

**Start the complete system (Agent + Web UI):**
```bash
uv run scripts/start_full_ui.py
```

This will:
- ✅ Start the A2A agent on `http://localhost:9999`
- ✅ Start the Streamlit web interface on `http://localhost:8501`
- ✅ Open your browser automatically
- ✅ Health check both services

**Run individual services:**

*Agent only:*
```bash
cd src && uv run python -m language_learning_academy.server.main
```

*Web UI only:*
```bash
uv run python -m streamlit run src/language_learning_academy/ui/streamlit_app.py --server.port 8501
```

## 🌍 Supported Languages

- **Spanish** 🇪🇸
- **French** 🇫🇷  
- **German** 🇩🇪
- **Italian** 🇮🇹
- **Portuguese** 🇵🇹
- **Japanese** 🇯🇵
- **Chinese** 🇨🇳
- **Korean** 🇰🇷

## 🛠️ Agent Skills

### 1. Vocabulary Lessons (`vocabulary_lesson`)
Learn new words and phrases with categorized vocabulary by difficulty level.

**Examples:**
- "Teach me Spanish vocabulary for beginners"
- "Show me intermediate French words"
- "I want to learn German vocabulary"

### 2. Grammar Lessons (`grammar_lesson`)
Master grammar rules, verb conjugations, and sentence structures.

**Examples:**
- "Explain Spanish present tense conjugation"
- "Show me French past tense rules"
- "Teach me German grammar basics"

### 3. Conversation Practice (`conversation_practice`)
Practice real-world conversations with scenario-based dialogues.

**Examples:**
- "Practice restaurant conversation in Spanish"
- "Show me a French café dialogue"
- "Help me with directions conversation in Italian"

### 4. Interactive Quizzes (`language_quiz`)
Test your knowledge with customizable quizzes.

**Examples:**
- "Quiz me on Spanish vocabulary"
- "Test my French grammar knowledge"
- "Give me a reverse translation quiz in German"

### 5. Language Information (`language_info`)
Get information about supported languages and services.

**Examples:**
- "What languages do you support?"
- "Show me available services"
- "Help me get started"

## 🔌 API Usage

### Agent Card
```bash
curl http://localhost:9999/.well-known/agent-card.json
```

### Health Check
The startup script automatically performs health checks using the agent card endpoint.

### A2A Protocol
The agent implements the A2A protocol for seamless integration with other A2A-compatible systems.

## 🧩 LangGraph Integration

The agent uses LangGraph's `create_react_agent` with:

- **Memory Management**: Persistent conversation state with `MemorySaver`
- **Tool Integration**: Five specialized language learning tools
- **Response Formatting**: Structured responses with status management
- **Streaming Support**: Real-time response streaming for interactive experiences

### Tool Architecture

```python
tools = [
    get_vocabulary_lesson,      # Vocabulary learning
    get_grammar_lesson,         # Grammar explanations  
    get_conversation_practice,  # Dialogue scenarios
    create_language_quiz,       # Interactive quizzes
    translate_with_context      # Context-aware translation
]
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o` |
| `SERVER_HOST` | Agent server host | `0.0.0.0` |
| `SERVER_PORT` | Agent server port | `9999` |

### Learning Levels

- **Beginner**: Basic vocabulary and simple grammar
- **Intermediate**: Complex structures and expanded vocabulary
- **Advanced**: Nuanced language usage and cultural context

## 📁 Project Structure

```
language-learning-academy/
├── src/
│   └── language_learning_academy/
│       ├── agent/
│       │   └── executor.py          # LangGraph agent implementation
│       ├── server/
│       │   └── main.py              # A2A server setup
│       └── ui/
│           └── streamlit_app.py     # Web interface
├── scripts/
│   └── start_full_ui.py             # Launcher script
├── pyproject.toml                   # Project configuration
└── README.md                        # This file
```

## 🔧 Development

### Running Tests
```bash
uv run pytest tests/
```

### Code Quality
The project follows these conventions:
- Structured logging with `structlog`
- Type hints with Pydantic models
- Error handling with try-except blocks
- Early returns and functional programming patterns

### Adding New Languages
1. Update the `SYSTEM_INSTRUCTION` in `executor.py`
2. Add language-specific examples to skills
3. Update this README's supported languages section

### Adding New Skills
1. Create a new `@tool` function in `executor.py`
2. Add the tool to the `tools` list
3. Create corresponding `AgentSkill` definition in `main.py`
4. Update the agent card skills list

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding conventions
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is built on the A2A SDK and follows open-source principles. See individual package licenses for more details.

## 🆘 Troubleshooting

### Common Issues

**Agent fails to start:**
- Ensure `OPENAI_API_KEY` is set
- Check that ports 9999 and 8501 are available
- Verify Python 3.10+ is installed

**Streamlit won't start:**
- Try running `uv run python -m streamlit --help` to verify installation
- Check for corrupted executable paths

**LangGraph errors:**
- Ensure all tool functions have proper descriptions
- Verify OpenAI API key has sufficient credits

### Logs
The agent uses structured logging. Check console output for detailed error information with timestamps and context.

---

Built with ❤️ using A2A SDK, LangGraph, and modern Python tooling.
