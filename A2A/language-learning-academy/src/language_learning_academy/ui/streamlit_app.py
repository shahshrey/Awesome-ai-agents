import asyncio
import os

from typing import Any
from uuid import uuid4

import httpx
import streamlit as st

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


AGENT_URL = 'http://localhost:9999'
SUPPORTED_LANGUAGES = ['spanish', 'french', 'german', 'italian', 'portuguese', 'japanese', 'chinese', 'korean']
LEVELS = ['beginner', 'intermediate', 'advanced']

def extract_text_from_artifacts(artifacts):
    """Extract text content from artifacts without nested loops."""
    if not artifacts:
        return ""

    for artifact in artifacts:
        parts = artifact.get('parts', [])
        text_content = extract_text_from_parts(parts)
        if text_content:
            return text_content
    return ""

def extract_text_from_parts(parts):
    """Extract text content from parts list."""
    if not parts:
        return ""

    for part in parts:
        text_content = part.get('text', '')
        if text_content:
            return str(text_content).strip()
    return ""

st.set_page_config(
    page_title="Polyglot Academy - Multi-Agent Language Learning",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding-top: 2rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        background: transparent;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stCheckbox label {
        color: white !important;
        font-weight: 500;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        animation: gradient 15s ease infinite;
        background-size: 400% 400%;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Inter', sans-serif;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.95;
        margin-bottom: 1.5rem;
    }
    
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.5rem;
    }
    
    .badge {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .status-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: none;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .status-success {
        background: linear-gradient(145deg, #d4edda, #c3e6cb);
        border-left: 4px solid #28a745;
    }
    
    .status-error {
        background: linear-gradient(145deg, #f8d7da, #f5c6cb);
        border-left: 4px solid #dc3545;
    }
    
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .feature-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .custom-button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        text-transform: none !important;
        width: 100% !important;
    }
    
    .custom-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        flex: 1;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-top: 3px solid #667eea;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        padding: 0.5rem;
        border-radius: 15px;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        background: transparent;
        border: none;
        border-radius: 10px;
        color: #495057;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '🤖';
        font-size: 3rem;
        position: absolute;
        top: -1rem;
        right: -1rem;
        opacity: 0.3;
    }
    
    .footer {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        text-align: center;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    .language-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .language-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 500;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .language-badge:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_agent_card():
    """Cache the agent card for 5 minutes"""
    try:
        return asyncio.run(_fetch_agent_card())
    except Exception as e:
        st.error(f"Failed to fetch agent card: {e}")
        return None

async def _fetch_agent_card():
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=AGENT_URL,
        )
        return await resolver.get_agent_card()

async def send_message_to_agent(message_text: str, use_streaming: bool = False) -> dict[str, Any]:
    try:
        agent_card = get_agent_card()
        if not agent_card:
            return {"error": "Could not connect to agent"}

        async with httpx.AsyncClient(timeout=60.0) as httpx_client:
            client = A2AClient(
                httpx_client=httpx_client,
                agent_card=agent_card
            )

            message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': message_text}
                    ],
                    'message_id': uuid4().hex,
                },
            }

            if use_streaming:
                request = SendStreamingMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(**message_payload)
                )

                response_chunks = []
                async for chunk in client.send_message_streaming(request):
                    response_chunks.append(chunk.model_dump(mode='json', exclude_none=True))

                return {"streaming_response": response_chunks}
            request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**message_payload)
            )

            response = await client.send_message(request)
            return response.model_dump(mode='json', exclude_none=True)

    except Exception as e:
        return {"error": str(e)}

def run_async(coroutine):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coroutine)

