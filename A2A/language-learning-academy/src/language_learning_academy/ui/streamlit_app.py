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

UI_LANGUAGES = ["English", "Hindi", "French"]
NATIVE_LANG_OPTS = ["English", "Hindi", "French", "Spanish", "German", "Italian", 
                    "Portuguese", "Japanese", "Chinese", "Korean"]
LEARNING_GOALS = ["Travel", "Business", "Exam prep"]
TUTOR_PERSONAS = ["Friendly", "Formal", "Coach"]
CORRECTION_LEVELS = ["Gentle", "Standard", "Strict"]

TRANSLATIONS = {
    "en": {
        "profile": "Profile",
        "personalization": "Personalization",
        "native_language": "Native Language",
        "ui_language": "UI Language",
        "learning_goal": "Learning Goal",
        "tutor_persona": "Tutor Persona",
        "correction_strictness": "Correction Strictness",
        "performance_settings": "Performance Settings",
        "learning_preferences": "Learning Preferences",
        "target_language": "Target Language",
        "proficiency_level": "Proficiency Level",
        "title": "Polyglot Academy",
        "subtitle": "Multi-Agent Language Learning Platform",
        "tagline": "Master any language with AI-powered tutors, real-time feedback, and personalized learning paths",
        "ai_tutors": "AI Tutors",
        "personalized": "Personalized",
        "real_time": "Real-time",
        "languages_count": "8 Languages",
        "powered_by": "gpt-5-2025-08-07 Powered",
        "supported_languages": "Supported Languages",
        "skill_levels": "Skill Levels",
        "learning_modes": "Learning Modes",
        "ai_possibilities": "AI Possibilities",
        "system_online": "Multi-Agent System Online",
        "system_offline": "Multi-Agent System Offline",
        "all_tutors_ready": "All AI tutors are ready to assist with your language learning journey!",
        "ensure_running": "Please ensure the agent is running on localhost:9999 with proper LLM API keys configured",
        "learning_hub": "Learning Hub",
        "customize_experience": "Customize your learning experience",
        "enable_streaming": "Enable Real-time Streaming",
        "streaming_help": "Get real-time responses from the LLM for immediate feedback",
        "choose_language": "Choose the language you want to learn",
        "select_skill": "Select your current skill level",
        "ai_engine_status": "AI Engine Status",
        "model_source": "Model Source",
        "ai_model": "AI Model",
        "quick_actions": "Quick Actions",
        "languages_btn": "Languages",
        "refresh_btn": "Refresh",
        "show_languages": "Show available languages",
        "refresh_connection": "Refresh connection",
        "currently_learning": "Currently learning",
        "at_level": "at",
        "level": "level",
        "vocabulary": "Vocabulary",
        "grammar": "Grammar",
        "conversation": "Conversation",
        "quiz": "Quiz",
        "translation": "Translation",
        "custom_query": "Custom Query",
        "vocab_academy": "AI-Powered Vocabulary Academy",
        "vocab_desc": "Expand your vocabulary with our intelligent tutoring system. Get personalized lessons with pronunciation guides, cultural context, and real-world usage examples.",
        "select_category": "Select vocabulary category:",
        "generate_lesson": "Generate Vocabulary Lesson",
        "create_lesson": "Create a personalized lesson",
        "pro_tips": "Pro Tips for Vocabulary Learning",
        "grammar_center": "AI Grammar Mastery Center",
        "grammar_desc": "Master grammar through intelligent explanations, pattern recognition, and practical exercises. Our AI tutors break down complex rules into digestible lessons.",
        "choose_focus": "Choose grammar focus:",
        "start_lesson": "Start Grammar Lesson",
        "convo_academy": "AI Conversation Academy",
        "convo_desc": "Practice real-world conversations with our intelligent coaching system. Build confidence through immersive scenarios with cultural insights and pronunciation guidance.",
        "select_scenario": "Select conversation scenario:",
        "start_practice": "Start Conversation Practice",
        "quiz_generator": "AI Quiz Generator",
        "quiz_desc": "Test and reinforce your knowledge with intelligent, adaptive quizzes. Our AI creates personalized assessments with detailed explanations to accelerate your learning.",
        "quiz_category": "Quiz category:",
        "challenge_level": "Challenge level:",
        "generate_quiz": "Generate Smart Quiz",
        "translation_studio": "AI Translation Studio",
        "translation_desc": "Experience intelligent translation that goes beyond words. Our AI provides cultural context, alternative expressions, and nuanced interpretations for professional-quality translations.",
        "from_language": "From language:",
        "to_language": "To language:",
        "enter_text": "Enter text to translate:",
        "smart_translate": "Smart Translate",
        "personal_tutor": "Personal AI Language Tutor",
        "tutor_desc": "Your dedicated AI language consultant is here to answer any question, solve learning challenges, and provide personalized guidance for your journey.",
        "what_to_learn": "What would you like to learn or explore?",
        "expert_mode": "Expert Mode",
        "include_examples": "Include Examples",
        "consult_tutor": "Consult AI Tutor",
        "technology": "AI Technology",
        "features": "Features",
        "built_with": "Built with ❤️ using Streamlit & A2A Protocol • Advanced AI for Language Excellence"
    },
    "hi": {
        "profile": "प्रोफ़ाइल",
        "personalization": "वैयक्तिकरण",
        "native_language": "मातृभाषा",
        "ui_language": "UI भाषा",
        "learning_goal": "सीखने का लक्ष्य",
        "tutor_persona": "शिक्षक व्यक्तित्व",
        "correction_strictness": "सुधार सख्ती",
        "performance_settings": "प्रदर्शन सेटिंग्स",
        "learning_preferences": "सीखने की प्राथमिकताएं",
        "target_language": "लक्ष्य भाषा",
        "proficiency_level": "दक्षता स्तर",
        "title": "पॉलीग्लॉट अकादमी",
        "subtitle": "मल्टी-एजेंट भाषा सीखने का मंच",
        "tagline": "AI-संचालित ट्यूटर्स, रीयल-टाइम फीडबैक और व्यक्तिगत सीखने के मार्गों के साथ किसी भी भाषा में महारत हासिल करें",
        "ai_tutors": "AI ट्यूटर्स",
        "personalized": "व्यक्तिगत",
        "real_time": "रीयल-टाइम",
        "languages_count": "8 भाषाएं",
        "powered_by": "gpt-5-2025-08-07 संचालित",
        "supported_languages": "समर्थित भाषाएं",
        "skill_levels": "कौशल स्तर",
        "learning_modes": "सीखने के मोड",
        "ai_possibilities": "AI संभावनाएं",
        "system_online": "मल्टी-एजेंट सिस्टम ऑनलाइन",
        "system_offline": "मल्टी-एजेंट सिस्टम ऑफलाइन",
        "all_tutors_ready": "सभी AI ट्यूटर आपकी भाषा सीखने की यात्रा में सहायता के लिए तैयार हैं!",
        "ensure_running": "कृपया सुनिश्चित करें कि एजेंट localhost:9999 पर उचित LLM API कुंजियों के साथ चल रहा है",
        "learning_hub": "लर्निंग हब",
        "customize_experience": "अपना सीखने का अनुभव अनुकूलित करें",
        "enable_streaming": "रीयल-टाइम स्ट्रीमिंग सक्षम करें",
        "streaming_help": "तत्काल फीडबैक के लिए LLM से रीयल-टाइम प्रतिक्रियाएं प्राप्त करें",
        "choose_language": "वह भाषा चुनें जो आप सीखना चाहते हैं",
        "select_skill": "अपना वर्तमान कौशल स्तर चुनें",
        "ai_engine_status": "AI इंजन स्थिति",
        "model_source": "मॉडल स्रोत",
        "ai_model": "AI मॉडल",
        "quick_actions": "त्वरित कार्रवाइयां",
        "languages_btn": "भाषाएं",
        "refresh_btn": "रीफ्रेश",
        "show_languages": "उपलब्ध भाषाएं दिखाएं",
        "refresh_connection": "कनेक्शन रीफ्रेश करें",
        "currently_learning": "वर्तमान में सीख रहे हैं",
        "at_level": "स्तर पर",
        "level": "स्तर",
        "vocabulary": "शब्दावली",
        "grammar": "व्याकरण",
        "conversation": "बातचीत",
        "quiz": "प्रश्नोत्तरी",
        "translation": "अनुवाद",
        "custom_query": "कस्टम प्रश्न",
        "vocab_academy": "AI-संचालित शब्दावली अकादमी",
        "vocab_desc": "हमारी बुद्धिमान ट्यूटरिंग प्रणाली के साथ अपनी शब्दावली का विस्तार करें। उच्चारण गाइड, सांस्कृतिक संदर्भ और वास्तविक उपयोग उदाहरणों के साथ व्यक्तिगत पाठ प्राप्त करें।",
        "select_category": "शब्दावली श्रेणी चुनें:",
        "generate_lesson": "शब्दावली पाठ जेनरेट करें",
        "create_lesson": "व्यक्तिगत पाठ बनाएं",
        "pro_tips": "शब्दावली सीखने के लिए प्रो टिप्स",
        "grammar_center": "AI व्याकरण महारत केंद्र",
        "grammar_desc": "बुद्धिमान स्पष्टीकरण, पैटर्न पहचान और व्यावहारिक अभ्यासों के माध्यम से व्याकरण में महारत हासिल करें। हमारे AI ट्यूटर जटिल नियमों को पचने योग्य पाठों में तोड़ देते हैं।",
        "choose_focus": "व्याकरण फोकस चुनें:",
        "start_lesson": "व्याकरण पाठ शुरू करें",
        "convo_academy": "AI बातचीत अकादमी",
        "convo_desc": "हमारी बुद्धिमान कोचिंग प्रणाली के साथ वास्तविक दुनिया की बातचीत का अभ्यास करें। सांस्कृतिक अंतर्दृष्टि और उच्चारण मार्गदर्शन के साथ immersive परिदृश्यों के माध्यम से आत्मविश्वास बनाएं।",
        "select_scenario": "बातचीत परिदृश्य चुनें:",
        "start_practice": "बातचीत अभ्यास शुरू करें",
        "quiz_generator": "AI प्रश्नोत्तरी जेनरेटर",
        "quiz_desc": "बुद्धिमान, अनुकूली प्रश्नोत्तरी के साथ अपने ज्ञान का परीक्षण और मजबूत करें। हमारा AI आपके सीखने को तेज करने के लिए विस्तृत स्पष्टीकरण के साथ व्यक्तिगत मूल्यांकन बनाता है।",
        "quiz_category": "प्रश्नोत्तरी श्रेणी:",
        "challenge_level": "चुनौती स्तर:",
        "generate_quiz": "स्मार्ट प्रश्नोत्तरी जेनरेट करें",
        "translation_studio": "AI अनुवाद स्टूडियो",
        "translation_desc": "बुद्धिमान अनुवाद का अनुभव करें जो शब्दों से परे जाता है। हमारा AI पेशेवर-गुणवत्ता अनुवादों के लिए सांस्कृतिक संदर्भ, वैकल्पिक अभिव्यक्तियां और सूक्ष्म व्याख्याएं प्रदान करता है।",
        "from_language": "किस भाषा से:",
        "to_language": "किस भाषा में:",
        "enter_text": "अनुवाद करने के लिए टेक्स्ट दर्ज करें:",
        "smart_translate": "स्मार्ट अनुवाद",
        "personal_tutor": "व्यक्तिगत AI भाषा ट्यूटर",
        "tutor_desc": "आपका समर्पित AI भाषा सलाहकार किसी भी प्रश्न का उत्तर देने, सीखने की चुनौतियों को हल करने और आपकी यात्रा के लिए व्यक्तिगत मार्गदर्शन प्रदान करने के लिए यहां है।",
        "what_to_learn": "आप क्या सीखना या खोजना चाहेंगे?",
        "expert_mode": "विशेषज्ञ मोड",
        "include_examples": "उदाहरण शामिल करें",
        "consult_tutor": "AI ट्यूटर से परामर्श करें",
        "technology": "AI प्रौद्योगिकी",
        "features": "विशेषताएं",
        "built_with": "❤️ के साथ Streamlit और A2A प्रोटोकॉल का उपयोग करके बनाया गया • भाषा उत्कृष्टता के लिए उन्नत AI"
    },
    "fr": {
        "profile": "Profil",
        "personalization": "Personnalisation",
        "native_language": "Langue maternelle",
        "ui_language": "Langue de l'interface",
        "learning_goal": "Objectif d'apprentissage",
        "tutor_persona": "Personnalité du tuteur",
        "correction_strictness": "Niveau de correction",
        "performance_settings": "Paramètres de performance",
        "learning_preferences": "Préférences d'apprentissage",
        "target_language": "Langue cible",
        "proficiency_level": "Niveau de compétence",
        "title": "Académie Polyglotte",
        "subtitle": "Plateforme d'apprentissage des langues multi-agents",
        "tagline": "Maîtrisez n'importe quelle langue avec des tuteurs alimentés par l'IA, des retours en temps réel et des parcours d'apprentissage personnalisés",
        "ai_tutors": "Tuteurs IA",
        "personalized": "Personnalisé",
        "real_time": "Temps réel",
        "languages_count": "8 Langues",
        "powered_by": "Alimenté par gpt-5-2025-08-07",
        "supported_languages": "Langues prises en charge",
        "skill_levels": "Niveaux de compétence",
        "learning_modes": "Modes d'apprentissage",
        "ai_possibilities": "Possibilités IA",
        "system_online": "Système multi-agents en ligne",
        "system_offline": "Système multi-agents hors ligne",
        "all_tutors_ready": "Tous les tuteurs IA sont prêts à vous aider dans votre parcours d'apprentissage des langues!",
        "ensure_running": "Veuillez vous assurer que l'agent fonctionne sur localhost:9999 avec les clés API LLM appropriées configurées",
        "learning_hub": "Centre d'apprentissage",
        "customize_experience": "Personnalisez votre expérience d'apprentissage",
        "enable_streaming": "Activer le streaming en temps réel",
        "streaming_help": "Obtenez des réponses en temps réel du LLM pour un retour immédiat",
        "choose_language": "Choisissez la langue que vous voulez apprendre",
        "select_skill": "Sélectionnez votre niveau de compétence actuel",
        "ai_engine_status": "État du moteur IA",
        "model_source": "Source du modèle",
        "ai_model": "Modèle IA",
        "quick_actions": "Actions rapides",
        "languages_btn": "Langues",
        "refresh_btn": "Actualiser",
        "show_languages": "Afficher les langues disponibles",
        "refresh_connection": "Actualiser la connexion",
        "currently_learning": "Apprend actuellement",
        "at_level": "au niveau",
        "level": "niveau",
        "vocabulary": "Vocabulaire",
        "grammar": "Grammaire",
        "conversation": "Conversation",
        "quiz": "Quiz",
        "translation": "Traduction",
        "custom_query": "Requête personnalisée",
        "vocab_academy": "Académie de vocabulaire alimentée par l'IA",
        "vocab_desc": "Élargissez votre vocabulaire avec notre système de tutorat intelligent. Obtenez des leçons personnalisées avec des guides de prononciation, un contexte culturel et des exemples d'utilisation réels.",
        "select_category": "Sélectionnez la catégorie de vocabulaire:",
        "generate_lesson": "Générer une leçon de vocabulaire",
        "create_lesson": "Créer une leçon personnalisée",
        "pro_tips": "Conseils pro pour l'apprentissage du vocabulaire",
        "grammar_center": "Centre de maîtrise de la grammaire IA",
        "grammar_desc": "Maîtrisez la grammaire grâce à des explications intelligentes, à la reconnaissance de modèles et à des exercices pratiques. Nos tuteurs IA décomposent les règles complexes en leçons digestes.",
        "choose_focus": "Choisissez le focus grammatical:",
        "start_lesson": "Commencer la leçon de grammaire",
        "convo_academy": "Académie de conversation IA",
        "convo_desc": "Pratiquez des conversations du monde réel avec notre système de coaching intelligent. Développez votre confiance grâce à des scénarios immersifs avec des informations culturelles et des conseils de prononciation.",
        "select_scenario": "Sélectionnez le scénario de conversation:",
        "start_practice": "Commencer la pratique de conversation",
        "quiz_generator": "Générateur de quiz IA",
        "quiz_desc": "Testez et renforcez vos connaissances avec des quiz intelligents et adaptatifs. Notre IA crée des évaluations personnalisées avec des explications détaillées pour accélérer votre apprentissage.",
        "quiz_category": "Catégorie de quiz:",
        "challenge_level": "Niveau de défi:",
        "generate_quiz": "Générer un quiz intelligent",
        "translation_studio": "Studio de traduction IA",
        "translation_desc": "Découvrez une traduction intelligente qui va au-delà des mots. Notre IA fournit un contexte culturel, des expressions alternatives et des interprétations nuancées pour des traductions de qualité professionnelle.",
        "from_language": "De la langue:",
        "to_language": "Vers la langue:",
        "enter_text": "Entrez le texte à traduire:",
        "smart_translate": "Traduction intelligente",
        "personal_tutor": "Tuteur personnel de langue IA",
        "tutor_desc": "Votre consultant linguistique IA dédié est là pour répondre à toute question, résoudre les défis d'apprentissage et fournir des conseils personnalisés pour votre parcours.",
        "what_to_learn": "Qu'aimeriez-vous apprendre ou explorer?",
        "expert_mode": "Mode expert",
        "include_examples": "Inclure des exemples",
        "consult_tutor": "Consulter le tuteur IA",
        "technology": "Technologie IA",
        "features": "Fonctionnalités",
        "built_with": "Construit avec ❤️ en utilisant Streamlit et le protocole A2A • IA avancée pour l'excellence linguistique"
    }
}

