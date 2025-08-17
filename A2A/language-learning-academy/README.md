# 🎓 Language Learning Academy - A2A Agent with LangGraph

An intelligent AI-powered language learning assistant built with **A2A (Agent-to-Agent) SDK** and **LangGraph** for advanced conversational learning experiences. This agent provides vocabulary lessons, grammar explanations, conversation practice, and interactive quizzes across multiple languages with **full personalization** and **multi-language interface support**.

## 🌟 Features

- **📚 Vocabulary Lessons**: Learn new words and phrases with categorized vocabulary by difficulty level
- **📖 Grammar Lessons**: Master grammar rules, verb conjugations, and sentence structures
- **💬 Conversation Practice**: Practice real-world conversations with scenario-based dialogues
- **🧠 Interactive Quizzes**: Test your knowledge with customizable quizzes on vocabulary and grammar
- **🌍 Translation Services**: Context-aware translation between supported languages
- **🎯 Personalized Learning**: Fully customizable AI tutor that adapts to your preferences:
  - **Native Language**: Get explanations in your preferred language (English, Hindi, French, Spanish, German, Italian, Portuguese, Japanese, Chinese, Korean)
  - **Learning Goals**: Optimize content for Travel, Business, or Exam preparation
  - **Tutor Persona**: Choose between Friendly, Formal, or Coach teaching styles
  - **Correction Strictness**: Adjust error correction from Gentle to Standard to Strict
- **🌐 Multi-Language Interface**: Complete UI translation in English, Hindi (हिन्दी), and French (Français)
- **🔄 Streaming Responses**: Real-time streaming for interactive learning experiences
- **🎨 Beautiful Web Interface**: Modern Streamlit-powered UI with personalized learning dashboard

## 🏗️ Architecture

This agent combines several cutting-edge technologies:

- **A2A SDK**: Provides the agent framework and communication protocols
- **LangGraph**: Orchestrates complex language learning workflows with state management
- **LangChain**: Powers the LLM integrations and tool management
- **OpenAI gpt-5-2025-08-07**: Advanced language model for natural language understanding
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
   export OPENAI_MODEL="gpt-5-2025-08-07"  # Optional, defaults to gpt-5-2025-08-07
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
- ✅ Launch with full personalization and multi-language support

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

### Learning Languages (8 supported)
- **Spanish** 🇪🇸
- **French** 🇫🇷  
- **German** 🇩🇪
- **Italian** 🇮🇹
- **Portuguese** 🇵🇹
- **Japanese** 🇯🇵
- **Chinese** 🇨🇳
- **Korean** 🇰🇷

### Interface Languages (3 supported)
- **English** 🇺🇸 - Complete UI translation
- **Hindi (हिन्दी)** 🇮🇳 - Complete UI translation  
- **French (Français)** 🇫🇷 - Complete UI translation

### Native Language Support (10 supported)
Your AI tutor can provide explanations and meta-commentary in any of these languages:
**English, Hindi, French, Spanish, German, Italian, Portuguese, Japanese, Chinese, Korean**

## 🎨 Personalization Features

### 🌍 **Multi-Language Experience**
- **Interface Language**: Switch the entire UI between English, Hindi (हिन्दी), and French (Français)
- **Native Language**: Get AI explanations in your preferred language (10 supported)
- **Target Language**: Learn any of 8 supported languages

### 🎯 **Adaptive Learning Style**
- **Learning Goals**: Optimize content for Travel, Business, or Exam preparation
- **Tutor Persona**: Choose between Friendly, Formal, or Coach teaching styles  
- **Correction Level**: Adjust feedback from Gentle to Standard to Strict

### 💾 **Session-Based Preferences**
- All settings are stored in your browser session
- Preferences apply to all learning activities
- Settings reset when you refresh the page (no data persistence)

### 🔄 **Real-Time Adaptation**
- AI responses immediately adapt to your preferences
- Teaching style changes based on your persona selection
- Content focus shifts according to your learning goals

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
| `OPENAI_MODEL` | OpenAI model to use | `gpt-5-2025-08-07` |
| `SERVER_HOST` | Agent server host | `0.0.0.0` |
| `SERVER_PORT` | Agent server port | `9999` |

### Learning Levels

- **Beginner**: Basic vocabulary and simple grammar
- **Intermediate**: Complex structures and expanded vocabulary
- **Advanced**: Nuanced language usage and cultural context

### Personalization Settings

The application offers comprehensive personalization through the sidebar:

#### Profile Settings
- **Native Language**: Choose from 10 supported languages for AI explanations
- **UI Language**: Switch interface between English, Hindi, and French

#### Learning Preferences  
- **Learning Goal**:
  - **Travel**: Focus on practical phrases, cultural etiquette, and survival vocabulary
  - **Business**: Emphasize formal language, professional communication, and industry terms
  - **Exam Prep**: Focus on grammar rules, academic vocabulary, and test-taking strategies

- **Tutor Persona**:
  - **Friendly**: Warm, encouraging, and supportive with casual language
  - **Formal**: Professional, academic tone with precise and structured responses
  - **Coach**: Motivating and goal-oriented with constructive feedback

- **Correction Strictness**:
  - **Gentle**: Point out errors softly, focus on communication over perfection
  - **Standard**: Balance error correction with encouragement
  - **Strict**: Correct all errors thoroughly with detailed explanations

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

**Personalization not working:**
- Check that profile data is being sent in the `metadata` field (not `meta`)
- Verify that the UI language change triggers a page refresh
- Ensure all translation keys are present in the `TRANSLATIONS` dictionary

**UI language not changing:**
- The interface should auto-refresh when changing UI Language in the sidebar
- If not, manually refresh the browser page
- Check browser console for any JavaScript errors

### Logs
The agent uses structured logging. Check console output for detailed error information with timestamps and context.

---

Built with ❤️ using A2A SDK, LangGraph, and modern Python tooling.