def display_agent_response(response_data):
    if 'error' in response_data:
        st.error(f"❌ Agent Error: {response_data['error']}")
        st.info("💡 Make sure you have configured your OpenAI API key:")
        st.code("""
# For OpenAI GPT-4o:
export OPENAI_API_KEY=your_openai_api_key_here
export OPENAI_MODEL=gpt-4o
        """)
        return

    if 'streaming_response' in response_data:
        st.markdown("### 🔄 Real-time Response from LLM:")
        response_container = st.container()
        with response_container:
            for chunk in response_data['streaming_response']:
                if 'content' in chunk:
                    content = str(chunk['content']).strip()
                    if content:
                        st.markdown(content)
        return

    try:
        content_found = False
        content_text = ""

        if 'result' in response_data:
            result = response_data['result']

            artifacts = result.get('artifacts', [])
            if artifacts:
                content_text = extract_text_from_artifacts(artifacts)
                if content_text:
                    content_found = True

            if not content_found:
                parts = result.get('parts', [])
                content_text = extract_text_from_parts(parts)
                if content_text:
                    content_found = True

        if content_found and content_text:
            with st.container():
                st.markdown("### 🤖 AI Response:")
                response_box = st.container()
                with response_box:
                    st.markdown(content_text)
            return

        if 'result' in response_data:
            result = response_data['result']
            if 'status' in result and result['status'].get('state') == 'completed':
                st.info("✅ Request completed successfully")
            else:
                st.warning("⚠️ No content found in response")
                with st.expander("Debug Information"):
                    st.json(response_data)
        else:
            st.warning("⚠️ Unexpected response format from LLM agent")
            with st.expander("Debug Information"):
                st.json(response_data)

    except Exception as e:
        st.error(f"Error parsing response: {e}")
        with st.expander("Debug Information"):
            st.json(response_data)

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🌟 Polyglot Academy</div>
    <div class="hero-subtitle">Multi-Agent Language Learning Platform</div>
    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">Master any language with AI-powered tutors, real-time feedback, and personalized learning paths</p>
    <div class="hero-badges">
        <div class="badge">🤖 AI Tutors</div>
        <div class="badge">🎯 Personalized</div>
        <div class="badge">⚡ Real-time</div>
        <div class="badge">🌍 8 Languages</div>
        <div class="badge">🧠 GPT-4o Powered</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="metric-container">
    <div class="metric-card">
        <span class="metric-number">8</span>
        <div class="metric-label">Supported Languages</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">3</span>
        <div class="metric-label">Skill Levels</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">6</span>
        <div class="metric-label">Learning Modes</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">∞</span>
        <div class="metric-label">AI Possibilities</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'agent_status' not in st.session_state:
    st.session_state.agent_status = "checking"

if st.session_state.agent_status == "checking":
    with st.spinner("🔍 Checking agent connection..."):
        agent_card = get_agent_card()
        if agent_card:
            st.session_state.agent_status = "connected"
            st.session_state.agent_card = agent_card
        else:
            st.session_state.agent_status = "offline"