def t(key: str) -> str:
    ui_lang = st.session_state.get('ui_language', 'English')
    lang_code = {'English': 'en', 'Hindi': 'hi', 'French': 'fr'}.get(ui_lang, 'en')
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['en']).get(key, key)

def build_profile_prompt(text: str) -> str:
    p = st.session_state.get('profile', {})
    if not p:
        return text
    preamble = (
        f"Native language: {p.get('native_language', 'English')}. "
        f"Learning goal: {p.get('learning_goal', 'Travel')}. "
        f"Tutor persona: {p.get('tutor_persona', 'Friendly')}. "
        f"Correction strictness: {p.get('correction_strictness', 'Standard')}. "
        "Provide explanations in the native language while leaving target-language examples unchanged."
    )
    return f"{preamble}\n\n{text}"

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

async def send_message_to_agent(message_text: str, use_streaming: bool = False, profile: dict | None = None) -> dict[str, Any]:
    try:
        agent_card = get_agent_card()
        if not agent_card:
            return {"error": "Could not connect to agent"}

        async with httpx.AsyncClient(timeout=200.0) as httpx_client:
            client = A2AClient(
                httpx_client=httpx_client,
                agent_card=agent_card
            )

            message_metadata = {}
            if profile:
                message_metadata['profile'] = profile
            
            message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': message_text}
                    ],
                    'message_id': uuid4().hex,
                    'metadata': message_metadata,
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
# For OpenAI gpt-5-2025-08-07:
export OPENAI_API_KEY=your_openai_api_key_here
export OPENAI_MODEL=gpt-5-2025-08-07
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

