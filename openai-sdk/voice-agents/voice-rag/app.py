import streamlit as st
import asyncio
import os
import tempfile
from typing import cast

from voice_agent import create_rag_agent, validate_environment, VoiceType

# ── 1. Config ────────────────────────────────────────────────────────────────
APP_TITLE = "Technical Documentation Voice Assistant"
SUPPORTED_VOICES = [
    "alloy", "ash", "coral", "echo", "fable", 
    "onyx", "nova", "sage", "shimmer"
]

# ── 2. Session State Management ──────────────────────────────────────────────
def init_session_state():
    """Initialize session state with default values"""
    defaults = {
        "rag_agent": None,
        "processed_documents": [],
        "setup_complete": False,
        "openai_api_key": "",
        "qdrant_url": "",
        "qdrant_api_key": "",
        "selected_voice": "nova"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ── 3. UI Components ─────────────────────────────────────────────────────────
def render_sidebar():
    """Render sidebar with configuration options"""
    with st.sidebar:
        st.title("🔑 Configuration")
        st.markdown("---")
        
        # API Keys
        st.session_state.openai_api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Your OpenAI API key for GPT and TTS"
        )
        
        st.session_state.qdrant_url = st.text_input(
            "Qdrant URL",
            value=st.session_state.qdrant_url,
            type="password",
            help="Your Qdrant cloud URL"
        )
        
        st.session_state.qdrant_api_key = st.text_input(
            "Qdrant API Key",
            value=st.session_state.qdrant_api_key,
            type="password",
            help="Your Qdrant API key"
        )
        
        st.markdown("---")
        
        # Voice Settings
        st.markdown("### 🎤 Voice Settings")
        st.session_state.selected_voice = st.selectbox(
            "Select Voice",
            options=SUPPORTED_VOICES,
            index=SUPPORTED_VOICES.index(st.session_state.selected_voice),
            help="Choose the voice for audio responses"
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 📊 System Status")
        if st.session_state.setup_complete:
            st.success("✅ System Ready")
            st.info(f"📚 {len(st.session_state.processed_documents)} documents loaded")
        else:
            st.warning("⚠️ Setup Required")
        
        # Processed Documents
        if st.session_state.processed_documents:
            st.markdown("### 📄 Loaded Documents")
            for doc in st.session_state.processed_documents:
                st.text(f"• {doc}")

def render_main_content():
    """Render main content area"""
    st.title(f"🎙️ {APP_TITLE}")
    
    # Welcome message
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3>🚀 Welcome to your Technical Documentation Voice Assistant!</h3>
        <p>Upload technical documents (PDFs) and ask questions to get natural voice explanations of complex topics.</p>
        <p><strong>Perfect for:</strong> API documentation, technical guides, research papers, and development resources.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Setup status
    if not st.session_state.setup_complete:
        st.info("👈 Please configure your API keys in the sidebar and upload a document to get started!")
        return
    
    # Query interface
    st.markdown("### 💬 Ask Your Question")
    query = st.text_input(
        "",
        placeholder="e.g., How do I authenticate API requests? What are the rate limits?",
        help="Ask any question about your uploaded documentation"
    )
    
    if st.button("🎧 Get Voice Answer", type="primary", disabled=not query):
        if query:
            handle_query(query)

def handle_file_upload():
    """Handle PDF file upload"""
    st.markdown("### 📄 Upload Technical Documentation")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload API docs, technical guides, or any PDF documentation"
    )
    
    if uploaded_file and uploaded_file.name not in st.session_state.processed_documents:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                # Setup RAG agent if needed
                if not st.session_state.rag_agent:
                    setup_rag_agent()
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Process document
                chunks = st.session_state.rag_agent.process_pdf(tmp_file_path, uploaded_file.name)
                st.session_state.rag_agent.store_documents(chunks)
                
                # Update session state
                st.session_state.processed_documents.append(uploaded_file.name)
                st.session_state.setup_complete = True
                
                # Cleanup
                os.unlink(tmp_file_path)
                
                st.success(f"✅ Successfully processed {uploaded_file.name} ({len(chunks)} chunks)")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")

def setup_rag_agent():
    """Setup RAG agent with current configuration"""
    try:
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
        os.environ["QDRANT_URL"] = st.session_state.qdrant_url
        os.environ["QDRANT_API_KEY"] = st.session_state.qdrant_api_key
        
        # Validate environment
        validate_environment()
        
        # Create RAG agent
        st.session_state.rag_agent = create_rag_agent(
            st.session_state.qdrant_url,
            st.session_state.qdrant_api_key
        )
        
    except Exception as e:
        raise Exception(f"Failed to setup RAG agent: {str(e)}")

def handle_query(query: str):
    """Handle user query and generate response"""
    try:
        with st.status("Processing your query...", expanded=True) as status:
            # Update status
            status.write("🔍 Searching documentation...")
            
            # Get voice setting
            voice = cast(VoiceType, st.session_state.selected_voice)
            
            # Process query
            result = asyncio.run(
                st.session_state.rag_agent.answer_query(query, voice)
            )
            
            if result.status == "success":
                status.update(label="✅ Response generated!", state="complete")
                
                # Display results
                st.markdown("### 📝 Answer")
                st.write(result.text_response)
                
                # Audio player
                st.markdown(f"### 🔊 Audio Response (Voice: {voice})")
                try:
                    with open(result.audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Audio",
                            data=audio_bytes,
                            file_name=f"tech_docs_answer_{voice}.mp3",
                            mime="audio/mp3"
                        )
                except Exception as e:
                    st.warning(f"Audio file not accessible: {str(e)}")
                
                # Sources
                if result.sources:
                    st.markdown("### 📚 Sources")
                    for source in result.sources:
                        st.markdown(f"• {source}")
                        
            else:
                status.update(label="❌ Error processing query", state="error")
                st.error(f"Error: {result.status}")
                
    except Exception as e:
        st.error(f"❌ Error processing query: {str(e)}")

# ── 4. Error Handling ────────────────────────────────────────────────────────
def safe_run_async(coro):
    """Safely run async function in Streamlit"""
    try:
        return asyncio.run(coro)
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)
        raise

# ── 5. Main Application ──────────────────────────────────────────────────────
def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .stApp > header {
            background-color: transparent;
        }
        .stApp {
            margin-top: -80px;
        }
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Render UI
    render_sidebar()
    
    # Check if API keys are provided
    if not all([
        st.session_state.openai_api_key,
        st.session_state.qdrant_url,
        st.session_state.qdrant_api_key
    ]):
        st.title(f"🎙️ {APP_TITLE}")
        st.warning("⚠️ Please configure your API keys in the sidebar to get started!")
        return
    
    # File upload section
    handle_file_upload()
    
    # Main content
    render_main_content()

if __name__ == "__main__":
    main() 