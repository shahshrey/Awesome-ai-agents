#!/usr/bin/env python3
"""Streamlit app for Bedtime Story Voice Agent."""

import streamlit as st
import asyncio
import os
from pathlib import Path
from voice_agent import (
    create_bedtime_story_with_audio,
    get_age_appropriate_themes,
    validate_duration,
    VOICE,
    MIN_DURATION_MINUTES,
    MAX_DURATION_MINUTES,
    DEFAULT_DURATION_MINUTES
)

# Voice options for TTS
VOICE_OPTIONS = {
    "nova": "Nova (Friendly & Warm)",
    "alloy": "Alloy (Neutral & Clear)", 
    "echo": "Echo (Smooth & Calm)",
    "fable": "Fable (Expressive)",
    "onyx": "Onyx (Deep & Authoritative)",
    "shimmer": "Shimmer (Gentle & Soothing)"
}

# Age ranges
AGE_RANGES = ["2-4 years", "4-8 years", "8-12 years"]


def init_session_state():
    """Initialize session state variables."""
    if "story_generated" not in st.session_state:
        st.session_state.story_generated = False
    if "current_story" not in st.session_state:
        st.session_state.current_story = None
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None


def handle_async(coro):
    """Handle async functions in Streamlit."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Handle event loop already running
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="🌙 Bedtime Story Generator",
        page_icon="🌙",
        layout="wide"
    )
    
    init_session_state()
    
    # Custom CSS for glassy, kid-friendly design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Bubblegum+Sans&family=Quicksand:wght@400;600;700&display=swap');

    :root {
      --bg1: #667eea;
      --bg2: #764ba2;
      --glass: rgba(255, 255, 255, 0.15);
      --glass-dark: rgba(0, 0, 0, 0.1);
      --border: rgba(255, 255, 255, 0.3);
      --shadow: 0 8px 32px rgba(31, 38, 135, 0.25);
      --accent: #ffd93d;
      --accent-2: #6bcf7f;
      --accent-3: #ff6b9d;
      --text-dark: #2d3748;
      --text-light: #ffffff;
      --muted: #4a5568;
    }

    /* Animated gradient background - apply to body */
    body {
      background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
      background-size: 400% 400%;
      animation: gradientShift 15s ease infinite;
      min-height: 100vh;
    }
    
    [data-testid="stAppViewContainer"] {
      background: transparent;
    }
    
    .main {
      background: transparent;
    }

    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* Floating clouds background element */
    .cloud-container {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 0;
      overflow: hidden;
    }

    .cloud {
      position: absolute;
      font-size: 60px;
      opacity: 0.3;
      animation: floatCloud 20s linear infinite;
    }

    .cloud:nth-child(1) {
      top: 10%;
      left: -100px;
      animation-duration: 20s;
    }

    .cloud:nth-child(2) {
      top: 30%;
      left: -150px;
      font-size: 80px;
      animation-duration: 25s;
      animation-delay: 5s;
    }

    .cloud:nth-child(3) {
      top: 60%;
      left: -120px;
      font-size: 70px;
      animation-duration: 22s;
      animation-delay: 10s;
    }

    @keyframes floatCloud {
      to { transform: translateX(calc(100vw + 200px)); }
    }

    /* Twinkling stars */
    .stars {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 0;
      overflow: hidden;
    }

    .stars::before, .stars::after {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image:
        radial-gradient(2px 2px at 20% 30%, white, transparent),
        radial-gradient(2px 2px at 60% 70%, white, transparent),
        radial-gradient(1px 1px at 50% 20%, white, transparent),
        radial-gradient(2px 2px at 80% 10%, white, transparent),
        radial-gradient(1px 1px at 30% 50%, white, transparent);
      background-size: 200% 200%;
      animation: twinkle 4s ease-in-out infinite;
    }

    @keyframes twinkle {
      0%, 100% { opacity: 0.2; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(1.1); }
    }

    /* Main content - ensure visibility */
    .main .block-container {
      position: relative;
      z-index: 10;
    }
    
    [data-testid="stVerticalBlock"] {
      position: relative;
      z-index: 10;
    }

    /* Typography with fun fonts */
    h1, h2, h3, h4 {
      font-family: 'Bubblegum Sans', 'Fredoka', cursive !important;
      color: white !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    p, label, span, div {
      font-family: 'Quicksand', 'Fredoka', sans-serif;
      color: white;
      font-weight: 500;
    }
    
    /* Dark text in light background containers */
    .story-box {
      color: #2d3748 !important;
    }
    
    .story-box * {
      color: #2d3748 !important;
    }
    
    /* Glass cards should have white text for visibility */
    .glass-card {
      background: rgba(0, 0, 0, 0.3) !important;
      color: white !important;
    }
    
    .glass-card * {
      color: white !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    .glass-card p {
      color: white !important;
      font-weight: 600;
      font-size: 1.05em;
    }
    
    .glass-card b {
      color: #ffd93d !important;
      font-size: 1.3em;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    /* Make emojis larger in glass cards */
    .glass-card span[style*="font-size: 2rem"] {
      font-size: 2.5rem !important;
      filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
    }
    
    [data-testid="stMetric"] *,
    [data-testid="stAlert"] *,
    [data-testid="stExpander"] * {
      color: #2d3748 !important;
    }
    
    /* Info boxes specifically */
    [data-testid="stInfo"] {
      background: rgba(255, 255, 255, 0.9) !important;
      color: #2d3748 !important;
      border-radius: 20px;
    }
    
    [data-testid="stInfo"] * {
      color: #2d3748 !important;
    }

    /* Animated title */
    .stTitle, .stMarkdown h1 {
      text-align: center;
      background: linear-gradient(45deg, #ffd93d, #6bcf7f, #ff6b9d, #c7ceea);
      background-size: 200% 200%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: gradientText 3s ease infinite;
      text-shadow: none;
      font-size: 3rem !important;
    }

    @keyframes gradientText {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    div.block-container { padding-top: 2rem; }

    /* Glassy sidebar with rainbow border */
    div[data-testid="stSidebar"] {
      background: rgba(255, 255, 255, 0.95) !important;
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-right: 2px solid;
      border-image: linear-gradient(180deg, #ffd93d, #6bcf7f, #ff6b9d, #c7ceea) 1;
      box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
    }
    
    div[data-testid="stSidebar"] * {
      color: #2d3748 !important;
    }

    /* Playful buttons with hover effects */
    div.stButton > button, button[kind="primary"] {
      font-family: 'Fredoka', sans-serif !important;
      font-weight: 600 !important;
      border-radius: 25px;
      border: 2px solid rgba(255, 255, 255, 0.5);
      background: rgba(255, 255, 255, 0.25);
      backdrop-filter: blur(10px);
      color: white !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
      box-shadow: 
        0 8px 32px rgba(31, 38, 135, 0.2),
        inset 0 1px 2px rgba(255, 255, 255, 0.3);
      padding: 12px 24px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
    }

    div.stButton > button::before {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      transform: translate(-50%, -50%);
      transition: width 0.6s, height 0.6s;
    }

    div.stButton > button:hover::before {
      width: 300px;
      height: 300px;
    }

    div.stButton > button:hover {
      transform: translateY(-3px) scale(1.02);
      box-shadow: 
        0 12px 40px rgba(31, 38, 135, 0.4),
        inset 0 1px 3px rgba(255, 255, 255, 0.4);
      border-color: var(--accent);
    }

    /* Glassy input fields */
    input, textarea, select, .stTextArea textarea, .stSelectbox, .stSlider, [data-baseweb="select"] > div {
      border-radius: 20px !important;
      font-family: 'Quicksand', sans-serif !important;
    }

    textarea, .stTextArea textarea, input[type="text"], input[type="password"] {
      background: rgba(255, 255, 255, 0.9) !important;
      backdrop-filter: blur(10px) !important;
      border: 2px solid rgba(255, 255, 255, 0.3) !important;
      color: #2d3748 !important;
      padding: 12px 16px !important;
      transition: all 0.3s ease !important;
    }
    
    /* Simple select slider styling with glass effect */
    .stSelectSlider {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 15px;
      border-radius: 15px;
      margin: 10px 0;
    }
    
    .stSelectSlider label {
      color: white !important;
      font-weight: 600 !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Form labels - specific styling per component */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stCheckbox label {
      color: white !important;
      font-weight: 600 !important;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Slider and SelectSlider labels are styled separately above for better visibility */
    
    /* Checkbox specific styling */
    .stCheckbox > label {
      background: rgba(255, 255, 255, 0.1);
      padding: 8px 12px;
      border-radius: 10px;
      display: inline-block;
    }
    
    .stCheckbox input[type="checkbox"] {
      margin-right: 8px;
    }

    textarea:focus, .stTextArea textarea:focus, input:focus {
      border-color: var(--accent) !important;
      box-shadow: 0 0 20px rgba(255, 217, 61, 0.3) !important;
      background: rgba(255, 255, 255, 0.25) !important;
    }

    /* Glassy cards with gradient borders */
    .story-box {
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-radius: 30px;
      padding: 25px;
      box-shadow: 
        0 8px 32px rgba(31, 38, 135, 0.2),
        inset 0 1px 2px rgba(255, 255, 255, 0.3);
      border: 2px solid;
      border-image: linear-gradient(135deg, var(--accent), var(--accent-2), var(--accent-3)) 1;
      color: #2d3748;
      margin: 15px 0;
      position: relative;
      overflow: hidden;
    }
    
    .glass-card {
      background: linear-gradient(135deg, 
        rgba(0, 0, 0, 0.4),
        rgba(0, 0, 0, 0.3)) !important;
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-radius: 30px;
      padding: 25px;
      box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 2px rgba(255, 255, 255, 0.2);
      border: 2px solid rgba(255, 255, 255, 0.3);
      margin: 15px 0;
      position: relative;
      overflow: hidden;
    }

    .story-box::before {
      content: "✨";
      position: absolute;
      font-size: 100px;
      opacity: 0.1;
      right: -20px;
      top: -20px;
      transform: rotate(15deg);
    }

    /* Theme suggestion bubbles */
    .theme-suggestion {
      background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.25) 0%, 
        rgba(255, 255, 255, 0.15) 100%);
      backdrop-filter: blur(10px);
      border: 2px dashed var(--accent);
      border-radius: 20px;
      padding: 15px;
      color: #2d3748;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
    }

    .theme-suggestion:hover {
      transform: translateY(-5px) scale(1.05);
      background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.35) 0%, 
        rgba(255, 255, 255, 0.25) 100%);
      box-shadow: 0 10px 30px rgba(31, 38, 135, 0.3);
    }

    /* Expander with rainbow gradient */
    [data-testid="stExpander"] {
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(31, 38, 135, 0.15);
    }

    /* Fun metrics cards */
    [data-testid="stMetric"] {
      background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.9) 0%, 
        rgba(255, 255, 255, 0.85) 100%);
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.4);
      border-radius: 20px;
      padding: 15px;
      box-shadow: 0 4px 20px rgba(31, 38, 135, 0.2);
      transition: transform 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
      transform: translateY(-2px);
    }

    /* Colorful alerts */
    [data-testid="stAlert"] {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.4);
      border-radius: 20px;
      box-shadow: 0 4px 20px rgba(31, 38, 135, 0.2);
      color: #2d3748;
    }

    /* Success message animation */
    [data-testid="stSuccess"] {
      background: linear-gradient(135deg, 
        rgba(107, 207, 127, 0.3) 0%, 
        rgba(107, 207, 127, 0.2) 100%);
      animation: bounce 0.5s ease;
    }

    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }

    /* Error message */
    [data-testid="stError"] {
      background: linear-gradient(135deg, 
        rgba(255, 107, 157, 0.3) 0%, 
        rgba(255, 107, 157, 0.2) 100%);
    }

    /* Simple, clean slider styling with glass effect */
    .stSlider {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 15px;
      border-radius: 15px;
      margin: 10px 0;
    }
    
    .stSlider label {
      color: white !important;
      font-weight: 600 !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Audio player styling */
    audio {
      width: 100%;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
    }

    /* Download button special styling */
    .stDownloadButton > button {
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
      border: none;
      font-weight: bold;
    }

    .stDownloadButton > button:hover {
      background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent) 100%);
    }

    /* Spinner animation */
    [data-testid="stSpinner"] > div {
      border-color: var(--accent) transparent var(--accent-2) transparent;
    }

    /* Small helpers */
    .small-note { 
      color: rgba(255, 255, 255, 0.9); 
      font-size: 0.9rem;
      font-weight: 500;
    }
    
    /* Help text and captions */
    .stTextInput > div > div > small,
    .stTextArea > div > div > small,
    .stSelectbox > div > div > small,
    .stSlider > div > div > small,
    small {
      color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Theme button specific - ensure visibility */
    [data-testid*="column"] button {
      min-height: 38px;
    }

    .badge {
      display: inline-block;
      padding: 8px 16px;
      border-radius: 999px;
      background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.3) 0%, 
        rgba(255, 255, 255, 0.2) 100%);
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.4);
      color: #2d3748;
      font-weight: 600;
      box-shadow: 0 4px 15px rgba(31, 38, 135, 0.2);
    }

    /* Floating animation for emojis */
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-20px); }
    }

    .floating-emoji {
      display: inline-block;
      animation: float 3s ease-in-out infinite;
    }
    
    /* Final overrides for visibility */
    .stMarkdown > div > p {
      color: white !important;
    }
    
    /* Ensure headers in main content are visible */
    .stMarkdown h3 {
      color: white !important;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Select boxes need dark text */
    [data-baseweb="select"] {
      background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    [data-baseweb="select"] * {
      color: #2d3748 !important;
    }
    </style>
    
    <div class="stars"></div>
    <div class="cloud-container">
        <div class="cloud">☁️</div>
        <div class="cloud">☁️</div>
        <div class="cloud">☁️</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated header with floating emojis
    st.markdown(
        """
        <h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0;'>
            <span class='floating-emoji' style='animation-delay: 0s;'>🌙</span>
            <span class='floating-emoji' style='animation-delay: 0.5s;'>✨</span>
            Bedtime Story Generator
            <span class='floating-emoji' style='animation-delay: 1s;'>✨</span>
            <span class='floating-emoji' style='animation-delay: 1.5s;'>🌙</span>
        </h1>
        <p style='text-align: center; font-size: 1.2rem; color: #ffffff; margin-top: 10px;'>
            <span style='background: linear-gradient(90deg, #ffd93d, #6bcf7f, #ff6b9d, #c7ceea); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-weight: 600;'>
                🦄 Create magical bedtime stories for sweet dreams! 🌈
            </span>
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    # Sidebar for API configuration
    with st.sidebar:
        st.markdown(
            "<h2 style='text-align: center;'>🔮 <span style='background: linear-gradient(90deg, #ffd93d, #6bcf7f); "
            "-webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Magic Settings</span> 🔮</h2>",
            unsafe_allow_html=True
        )
        
        # API Key section with glass container
        st.markdown(
            "<h3 style='text-align: center;'>"
            "<span class='floating-emoji'>🔑</span> "
            "OpenAI API Key"
            "</h3>",
            unsafe_allow_html=True
        )
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to generate stories",
            label_visibility="collapsed"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.markdown(
                """
                <div class='glass-card' style='text-align: center; background: linear-gradient(135deg, 
                    rgba(107, 207, 127, 0.2), rgba(165, 228, 255, 0.2));'>
                    <span style='font-size: 2rem;'>✅</span>
                    <p style='margin: 10px 0;'>
                        <b style='font-size: 1.1rem; color: #6bcf7f;'>API Key Configured!</b><br>
                        Ready to create magical stories!
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class='glass-card' style='text-align: center;'>
                    <span style='font-size: 2rem;'>🔑</span>
                    <p style='margin: 10px 0;'>
                        <b>Enter your API key above</b><br>
                        to unlock magical storytelling!
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Voice selection with glass container
        st.markdown(
            "<h3 style='text-align: center;'>"
            "<span class='floating-emoji'>🎤</span> "
            "Narrator Voice"
            "</h3>",
            unsafe_allow_html=True
        )
        selected_voice_key = st.selectbox(
            "Choose a voice",
            options=list(VOICE_OPTIONS.keys()),
            format_func=lambda x: VOICE_OPTIONS[x],
            index=list(VOICE_OPTIONS.keys()).index(VOICE),
            help="Select the voice for story narration",
            label_visibility="collapsed"
        )
        
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; background: linear-gradient(135deg, 
                rgba(255, 202, 212, 0.2), rgba(199, 206, 234, 0.2));'>
                <span style='font-size: 2rem;'>🎭</span>
                <p style='margin: 10px 0;'>
                    Your narrator will be<br>
                    <b style='font-size: 1.3rem; color: #ffd93d;'>{VOICE_OPTIONS[selected_voice_key]}</b><br>
                    Perfect for bedtime tales!
                </p>
                <span style='font-size: 0.9rem;'>Ready to tell your story! 🌟</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown(
            """
            <div class='glass-card' style='text-align: center; padding: 15px;'>
                <span style='font-size: 2rem;'>🎭</span>
                <p style='font-size: 0.9rem; margin-top: 10px;'>
                    <b>Fun Fact!</b><br>
                    Stories are created by magical AI friends<br>
                    who love making children smile! 🌟
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Story theme input with animated icon
        st.markdown(
            "<h3 style='text-align: center;'>"
            "<span class='floating-emoji'>🎨</span> "
            "What should the story be about?"
            "</h3>",
            unsafe_allow_html=True
        )
        
        # Age range selection
        age_range = st.select_slider(
            "Age Range",
            options=AGE_RANGES,
            value="4-8 years",
            help="Select the appropriate age range for the story"
        )
        
        # Show theme suggestions with colorful design
        st.markdown(
            "<p style='text-align: center; font-weight: 600; font-size: 1.1rem;'>"
            "<span class='floating-emoji'>💫</span> "
            "Choose a magical theme or create your own!"
            "</p>",
            unsafe_allow_html=True
        )
        themes = get_age_appropriate_themes(age_range)
        theme_cols = st.columns(2)
        
        for i, theme in enumerate(themes):
            with theme_cols[i % 2]:
                if st.button(
                    f"✨ {theme}",
                    key=f"theme_{i}",
                    use_container_width=True
                ):
                    st.session_state.selected_theme = theme
        
        # Custom theme input
        theme_input = st.text_area(
            "Or describe your own story idea:",
            placeholder=(
                "E.g., A brave little star who helps lost "
                "clouds find their way home..."
            ),
            height=100,
            value=getattr(st.session_state, "selected_theme", "")
        )
        
        # Story options
        include_moral = st.checkbox(
            "Include a gentle life lesson",
            value=True,
            help="Add a subtle moral or lesson to the story"
        )
    
    with col2:
        # Duration settings with playful design
        st.markdown(
            "<h3 style='text-align: center;'>"
            "<span class='floating-emoji'>⏱️</span> "
            "How long should the adventure be?"
            "</h3>",
            unsafe_allow_html=True
        )
        duration = st.slider(
            "Duration (minutes)",
            min_value=MIN_DURATION_MINUTES,
            max_value=MAX_DURATION_MINUTES,
            value=DEFAULT_DURATION_MINUTES,
            step=1,
            help=f"How long should the story be? "
                 f"({MIN_DURATION_MINUTES}-{MAX_DURATION_MINUTES} minutes)"
        )
        
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; background: linear-gradient(135deg, 
                rgba(107, 207, 127, 0.2), rgba(165, 228, 255, 0.2));'>
                <span style='font-size: 2rem;'>📖</span>
                <p style='margin: 10px 0;'>
                    Your magical story will be<br>
                    <b style='font-size: 1.3rem; color: #ffd93d;'>{duration} minutes</b><br>
                    of pure adventure!
                </p>
                <span style='font-size: 0.9rem;'>Perfect for sweet dreams! 😴</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Fun facts box with animations
        st.markdown(
            """
            <h3 style='text-align: center;'>
                <span class='floating-emoji'>🌟</span> Did you know?
            </h3>
            <div class='glass-card' style='background: linear-gradient(135deg, 
                rgba(255, 202, 212, 0.2), rgba(199, 206, 234, 0.2));'>
                <div style='text-align: center; font-size: 0.95rem;'>
                    <p>📚 Stories make your imagination grow!</p>
                    <p>💤 They help you have the best dreams!</p>
                    <p>💕 Story time = Family fun time!</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Generate story button
    st.markdown("---")
    
    if st.button(
        "🪄✨ Create My Magical Story! ✨🪄",
        type="primary",
        use_container_width=True,
        disabled=not api_key or not theme_input
    ):
        if not api_key:
            st.error("🔑 Please enter your OpenAI API key in the sidebar!")
        elif not theme_input:
            st.error("🎨 Please describe what your story should be about!")
        else:
            with st.spinner("✨ Creating your magical story..."):
                try:
                    # Generate story
                    story_output, audio_path = handle_async(
                        create_bedtime_story_with_audio(
                            theme=theme_input,
                            age_range=age_range,
                            duration_minutes=validate_duration(duration),
                            voice=selected_voice_key,
                            include_moral=include_moral
                        )
                    )
                    
                    # Store in session state
                    st.session_state.story_generated = True
                    st.session_state.current_story = story_output
                    st.session_state.audio_path = audio_path
                    
                    st.success("🎉 Hooray! Your magical story is ready! 🎊")
                    st.balloons()
                    st.snow()
                    
                except Exception as e:
                    st.error(f"😔 Oops! Something went wrong: {str(e)}")
    
    # Display generated story
    if st.session_state.story_generated and st.session_state.current_story:
        st.markdown("---")
        
        # Animated story title
        st.markdown(
            f"""
            <h2 style='text-align: center; font-size: 2.5rem; margin: 30px 0;'>
                <span class='floating-emoji'>📖</span>
                <span style='background: linear-gradient(90deg, #ffd93d, #6bcf7f, #ff6b9d); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    {st.session_state.current_story.title}
                </span>
                <span class='floating-emoji'>✨</span>
            </h2>
            """,
            unsafe_allow_html=True
        )
        
        # Audio player with colorful design
        st.markdown(
            """
            <h3 style='text-align: center;'>
                <span class='floating-emoji'>🎧</span>
                <span style='background: linear-gradient(90deg, #90cdf4, #fbb6ce); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    Listen to Your Magical Story
                </span>
                <span class='floating-emoji'>🎵</span>
            </h3>
            """,
            unsafe_allow_html=True
        )
        if st.session_state.audio_path and Path(st.session_state.audio_path).exists():
            st.audio(str(st.session_state.audio_path), format="audio/mp3")
            
            # Download button
            with open(st.session_state.audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                filename = f"bedtime_story_{st.session_state.current_story.title.lower().replace(' ', '_')}.mp3"
                
                st.download_button(
                    label="🎁 Save My Story Forever! 💝",
                    data=audio_bytes,
                    file_name=filename,
                    mime="audio/mp3"
                )
        
        # Story text with magical design
        with st.expander("📜✨ Read the Magical Story ✨📜", expanded=True):
            st.markdown(
                f"<div class='story-box'>{st.session_state.current_story.story}</div>",
                unsafe_allow_html=True
            )
        
        # Story info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "⏱️ Duration",
                f"{st.session_state.current_story.estimated_duration_minutes} min"
            )
        with col2:
            st.metric("🎯 Age Range", age_range)
        with col3:
            st.metric("🎤 Voice", VOICE_OPTIONS[selected_voice_key].split()[0])
        
        # Generate another story button with animation
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🌈 Create Another Magical Adventure! 🦄", use_container_width=True):
            st.session_state.story_generated = False
            st.session_state.current_story = None
            st.session_state.audio_path = None
            st.rerun()
    
    # Animated footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <p style='font-size: 1.1rem; color: #ffffff;'>
                <span class='floating-emoji' style='animation-delay: 0s;'>🌙</span>
                <span class='floating-emoji' style='animation-delay: 0.3s;'>💤</span>
                <span style='background: linear-gradient(90deg, #ffd93d, #ff6b9d, #6bcf7f); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                            font-weight: 600;'>
                    Sweet Dreams, Little Dreamer!
                </span>
                <span class='floating-emoji' style='animation-delay: 0.6s;'>⭐</span>
                <span class='floating-emoji' style='animation-delay: 0.9s;'>🌟</span>
            </p>
            <p style='font-size: 0.9rem; color: #e8f4fd; margin-top: 10px;'>
                Made with <span style='color: #ff6b9d; font-size: 1.2rem;'>❤️</span> 
                for magical bedtime adventures
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 