if st.session_state.agent_status == "connected":
    st.markdown("""
    <div class="status-card status-success">
        <h3 style="margin: 0; color: #155724;">✅ Multi-Agent System Online</h3>
        <p style="margin: 0.5rem 0 0 0; color: #155724;">All AI tutors are ready to assist with your language learning journey!</p>
    </div>
    """, unsafe_allow_html=True)

    if hasattr(st.session_state, 'agent_card'):
        st.markdown(f"""
        <div class="agent-card">
            <h4 style="margin: 0; font-size: 1.2rem;">🤖 {st.session_state.agent_card.name}</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Version {st.session_state.agent_card.version} • Ready for multi-language instruction</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.agent_status == "offline":
    st.markdown("""
    <div class="status-card status-error">
        <h3 style="margin: 0; color: #721c24;">❌ Multi-Agent System Offline</h3>
        <p style="margin: 0.5rem 0 0 0; color: #721c24;">Please ensure the agent is running on localhost:9999 with proper LLM API keys configured</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 style="color: white; margin: 0; font-size: 1.8rem;">🌍 Learning Hub</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Customize your learning experience</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚡ Performance Settings")
streaming_enabled = st.sidebar.checkbox(
    "🔄 Enable Real-time Streaming",
    value=False,
    help="Get real-time responses from the LLM for immediate feedback"
)

st.sidebar.markdown("### 🎯 Learning Preferences")
selected_language = st.sidebar.selectbox(
    "🌐 Target Language:",
    SUPPORTED_LANGUAGES,
    index=0,
    help="Choose the language you want to learn"
).title()

selected_level = st.sidebar.selectbox(
    "📊 Proficiency Level:",
    LEVELS,
    index=0,
    help="Select your current skill level"
).title()

st.sidebar.markdown("---")

st.sidebar.markdown("### 🧠 AI Engine Status")
openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o')

st.sidebar.markdown("""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
    <div style="color: white; font-weight: 500;">🤖 Model Source</div>
    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">OPENAI</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
    <div style="color: white; font-weight: 500;">🚀 AI Model</div>
    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">{openai_model}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🛠️ Quick Actions")

sidebar_response_placeholder = st.sidebar.empty()

col1, col2 = st.sidebar.columns(2)
with col1:
    lang_info_clicked = st.button("ℹ️ Languages", key="lang_info", help="Show available languages")

with col2:
    if st.button("🔄 Refresh", key="refresh_conn", help="Refresh connection"):
        st.session_state.agent_status = "checking"
        st.rerun()

if lang_info_clicked:
    with st.spinner("🤖 Querying AI tutors..."):
        response = run_async(send_message_to_agent("What languages do you support and what can you help me learn? Give me a comprehensive overview with your capabilities for each language.", streaming_enabled))

    with st.container():
        st.markdown("---")
        display_agent_response(response)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="language-grid">
""" + "".join([f'<div class="language-badge">{lang.title()}</div>' for lang in SUPPORTED_LANGUAGES[:4]]) + """
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.7); font-size: 0.8rem;">
    <p>🎓 Currently learning <strong>{selected_language}</strong><br/>
    at <strong>{selected_level}</strong> level</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📚 Vocabulary", "📝 Grammar", "💬 Conversation", "🧩 Quiz", "🌐 Translation", "🎯 Custom Query"
])

with tab1:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">📚 AI-Powered Vocabulary Academy</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Expand your <strong>{selected_language}</strong> vocabulary with our intelligent tutoring system. 
            Get personalized lessons at the <strong>{selected_level}</strong> level with pronunciation guides, 
            cultural context, and real-world usage examples.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        vocab_type = st.selectbox(
            "🏷️ Select vocabulary category:",
            ["general", "greetings", "food", "family", "travel", "business", "technology", "emotions", "nature"],
            key="vocab_type",
            help="Choose a category that interests you most"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        vocab_clicked = st.button("🎯 Generate Vocabulary Lesson", key="vocab_btn", help="Create a personalized lesson")

    response_placeholder = st.empty()

    if vocab_clicked:
        query = f"Create a comprehensive {selected_language} vocabulary lesson for {vocab_type} words at {selected_level} level. Include: 1) 10-15 essential words with pronunciation, 2) Example sentences with translations, 3) Cultural context and usage tips, 4) Memory techniques or mnemonics, 5) Practice exercises. Make it engaging and educational."
        with st.spinner("🤖 AI tutors crafting your personalized vocabulary lesson..."):
            response = run_async(send_message_to_agent(query, streaming_enabled))

        with response_placeholder.container():
            display_agent_response(response)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd, #f3e5f5); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #2196f3;">
        <h4 style="margin: 0 0 0.5rem 0; color: #1976d2;">💡 Pro Tips for Vocabulary Learning</h4>
        <ul style="margin: 0; color: #424242;">
            <li><strong>Context is key:</strong> Learn words in sentences, not isolation</li>
            <li><strong>Daily practice:</strong> Use 3-5 new words in conversation each day</li>
            <li><strong>Visual association:</strong> Connect words with images or situations</li>
            <li><strong>Spaced repetition:</strong> Review words at increasing intervals</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <p style="margin: 0; color: #6c757d; font-style: italic;">
            💬 <strong>Example query:</strong> "Teach me advanced Spanish business vocabulary with formal expressions and email phrases"
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">📝 AI Grammar Mastery Center</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Master <strong>{selected_language}</strong> grammar through intelligent explanations, pattern recognition, 
            and practical exercises. Our AI tutors break down complex rules into digestible lessons 
            perfect for <strong>{selected_level}</strong> level learners.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        grammar_topic = st.selectbox(
            "📖 Choose grammar focus:",
            ["present tense", "past tense", "future tense", "subjunctive", "conditionals", "pronouns", "articles", "prepositions", "irregular verbs", "question formation"],
            key="grammar_topic",
            help="Select the grammar concept you want to master"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        grammar_clicked = st.button("🎓 Start Grammar Lesson", key="grammar_btn", help="Get comprehensive grammar instruction")

    grammar_response_placeholder = st.empty()

    if grammar_clicked:
        query = f"Create an in-depth {selected_language} grammar lesson on {grammar_topic} for {selected_level} learners. Include: 1) Clear rule explanations with visual patterns, 2) Common exceptions and irregularities, 3) Step-by-step conjugation guides, 4) 10+ practical examples with translations, 5) Common mistakes to avoid, 6) Practice exercises with solutions. Make it comprehensive yet easy to understand."
        with st.spinner("🤖 AI grammar experts preparing your personalized lesson..."):
            response = run_async(send_message_to_agent(query, streaming_enabled))

        with grammar_response_placeholder.container():
            display_agent_response(response)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3e0, #fce4ec); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #ff9800;">
        <h4 style="margin: 0 0 0.5rem 0; color: #f57c00;">🧠 Grammar Learning Strategies</h4>
        <ul style="margin: 0; color: #424242;">
            <li><strong>Pattern recognition:</strong> Look for similarities between grammar rules</li>
            <li><strong>Real-world practice:</strong> Use new structures in daily conversations</li>
            <li><strong>Error analysis:</strong> Learn from mistakes to avoid repetition</li>
            <li><strong>Progressive complexity:</strong> Master basics before tackling advanced concepts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <p style="margin: 0; color: #6c757d; font-style: italic;">
            💬 <strong>Example query:</strong> "Explain French subjunctive mood with clear examples and when to use it in real conversations"
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">💬 AI Conversation Academy</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Practice real-world <strong>{selected_language}</strong> conversations with our intelligent coaching system. 
            Build confidence through immersive scenarios tailored for <strong>{selected_level}</strong> level speakers 
            with cultural insights and pronunciation guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        scenario = st.selectbox(
            "🎭 Select conversation scenario:",
            ["restaurant", "directions", "hotel", "shopping", "airport", "café", "job interview", "doctor visit", "making friends", "business meeting", "phone call"],
            key="scenario",
            help="Choose a real-world situation to practice"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        convo_clicked = st.button("🗣️ Start Conversation Practice", key="convo_btn", help="Begin interactive role-play")

    convo_response_placeholder = st.empty()

    if convo_clicked:
        query = f"Create an immersive {scenario} conversation practice session in {selected_language} for {selected_level} level. Include: 1) Realistic dialogue with multiple turns, 2) Essential phrases and vocabulary, 3) Cultural etiquette and social cues, 4) Pronunciation tips for key expressions, 5) Alternative responses for different situations, 6) Common mistakes to avoid. Make it interactive and engaging like a real conversation coach."
        with st.spinner("🤖 AI conversation coaches setting up your practice session..."):
            response = run_async(send_message_to_agent(query, streaming_enabled))

        with convo_response_placeholder.container():
            display_agent_response(response)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e8, #f0f8ff); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #4caf50;">
        <h4 style="margin: 0 0 0.5rem 0; color: #2e7d32;">🎯 Conversation Mastery Tips</h4>
        <ul style="margin: 0; color: #424242;">
            <li><strong>Active listening:</strong> Pay attention to tone, pace, and cultural cues</li>
            <li><strong>Practice naturally:</strong> Don't memorize scripts, focus on natural flow</li>
            <li><strong>Cultural awareness:</strong> Learn social norms and etiquette</li>
            <li><strong>Confidence building:</strong> Start simple, gradually increase complexity</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <p style="margin: 0; color: #6c757d; font-style: italic;">
            💬 <strong>Example query:</strong> "Create a Japanese business meeting role-play with formal expressions and cultural etiquette"
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">🧩 AI Quiz Generator</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Test and reinforce your <strong>{selected_language}</strong> knowledge with intelligent, adaptive quizzes. 
            Our AI creates personalized assessments at the <strong>{selected_level}</strong> level with detailed 
            explanations to accelerate your learning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        quiz_type = st.selectbox(
            "🎪 Quiz category:",
            ["vocabulary", "translation", "grammar", "listening comprehension", "cultural knowledge", "mixed review"],
            key="quiz_type",
            help="Choose what aspect to focus on"
        )
    with col2:
        quiz_difficulty = st.selectbox(
            "⚡ Challenge level:",
            LEVELS,
            key="quiz_diff",
            help="Select quiz difficulty"
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        quiz_clicked = st.button("🎯 Generate Smart Quiz", key="quiz_btn", help="Create personalized assessment")

    quiz_response_placeholder = st.empty()

    if quiz_clicked:
        query = f"Create an engaging {quiz_type} quiz for {selected_language} at {quiz_difficulty} level. Include: 1) 8-10 well-crafted questions with multiple choice options, 2) Detailed explanations for both correct and incorrect answers, 3) Progressive difficulty within the quiz, 4) Cultural context where relevant, 5) Tips for improvement, 6) Score interpretation guide. Make it educational and motivating."
        with st.spinner("🤖 AI assessment specialists generating your personalized quiz..."):
            response = run_async(send_message_to_agent(query, streaming_enabled))

        with quiz_response_placeholder.container():
            display_agent_response(response)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff9c4, #ffe0b3); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #ffc107;">
        <h4 style="margin: 0 0 0.5rem 0; color: #f57f17;">🏆 Effective Quiz Strategies</h4>
        <ul style="margin: 0; color: #424242;">
            <li><strong>Regular assessment:</strong> Take quizzes weekly to track progress</li>
            <li><strong>Learn from mistakes:</strong> Review explanations for wrong answers</li>
            <li><strong>Mixed practice:</strong> Combine different quiz types for comprehensive review</li>
            <li><strong>Timed practice:</strong> Challenge yourself with time constraints</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab5:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-header">🌐 AI Translation Studio</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Experience intelligent translation that goes beyond words. Our AI provides cultural context, 
            alternative expressions, and nuanced interpretations for professional-quality translations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            "🔤 From language:",
            ["Auto-detect"] + [lang.title() for lang in SUPPORTED_LANGUAGES],
            key="source_lang",
            help="Source language (auto-detect available)"
        )
    with col2:
        target_lang = st.selectbox(
            "🎯 To language:",
            [lang.title() for lang in SUPPORTED_LANGUAGES],
            index=0,
            key="target_lang",
            help="Target language for translation"
        )

    text_to_translate = st.text_area(
        "📝 Enter text to translate:",
        placeholder="Type or paste your text here... (supports multiple languages)",
        height=120,
        key="translate_text",
        help="Enter any text for intelligent translation with cultural context"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        translate_clicked = st.button("🚀 Smart Translate", key="translate_btn", help="Get intelligent translation with context")

    translate_response_placeholder = st.empty()

    if translate_clicked:
        if text_to_translate.strip():
            source = source_lang.lower() if source_lang != "Auto-detect" else "auto"
            target = target_lang.lower()
            query = f"Provide an intelligent translation from {source} to {target} for: '{text_to_translate}'. Include: 1) Primary translation, 2) Alternative expressions, 3) Cultural context and nuances, 4) Formality level analysis, 5) Usage tips, 6) Common variations. Make it comprehensive and culturally aware."
            with st.spinner("🤖 AI linguists analyzing and translating with cultural intelligence..."):
                response = run_async(send_message_to_agent(query, streaming_enabled))

            with translate_response_placeholder.container():
                display_agent_response(response)
        else:
            st.warning("⚠️ Please enter text to translate!")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #e1f5fe, #f3e5f5); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #00bcd4;">
        <h4 style="margin: 0 0 0.5rem 0; color: #0097a7;">🔍 Translation Excellence Features</h4>
        <ul style="margin: 0; color: #424242;">
            <li><strong>Cultural awareness:</strong> Understand social context and etiquette</li>
            <li><strong>Multiple options:</strong> Get alternative phrasings for different situations</li>
            <li><strong>Formality levels:</strong> Choose appropriate register for your audience</li>
            <li><strong>Idiomatic expressions:</strong> Learn natural, native-like phrases</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab6:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">🎯 Personal AI Language Tutor</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Your dedicated AI language consultant is here to answer any question, solve learning challenges, 
            and provide personalized guidance for your <strong>{selected_language}</strong> journey at the <strong>{selected_level}</strong> level.
        </p>
    </div>
    """, unsafe_allow_html=True)

    custom_query = st.text_area(
        "💭 What would you like to learn or explore?",
        placeholder="Ask anything: grammar rules, cultural insights, pronunciation tips, study strategies, writing help, conversation practice, or language learning advice...",
        height=140,
        key="custom_query",
        help="Ask your AI tutor anything about language learning"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        advanced_mode = st.checkbox(
            "🧠 Expert Mode",
            help="Get comprehensive responses with deep cultural insights and advanced explanations",
            key="expert_mode"
        )
    with col2:
        include_examples = st.checkbox(
            "📚 Include Examples",
            help="Add practical examples and exercises to the response",
            value=True,
            key="include_examples"
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        custom_clicked = st.button("🚀 Consult AI Tutor", key="custom_btn", help="Get personalized language learning guidance")

    custom_response_placeholder = st.empty()

    if custom_clicked:
        if custom_query.strip():
            enhanced_query = custom_query
            if advanced_mode and include_examples:
                enhanced_query = f"As an expert multilingual tutor, provide a comprehensive and detailed answer with cultural context, practical examples, exercises, and actionable tips for a {selected_level} level {selected_language} learner: {custom_query}"
            elif advanced_mode:
                enhanced_query = f"As an expert language tutor, provide a comprehensive answer with deep cultural context and advanced insights for a {selected_level} level {selected_language} learner: {custom_query}"
            elif include_examples:
                enhanced_query = f"Provide a helpful answer with practical examples and exercises for a {selected_level} level {selected_language} learner: {custom_query}"
            else:
                enhanced_query = f"Help a {selected_level} level {selected_language} learner with this question: {custom_query}"

            with st.spinner("🤖 AI tutors collaborating to craft your personalized response..."):
                response = run_async(send_message_to_agent(enhanced_query, streaming_enabled))

            with custom_response_placeholder.container():
                display_agent_response(response)
        else:
            st.warning("⚠️ Please enter your question or learning request!")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8e1ff, #e3f2fd); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #9c27b0;">
        <h4 style="margin: 0 0 0.5rem 0; color: #7b1fa2;">💡 Popular Learning Topics</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 0; color: #424242; font-size: 0.9rem;">
            <div>• Grammar explanations & rules</div>
            <div>• Pronunciation & accent training</div>
            <div>• Cultural insights & etiquette</div>
            <div>• Writing & composition help</div>
            <div>• Conversation starters & phrases</div>
            <div>• Study plans & learning strategies</div>
            <div>• Common mistakes & corrections</div>
            <div>• Professional & business language</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🌟 Polyglot Academy")
st.markdown("**Multi-Agent Language Learning Platform**")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 🤖 AI Technology")
    st.markdown("""
    - Powered by OpenAI GPT-4o
    - Real-time streaming responses
    - Multi-agent coordination
    """)

with col2:
    st.markdown("#### 🌍 Languages")
    st.markdown("""
    - 8 supported languages
    - Cultural context integration
    - Native-level instruction
    """)

with col3:
    st.markdown("#### 🎯 Features")
    st.markdown("""
    - Personalized learning paths
    - Interactive conversations
    - Intelligent assessments
    """)

st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit & A2A Protocol • Advanced AI for Language Excellence*")