st.markdown(f"""
<div class="hero-section">
    <div class="hero-title">🌟 {t('title')}</div>
    <div class="hero-subtitle">{t('subtitle')}</div>
    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">{t('tagline')}</p>
    <div class="hero-badges">
        <div class="badge">🤖 {t('ai_tutors')}</div>
        <div class="badge">🎯 {t('personalized')}</div>
        <div class="badge">⚡ {t('real_time')}</div>
        <div class="badge">🌍 {t('languages_count')}</div>
        <div class="badge">🧠 {t('powered_by')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-container">
    <div class="metric-card">
        <span class="metric-number">8</span>
        <div class="metric-label">{t('supported_languages')}</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">3</span>
        <div class="metric-label">{t('skill_levels')}</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">6</span>
        <div class="metric-label">{t('learning_modes')}</div>
    </div>
    <div class="metric-card">
        <span class="metric-number">∞</span>
        <div class="metric-label">{t('ai_possibilities')}</div>
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
    st.markdown(f"""
    <div class="status-card status-success">
        <h3 style="margin: 0; color: #155724;">✅ {t('system_online')}</h3>
        <p style="margin: 0.5rem 0 0 0; color: #155724;">{t('all_tutors_ready')}</p>
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
    st.markdown(f"""
    <div class="status-card status-error">
        <h3 style="margin: 0; color: #721c24;">❌ {t('system_offline')}</h3>
        <p style="margin: 0.5rem 0 0 0; color: #721c24;">{t('ensure_running')}</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1rem 0;">
    <h1 style="color: white; margin: 0; font-size: 1.8rem;">🌍 {t('learning_hub')}</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">{t('customize_experience')}</p>
</div>
""", unsafe_allow_html=True)

if 'profile' not in st.session_state:
    st.session_state.profile = {
        'native_language': 'English',
        'ui_language': 'English',
        'learning_goal': 'Travel',
        'tutor_persona': 'Friendly',
        'correction_strictness': 'Standard'
    }

st.sidebar.markdown(f"### 🌐 {t('profile')}")
col1, col2 = st.sidebar.columns(2)
with col1:
    native_lang = st.sidebar.selectbox(
        f"🗣️ {t('native_language')}:",
        NATIVE_LANG_OPTS,
        index=NATIVE_LANG_OPTS.index(st.session_state.profile.get('native_language', 'English')),
        key="native_lang_select",
        help="Your native language for explanations"
    )
with col2:
    ui_lang = st.sidebar.selectbox(
        f"💻 {t('ui_language')}:",
        UI_LANGUAGES,
        index=UI_LANGUAGES.index(st.session_state.profile.get('ui_language', 'English')),
        key="ui_lang_select",
        help="Interface display language"
    )

if native_lang != st.session_state.profile.get('native_language'):
    st.session_state.profile['native_language'] = native_lang
if ui_lang != st.session_state.profile.get('ui_language'):
    st.session_state.profile['ui_language'] = ui_lang
    st.session_state.ui_language = ui_lang
    st.rerun()

st.sidebar.markdown(f"### 🎨 {t('personalization')}")
learning_goal = st.sidebar.selectbox(
    f"🎯 {t('learning_goal')}:",
    LEARNING_GOALS,
    index=LEARNING_GOALS.index(st.session_state.profile.get('learning_goal', 'Travel')),
    key="goal_select",
    help="Your primary motivation for learning"
)
tutor_persona = st.sidebar.selectbox(
    f"👤 {t('tutor_persona')}:",
    TUTOR_PERSONAS,
    index=TUTOR_PERSONAS.index(st.session_state.profile.get('tutor_persona', 'Friendly')),
    key="persona_select",
    help="Teaching style preference"
)
correction_level = st.sidebar.selectbox(
    f"✏️ {t('correction_strictness')}:",
    CORRECTION_LEVELS,
    index=CORRECTION_LEVELS.index(st.session_state.profile.get('correction_strictness', 'Standard')),
    key="correction_select",
    help="How strictly to correct mistakes"
)

st.session_state.profile['learning_goal'] = learning_goal
st.session_state.profile['tutor_persona'] = tutor_persona
st.session_state.profile['correction_strictness'] = correction_level

st.sidebar.markdown(f"### ⚡ {t('performance_settings')}")
streaming_enabled = st.sidebar.checkbox(
    f"🔄 {t('enable_streaming')}",
    value=False,
    help=t('streaming_help')
)

st.sidebar.markdown(f"### 🎯 {t('learning_preferences')}")
selected_language = st.sidebar.selectbox(
    f"🌐 {t('target_language')}:",
    SUPPORTED_LANGUAGES,
    index=0,
    help=t('choose_language')
).title()

selected_level = st.sidebar.selectbox(
    f"📊 {t('proficiency_level')}:",
    LEVELS,
    index=0,
    help=t('select_skill')
).title()

st.sidebar.markdown("---")

st.sidebar.markdown(f"### 🧠 {t('ai_engine_status')}")
openai_model = os.getenv('OPENAI_MODEL', 'gpt-5-2025-08-07')

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
    <div style="color: white; font-weight: 500;">🤖 {t('model_source')}</div>
    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">OPENAI</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
    <div style="color: white; font-weight: 500;">🚀 {t('ai_model')}</div>
    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">{openai_model}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"### 🛠️ {t('quick_actions')}")

sidebar_response_placeholder = st.sidebar.empty()

col1, col2 = st.sidebar.columns(2)
with col1:
    lang_info_clicked = st.button(f"ℹ️ {t('languages_btn')}", key="lang_info", help=t('show_languages'))

with col2:
    if st.button(f"🔄 {t('refresh_btn')}", key="refresh_conn", help=t('refresh_connection')):
        st.session_state.agent_status = "checking"
        st.rerun()

if lang_info_clicked:
    with st.spinner("🤖 Querying AI tutors..."):
        prompt = build_profile_prompt("What languages do you support and what can you help me learn? Give me a comprehensive overview with your capabilities for each language.")
        response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
    <p>🎓 {t('currently_learning')} <strong>{selected_language}</strong><br/>
    {t('at_level')} <strong>{selected_level}</strong> {t('level')}</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    f"📚 {t('vocabulary')}", f"📝 {t('grammar')}", f"💬 {t('conversation')}", f"🧩 {t('quiz')}", f"🌐 {t('translation')}", f"🎯 {t('custom_query')}"
])

