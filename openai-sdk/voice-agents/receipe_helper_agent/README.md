# 🍳 AI Cooking Recipe Voice Guide

An AI-powered cooking assistant that generates personalized recipes from your available ingredients and provides step-by-step voice guidance for cooking.

## Features

- **Ingredient-based Recipe Generation**: Add your available ingredients and get custom recipes
- **Voice-Guided Cooking**: Natural-sounding voice instructions using OpenAI's TTS
- **Dietary Customization**: Specify dietary restrictions and cuisine preferences
- **Multiple Voice Options**: Choose from 9 different voice personalities
- **Recipe Export**: Download your voice guide for offline use

## Setup Instructions

### 1. Environment Setup

Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Configure OpenAI API Key

You have two options:

**Option A: Using the Streamlit UI (Recommended)**
- Run the app and enter your API key in the sidebar
- The key will be saved for the current session

**Option B: Using Environment Variables**
- Create a `.env` file in the project root:
```bash
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env
```

### 3. Run the Application

Activate the virtual environment and start the app:

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Run the Streamlit app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Usage

1. **Add Ingredients**: Enter ingredients one by one and build your pantry list
2. **Set Preferences**: Specify dietary restrictions and preferred cuisine type
3. **Generate Recipe**: Click the generate button to create your personalized recipe
4. **Listen & Cook**: Play the voice guide and follow along while cooking
5. **Download**: Save the audio guide for offline use

## Voice Options

Choose from these natural-sounding voices:
- **Nova** (default): Friendly and warm
- **Coral**: Enthusiastic and energetic
- **Echo**: Clear and professional
- **Fable**: British accent
- **Alloy**: Neutral and balanced
- **Ash**: Calm and soothing
- **Onyx**: Deep and authoritative
- **Sage**: Wise and measured
- **Shimmer**: Bright and cheerful

## Project Structure

```
/
├── voice_agent.py    # Backend logic for recipe generation and TTS
├── app.py           # Streamlit frontend
├── requirements.txt # Python dependencies
├── venv/           # Virtual environment (created)
└── README.md       # This file
```

## Troubleshooting

### API Key Issues
- Ensure your OpenAI API key has access to GPT-4 and TTS models
- Check that the key is properly formatted without extra spaces

### Audio Playback
- The generated audio file is saved as `recipe_guide.mp3` in the project directory
- If audio doesn't play in the browser, try downloading and playing locally

### Dependencies
- If you encounter import errors, ensure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4 and TTS access
- macOS, Windows, or Linux
- Internet connection for API calls

## License

This project is provided as-is for educational and personal use. 