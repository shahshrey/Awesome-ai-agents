# 🐉 Mythical Creature Designer

An AI-powered Streamlit application that generates unique mythical creatures based on user descriptions. This application features a beautiful UI, creature battles, collections, and image generation!

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## ✨ Features

### Core Features
- **AI-Powered Generation**: Uses OpenAI GPT-4o to create detailed creature profiles
- **Image Generation**: Generates creature artwork using OpenAI's image generation API (gpt-image-1 model)
- **Research Integration**: Uses DuckDuckGo tools for folklore inspiration

### Enhanced Features
- **🎨 Beautiful UI**: Custom CSS with gradient backgrounds, animated cards, and smooth transitions
- **📊 Stats System**: Each creature has HP, Attack, Defense, Speed, and Magic stats
- **💎 Rarity System**: Creatures are classified from Common to Mythic based on power level
- **🔥 Type System**: 8 different creature types (Fire, Water, Earth, Air, Shadow, Light, Nature, Tech)
- **⚔️ Battle Arena**: Simulate battles between your creatures
- **🏛️ Creature Gallery**: Save and view your creature collection
- **📤 Export/Share**: Export your collection as JSON or share individual creatures
- **🎲 Random Generation**: Quick random creature generation
- **🎭 Templates**: Pre-built templates for common creature types (Dragon, Phoenix, Unicorn, etc.)
- **🔄 Evolution Paths**: Each creature has potential evolution stages
- **🎵 Sound Themes**: Musical/sound associations for each creature
- **💪 Weaknesses**: Strategic weaknesses for game balance
- **🎨 Theme Selection**: Multiple UI themes (Ocean Depths, Mystic Forest, Crystal Caves, Sky Realm)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key with access to GPT-4o and image generation

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agno
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment (optional):
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the app:
```bash
streamlit run app.py
```

## 🎮 How to Use

### Creating Creatures
1. Enter your OpenAI API key in the sidebar
2. Describe your creature's traits in the text area
3. Optionally:
   - Use pre-built templates
   - Set preferred types, minimum rarity, or power boost in Advanced Options
4. Click "✨ Generate Creature ✨"
5. Watch as your creature comes to life with stats, abilities, and artwork!

### Battle Mode
1. Generate or load at least 2 creatures
2. Click "Select for Battle" on each creature you want to fight
3. Toggle "⚔️ Battle Mode" from the sidebar
4. Click "⚡ FIGHT!" to simulate combat
5. View the battle log to see round-by-round combat

### Collection Management
- **Save**: Click "💾 Save to Collection" to keep creatures permanently
- **Gallery**: View all saved creatures in the gallery section
- **Sort**: Sort by newest, oldest, power level, or rarity
- **Export**: Download your entire collection as JSON from the sidebar

### Quick Actions (Sidebar)
- **🎲 Random Creature**: Generate a creature with random traits
- **⚔️ Battle Mode**: Toggle battle interface
- **📥 Export Collection**: Download your creatures as JSON
- **🎨 Theme**: Choose from 4 different UI themes

### Advanced Options
- **Preferred Types**: Select specific elemental types for your creature
- **Minimum Rarity**: Set a minimum rarity threshold  
- **Power Boost**: Add 0-50 bonus stats to your creature

## 🏗️ Architecture

### Dependencies
```
streamlit          # Web UI framework
openai            # GPT-4o and image generation
duckduckgo-search # Web research capabilities  
agno              # AI agent framework
pillow            # Image processing
requests          # HTTP requests
```

### Components
- **Agent System**: Uses the Agno library for AI agent management
- **Models**: OpenAI GPT-4o for text generation, gpt-image-1 for images
- **Tools**: DuckDuckGo integration for folklore research
- **UI**: Streamlit with extensive custom CSS styling

### Data Structure
Each creature contains:
```json
{
  "name": "Creature Name",
  "backstory": "Detailed backstory (200-300 words)",
  "abilities": ["List", "of", "4-6", "unique", "abilities"],
  "habitat": "Natural habitat description (100-200 words)",
  "game_mechanic": "Game interaction rules (100-200 words)",
  "visual_description": "Image generation prompt (50-100 words)",
  "weakness": "Main vulnerability",
  "evolution_path": "Evolution possibilities",
  "sound_theme": "Associated sounds/music",
  "stats": {
    "HP": 80,
    "Attack": 65,
    "Defense": 50,
    "Speed": 70,
    "Magic": 60
  },
  "rarity": "Epic",
  "types": ["Fire", "Shadow"],
  "image_url": "Generated image URL",
  "created_at": "ISO timestamp"
}
```

## 🎨 UI Features

### Custom Styling
- **Gradients**: Beautiful gradient backgrounds and animated titles
- **Animations**: Hover effects, fadeIn animations for new creatures
- **Color Coding**: Rarity-based colors, type-specific badges with emojis
- **Interactive Elements**: Animated stat bars, card hover effects
- **Responsive Design**: Grid layouts that adapt to screen size

### Battle System
- **Visual Combat**: Side-by-side creature display with power comparison
- **Turn-Based Simulation**: Round-by-round combat with damage calculations
- **Battle Log**: Detailed log of all battle events
- **Victory Celebration**: Balloons animation for winners

### Gallery Features
- **Sorting Options**: Multiple ways to organize your collection
- **Quick Stats**: Rarity and power level at a glance
- **Detailed View**: Click to see full creature information
- **Collection Stats**: Total creatures and rarity breakdown in sidebar

## 🔧 Configuration

### Required API Keys
- **OpenAI API Key**: Required for GPT-4o text generation and image creation
  - Enter in the sidebar when running the app
  - Or set in `.env` file as `OPENAI_API_KEY`

### Customization Options
You can modify these in the code:
- **Templates**: Add new creature templates in `creature_templates` dict
- **Type System**: Modify type keywords and colors
- **Stat Calculations**: Adjust how traits influence stats
- **Battle Mechanics**: Change damage calculations and victory conditions
- **UI Themes**: Add new CSS themes and color schemes

## 📝 Tips for Best Results

1. **Detailed Prompts**: Be specific with traits for more unique creatures
   - ✅ "a dragon that's eco-friendly and loves puzzles"
   - ❌ "a dragon"

2. **Template Starting Points**: Use templates as inspiration, then modify
3. **Type Combinations**: Mix 2 complementary types for interesting abilities
4. **Battle Strategy**: Stats matter, but battles include randomness
5. **Collection Diversity**: Save creatures with different strengths for varied battles


## 📄 License

This project is licensed under the MIT License.