with tab1:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">📚 {t('vocab_academy')}</div>
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
            f"🏷️ {t('select_category')}",
            ["general", "greetings", "food", "family", "travel", "business", "technology", "emotions", "nature"],
            key="vocab_type",
            help="Choose a category that interests you most"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        vocab_clicked = st.button(f"🎯 {t('generate_lesson')}", key="vocab_btn", help=t('create_lesson'))

    response_placeholder = st.empty()

    if vocab_clicked:
        query = f"Create a comprehensive {selected_language} vocabulary lesson for {vocab_type} words at {selected_level} level. Include: 1) 10-15 essential words with pronunciation, 2) Example sentences with translations, 3) Cultural context and usage tips, 4) Memory techniques or mnemonics, 5) Practice exercises. Make it engaging and educational."
        prompt = build_profile_prompt(query)
        with st.spinner("🤖 AI tutors crafting your personalized vocabulary lesson..."):
            response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

        with response_placeholder.container():
            display_agent_response(response)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd, #f3e5f5); padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; border-left: 4px solid #2196f3;">
        <h4 style="margin: 0 0 0.5rem 0; color: #1976d2;">💡 {t('pro_tips')}</h4>
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
        <div class="feature-header">📝 {t('grammar_center')}</div>
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
            f"📖 {t('choose_focus')}",
            ["present tense", "past tense", "future tense", "subjunctive", "conditionals", "pronouns", "articles", "prepositions", "irregular verbs", "question formation"],
            key="grammar_topic",
            help="Select the grammar concept you want to master"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        grammar_clicked = st.button(f"🎓 {t('start_lesson')}", key="grammar_btn", help="Get comprehensive grammar instruction")

    grammar_response_placeholder = st.empty()

    if grammar_clicked:
        query = f"Create an in-depth {selected_language} grammar lesson on {grammar_topic} for {selected_level} learners. Include: 1) Clear rule explanations with visual patterns, 2) Common exceptions and irregularities, 3) Step-by-step conjugation guides, 4) 10+ practical examples with translations, 5) Common mistakes to avoid, 6) Practice exercises with solutions. Make it comprehensive yet easy to understand."
        prompt = build_profile_prompt(query)
        with st.spinner("🤖 AI grammar experts preparing your personalized lesson..."):
            response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
        <div class="feature-header">💬 {t('convo_academy')}</div>
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
            f"🎭 {t('select_scenario')}",
            ["restaurant", "directions", "hotel", "shopping", "airport", "café", "job interview", "doctor visit", "making friends", "business meeting", "phone call"],
            key="scenario",
            help="Choose a real-world situation to practice"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        convo_clicked = st.button(f"🗣️ {t('start_practice')}", key="convo_btn", help="Begin interactive role-play")

    convo_response_placeholder = st.empty()

    if convo_clicked:
        query = f"Create an immersive {scenario} conversation practice session in {selected_language} for {selected_level} level. Include: 1) Realistic dialogue with multiple turns, 2) Essential phrases and vocabulary, 3) Cultural etiquette and social cues, 4) Pronunciation tips for key expressions, 5) Alternative responses for different situations, 6) Common mistakes to avoid. Make it interactive and engaging like a real conversation coach."
        prompt = build_profile_prompt(query)
        with st.spinner("🤖 AI conversation coaches setting up your practice session..."):
            response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
        <div class="feature-header">🧩 {t('quiz_generator')}</div>
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
            f"🎪 {t('quiz_category')}",
            ["vocabulary", "translation", "grammar", "listening comprehension", "cultural knowledge", "mixed review"],
            key="quiz_type",
            help="Choose what aspect to focus on"
        )
    with col2:
        quiz_difficulty = st.selectbox(
            f"⚡ {t('challenge_level')}",
            LEVELS,
            key="quiz_diff",
            help="Select quiz difficulty"
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        quiz_clicked = st.button(f"🎯 {t('generate_quiz')}", key="quiz_btn", help="Create personalized assessment")

    quiz_response_placeholder = st.empty()

    if quiz_clicked:
        query = f"Create an engaging {quiz_type} quiz for {selected_language} at {quiz_difficulty} level. Include: 1) 8-10 well-crafted questions with multiple choice options, 2) Detailed explanations for both correct and incorrect answers, 3) Progressive difficulty within the quiz, 4) Cultural context where relevant, 5) Tips for improvement, 6) Score interpretation guide. Make it educational and motivating."
        prompt = build_profile_prompt(query)
        with st.spinner("🤖 AI assessment specialists generating your personalized quiz..."):
            response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">🌐 {t('translation_studio')}</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            {t('translation_desc')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            f"🔤 {t('from_language')}",
            ["Auto-detect"] + [lang.title() for lang in SUPPORTED_LANGUAGES],
            key="source_lang",
            help="Source language (auto-detect available)"
        )
    with col2:
        target_lang = st.selectbox(
            f"🎯 {t('to_language')}",
            [lang.title() for lang in SUPPORTED_LANGUAGES],
            index=0,
            key="target_lang",
            help="Target language for translation"
        )

    text_to_translate = st.text_area(
        f"📝 {t('enter_text')}",
        placeholder="Type or paste your text here... (supports multiple languages)",
        height=120,
        key="translate_text",
        help="Enter any text for intelligent translation with cultural context"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        translate_clicked = st.button(f"🚀 {t('smart_translate')}", key="translate_btn", help="Get intelligent translation with context")

    translate_response_placeholder = st.empty()

    if translate_clicked:
        if text_to_translate.strip():
            source = source_lang.lower() if source_lang != "Auto-detect" else "auto"
            target = target_lang.lower()
            query = f"Provide an intelligent translation from {source} to {target} for: '{text_to_translate}'. Include: 1) Primary translation, 2) Alternative expressions, 3) Cultural context and nuances, 4) Formality level analysis, 5) Usage tips, 6) Common variations. Make it comprehensive and culturally aware."
            prompt = build_profile_prompt(query)
            with st.spinner("🤖 AI linguists analyzing and translating with cultural intelligence..."):
                response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
        <div class="feature-header">🎯 {t('personal_tutor')}</div>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Your dedicated AI language consultant is here to answer any question, solve learning challenges, 
            and provide personalized guidance for your <strong>{selected_language}</strong> journey at the <strong>{selected_level}</strong> level.
        </p>
    </div>
    """, unsafe_allow_html=True)

    custom_query = st.text_area(
        f"💭 {t('what_to_learn')}",
        placeholder="Ask anything: grammar rules, cultural insights, pronunciation tips, study strategies, writing help, conversation practice, or language learning advice...",
        height=140,
        key="custom_query",
        help="Ask your AI tutor anything about language learning"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        advanced_mode = st.checkbox(
            f"🧠 {t('expert_mode')}",
            help="Get comprehensive responses with deep cultural insights and advanced explanations",
            key="expert_mode"
        )
    with col2:
        include_examples = st.checkbox(
            f"📚 {t('include_examples')}",
            help="Add practical examples and exercises to the response",
            value=True,
            key="include_examples"
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        custom_clicked = st.button(f"🚀 {t('consult_tutor')}", key="custom_btn", help="Get personalized language learning guidance")

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

            prompt = build_profile_prompt(enhanced_query)
            with st.spinner("🤖 AI tutors collaborating to craft your personalized response..."):
                response = run_async(send_message_to_agent(prompt, streaming_enabled, profile=st.session_state.profile))

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
st.markdown(f"### 🌟 {t('title')}")
st.markdown(f"**{t('subtitle')}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"#### 🤖 {t('technology')}")
    st.markdown("""
    - Powered by OpenAI gpt-5-2025-08-07
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
    st.markdown(f"#### 🎯 {t('features')}")
    st.markdown("""
    - Personalized learning paths
    - Interactive conversations
    - Intelligent assessments
    """)

st.markdown("---")
st.markdown(f"*{t('built_with')}*")
