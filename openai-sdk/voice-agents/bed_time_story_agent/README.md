# 🌙 Bedtime Story Voice Agent

An AI-powered bedtime story generator that creates personalized, kid-friendly stories with natural voice narration using OpenAI's SDK.

## ✨ Features

- **Personalized Stories**: Generate unique bedtime stories based on any theme
- **Age-Appropriate Content**: Stories tailored for different age groups (2-4, 4-8, 8-12 years)
- **Natural Voice Narration**: Stories are narrated using OpenAI's text-to-speech with multiple voice options
- **Customizable Duration**: Choose story length from 2-15 minutes
- **Educational Options**: Include gentle life lessons and morals
- **Download Audio**: Save stories as MP3 files for offline listening

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd bed_time_story_agent
```

2. Install dependencies using UV (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
# With UV
uv run streamlit run app.py

# Or with regular Python
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

5. Enter your OpenAI API key in the sidebar

6. Start creating magical bedtime stories!

## 🎯 Usage

1. **Select Age Range**: Choose the appropriate age group for your story
2. **Choose a Theme**: Pick from suggestions or write your own story idea
3. **Set Duration**: Adjust the story length (2-15 minutes)
4. **Select Voice**: Choose from 6 different narrator voices
5. **Generate**: Click "Create My Bedtime Story" and wait for the magic!
6. **Listen & Download**: Play the audio directly or download as MP3

## 🎤 Available Voices

- **Nova**: Friendly & Warm (default)
- **Alloy**: Neutral & Clear
- **Echo**: Smooth & Calm
- **Fable**: Expressive
- **Onyx**: Deep & Authoritative
- **Shimmer**: Gentle & Soothing

## 📝 Story Themes

The agent suggests age-appropriate themes, including:
- Friendly animals and nature stories (2-4 years)
- Magical adventures and dream journeys (4-8 years)
- Fantasy quests and guardian tales (8-12 years)

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

Or enter your API key directly in the Streamlit sidebar.

## 🏗️ Project Structure

```
bed_time_story_agent/
├── voice_agent.py    # Core story generation and TTS logic
├── app.py           # Streamlit web interface
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
