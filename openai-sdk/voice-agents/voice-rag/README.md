# 🎙️ Technical Documentation Voice Assistant

A RAG (Retrieval-Augmented Generation) voice agent that helps you get natural voice explanations from technical documentation. Upload PDFs and ask questions to receive both text and audio responses.

## Features

- **PDF Document Processing**: Upload technical PDFs (API docs, guides, manuals)
- **Natural Voice Responses**: Get answers in natural-sounding speech
- **Multiple Voice Options**: Choose from 9 different OpenAI voices
- **Semantic Search**: Find relevant information across your documents
- **Source Citations**: See which documents your answers came from
- **Audio Downloads**: Save voice responses as MP3 files

## Perfect For

- API documentation
- Technical guides and manuals
- Research papers
- Development resources
- Educational materials

## Prerequisites

You'll need API keys for:
- **OpenAI**: For GPT models and text-to-speech
- **Qdrant**: For vector database storage (free tier available)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables (you can also enter these in the Streamlit sidebar):
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export QDRANT_URL="your_qdrant_url_here"
export QDRANT_API_KEY="your_qdrant_api_key_here"
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Configure your API keys in the sidebar

3. Upload a PDF document

4. Ask questions and get voice responses!

## API Key Setup

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### Qdrant Setup
1. Go to https://cloud.qdrant.io/
2. Create a free account
3. Create a new cluster
4. Copy the URL and API key

## Voice Options

Choose from these OpenAI voices:
- **alloy**: Balanced and natural
- **ash**: Clear and articulate  
- **coral**: Warm and friendly
- **echo**: Confident and clear
- **fable**: Expressive and engaging
- **onyx**: Deep and authoritative
- **nova**: Bright and energetic
- **sage**: Wise and measured
- **shimmer**: Gentle and soothing

## Technical Details

- **Vector Database**: Qdrant for semantic search
- **Embeddings**: FastEmbed for document vectorization
- **Text Processing**: LangChain for PDF parsing and chunking
- **LLM**: OpenAI GPT-4o for answer generation
- **TTS**: OpenAI gpt-4o-mini-tts for voice synthesis
- **Frontend**: Streamlit for the web interface

## Architecture

```
PDF Upload → Text Extraction → Chunking → Embedding → Vector Storage
                                                           ↓
User Query → Query Embedding → Similarity Search → Context Retrieval
                                                           ↓
Context + Query → GPT-4o → Text Response → TTS → Audio Response
```

## License

This project is open source and available under the MIT License. 