import streamlit as st
from typing import Optional, Dict, List, Any
import json
import random
from datetime import datetime
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from openai import OpenAI
import base64



def create_agent() -> Agent:
    return Agent(
        model=OpenAIChat(
            id="gpt-4o",
            api_key=st.session_state.openai_key,
            system_prompt="""You are a specialized agent for designing mythical creatures. 
        Given user-input traits (e.g., 'a dragon that's eco-friendly and loves puzzles'), 
        create a full mythical creature profile. Use tools for folklore research if needed to inspire your design.
        
        You must respond with ONLY a valid JSON object with these exact keys:
        - name: A creative name for the creature
        - backstory: A engaging backstory (200-300 words)
        - abilities: List of 4-6 unique abilities
        - habitat: Description of its natural habitat (100-200 words)
        - game_mechanic: A simple game mechanic involving the creature (e.g., rules for a puzzle or battle system, 100-200 words)
        - visual_description: A detailed prompt for generating an image of the creature (50-100 words)
        - weakness: The creature's main weakness or vulnerability
        - evolution_path: Possible evolution or transformation stages
        - sound_theme: Description of sounds/music associated with the creature
        
        Ensure the design incorporates the user's traits creatively. Make it fun and imaginative.
        
        Respond with ONLY the JSON object, no additional text.""",
        ),
        tools=[DuckDuckGoTools()],
        markdown=False,
    )


def generate_image(api_key: str, prompt: str) -> Optional[str]:
    try:
        client = OpenAI(api_key=api_key)
        prompt_image = f"""
        Game art design, ultra high definition: {prompt}. 
        Kind of like a pokemon, but a game character, not a real animal.
        The creature should be a game character, not a real animal. The creature should be a game character, not a real animal.
        This will be used for a game, so it should be a game character, not a real animal.
        """
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_image,
            size="1024x1024",
            quality="high",
            n=1,
        )

        # Extract image from response
        if hasattr(response, "data") and len(response.data) > 0:
            first_item = response.data[0]

            # Try URL first, then b64_json
            if hasattr(first_item, "url") and first_item.url:
                return first_item.url
            elif hasattr(first_item, "b64_json") and first_item.b64_json:
                # Convert base64 to data URL
                b64_data = first_item.b64_json
                return f"data:image/png;base64,{b64_data}"

        return None
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None


def get_rarity_emoji(rarity: str) -> str:
    emoji_map = {
        "Common": "⚪",
        "Uncommon": "🟢",
        "Rare": "🔵",
        "Epic": "🟣",
        "Legendary": "🟡",
        "Mythic": "🔴",
    }
    return emoji_map.get(rarity, "⚪")


def get_type_emoji(creature_type: str) -> str:
    emoji_map = {
        "Fire": "🔥",
        "Water": "💧",
        "Earth": "🌍",
        "Air": "💨",
        "Shadow": "🌑",
        "Light": "✨",
        "Nature": "🌿",
        "Tech": "⚡",
    }
    return emoji_map.get(creature_type, "❓")


def calculate_stats(traits: str) -> Dict[str, int]:
    # Generate stats based on trait keywords
    base_stats = {
        "HP": random.randint(50, 100),
        "Attack": random.randint(30, 80),
        "Defense": random.randint(20, 70),
        "Speed": random.randint(40, 90),
        "Magic": random.randint(25, 85),
    }

    # Adjust stats based on keywords
    traits_lower = traits.lower()
    if "strong" in traits_lower or "powerful" in traits_lower:
        base_stats["Attack"] += 20
    if "defensive" in traits_lower or "armored" in traits_lower:
        base_stats["Defense"] += 20
    if "fast" in traits_lower or "swift" in traits_lower:
        base_stats["Speed"] += 20
    if "magical" in traits_lower or "mystical" in traits_lower:
        base_stats["Magic"] += 20
    if "ancient" in traits_lower or "legendary" in traits_lower:
        base_stats["HP"] += 30

    # Normalize stats to max 100
    for stat in base_stats:
        base_stats[stat] = min(100, base_stats[stat])

    return base_stats


def determine_rarity(stats: Dict[str, int]) -> str:
    total_stats = sum(stats.values())
    if total_stats >= 400:
        return "Mythic"
    elif total_stats >= 350:
        return "Legendary"
    elif total_stats >= 300:
        return "Epic"
    elif total_stats >= 250:
        return "Rare"
    elif total_stats >= 200:
        return "Uncommon"
    else:
        return "Common"


def determine_types(traits: str, backstory: str) -> List[str]:
    types = []
    combined_text = (traits + " " + backstory).lower()

    type_keywords = {
        "Fire": ["fire", "flame", "burn", "heat", "lava", "ember"],
        "Water": ["water", "ocean", "sea", "aquatic", "rain", "ice"],
        "Earth": ["earth", "stone", "rock", "mountain", "crystal", "gem"],
        "Air": ["air", "wind", "sky", "fly", "wing", "storm"],
        "Shadow": ["shadow", "dark", "night", "void", "stealth", "mysterious"],
        "Light": ["light", "bright", "sun", "holy", "divine", "radiant"],
        "Nature": ["nature", "forest", "plant", "tree", "eco", "green"],
        "Tech": ["tech", "mechanical", "cyber", "digital", "robot", "artificial"],
    }

    for type_name, keywords in type_keywords.items():
        if any(keyword in combined_text for keyword in keywords):
            types.append(type_name)

    # Ensure at least one type
    if not types:
        types.append(random.choice(list(type_keywords.keys())))

    # Limit to 2 types
    return types[:2]

def load_css():
    st.markdown(
        """
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
    }
    
    /* Custom card styling */
    .creature-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .creature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Stat bars */
    .stat-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        position: relative;
        overflow: hidden;
        margin: 5px 0;
    }
    
    .stat-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Rarity colors */
    .rarity-common { color: #808080; }
    .rarity-uncommon { color: #2ecc71; }
    .rarity-rare { color: #3498db; }
    .rarity-epic { color: #9b59b6; }
    .rarity-legendary { color: #f39c12; }
    .rarity-mythic { color: #e74c3c; }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Title styling */
    h1 {
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-size: 3em !important;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 20px;
    }
    
    h3 {
        color: #34495e;
        margin-top: 15px;
    }
    
    /* Type badges */
    .type-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
        font-size: 0.9em;
    }
    
    .type-fire { background: #ff6b6b; color: white; }
    .type-water { background: #4ecdc4; color: white; }
    .type-earth { background: #95e1d3; color: #2c3e50; }
    .type-air { background: #a8e6cf; color: #2c3e50; }
    .type-shadow { background: #4a4a4a; color: white; }
    .type-light { background: #ffd93d; color: #2c3e50; }
    .type-nature { background: #6bcf7f; color: white; }
    .type-tech { background: #6c5ce7; color: white; }
    
    /* Animation for new creatures */
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .new-creature {
        animation: fadeInScale 0.5s ease;
    }
    
    /* Gallery styling */
    .gallery-item {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .gallery-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    /* Battle animation */
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    .battle-hit {
        animation: shake 0.5s ease;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    defaults = {
        "openai_key": "",
        "creature_collection": [],
        "current_creature": None,
        "battle_log": [],
        "selected_creature_1": None,
        "selected_creature_2": None,
        "show_battle": False,
        "creature_templates": {
            "Dragon": "a powerful dragon with ancient wisdom",
            "Phoenix": "a mystical phoenix that rises from ashes",
            "Unicorn": "a magical unicorn with healing powers",
            "Kraken": "a massive sea creature from the depths",
            "Griffin": "a majestic griffin, part eagle part lion",
            "Chimera": "a fearsome chimera with multiple forms",
            "Fairy": "a tiny fairy with nature magic",
            "Golem": "an ancient golem made of living stone",
        },
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def setup_sidebar() -> None:
    with st.sidebar:
        st.title("🔮 Configuration")
        st.session_state.openai_key = st.text_input(
            "OpenAI API Key", value=st.session_state.openai_key, type="password"
        )

        st.divider()

        # Creature type filter for gallery
        st.subheader("🎭 Creature Gallery")
        if st.session_state.creature_collection:
            st.write(f"📚 Total Creatures: {len(st.session_state.creature_collection)}")

            # Rarity breakdown
            rarity_counts = {}
            for creature in st.session_state.creature_collection:
                rarity = creature.get("rarity", "Common")
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

            for rarity, count in rarity_counts.items():
                st.write(f"{get_rarity_emoji(rarity)} {rarity}: {count}")

        st.divider()

        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🎲 Random Creature", use_container_width=True):
            st.session_state.random_gen = True

        if st.button("⚔️ Battle Mode", use_container_width=True):
            st.session_state.show_battle = not st.session_state.show_battle

        if st.session_state.creature_collection:
            if st.button("📥 Export Collection", use_container_width=True):
                export_collection()

        st.divider()

        # Theme selector
        st.subheader("🎨 Theme")
        theme = st.selectbox(
            "Choose Theme",
            ["Ocean Depths", "Mystic Forest", "Crystal Caves", "Sky Realm"],
        )


def display_stat_bar(stat_name: str, value: int, color: str):
    st.markdown(
        f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: bold; color: #2c3e50;">{stat_name}</span>
            <span style="font-weight: bold; color: {color};">{value}</span>
        </div>
        <div class="stat-bar">
            <div class="stat-fill" style="width: {value}%; background: {color};"></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_creature_card(creature: Dict[str, Any], index: Optional[int] = None):
    st.markdown('<div class="creature-card new-creature">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if creature.get("image_url"):
            st.image(creature["image_url"], use_container_width=True)
        else:
            st.info("🖼️ No image available")

        # Display types
        types = creature.get("types", ["Unknown"])
        type_html = ""
        for t in types:
            type_html += f'<span class="type-badge type-{t.lower()}">{get_type_emoji(t)} {t}</span>'
        st.markdown(type_html, unsafe_allow_html=True)

        # Display rarity
        rarity = creature.get("rarity", "Common")
        st.markdown(
            f'<h3 class="rarity-{rarity.lower()}">{get_rarity_emoji(rarity)} {rarity}</h3>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(f"## {creature.get('name', 'Unnamed Creature')}")

        # Stats
        stats = creature.get("stats", {})
        stat_colors = {
            "HP": "#e74c3c",
            "Attack": "#f39c12",
            "Defense": "#3498db",
            "Speed": "#2ecc71",
            "Magic": "#9b59b6",
        }

        for stat, value in stats.items():
            display_stat_bar(stat, value, stat_colors.get(stat, "#95a5a6"))

        # Power Level
        total_stats = sum(stats.values())
        st.metric("⚡ Power Level", total_stats)

    # Abilities, Backstory, etc. in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📖 Story", "⚔️ Abilities", "🏠 Habitat", "🎮 Game", "🎵 Sound"]
    )

    with tab1:
        st.write(creature.get("backstory", "No backstory available."))
        if creature.get("evolution_path"):
            st.subheader("🔄 Evolution Path")
            st.write(creature.get("evolution_path"))

    with tab2:
        abilities = creature.get("abilities", [])
        for i, ability in enumerate(abilities, 1):
            st.write(f"**{i}.** {ability}")
        if creature.get("weakness"):
            st.warning(f"**Weakness:** {creature.get('weakness')}")

    with tab3:
        st.write(creature.get("habitat", "No habitat described."))

    with tab4:
        st.write(creature.get("game_mechanic", "No game mechanic designed."))

    with tab5:
        st.write(creature.get("sound_theme", "No sound theme described."))

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save to Collection", key=f"save_{index}"):
            save_creature(creature)
    with col2:
        if st.button("⚔️ Select for Battle", key=f"battle_{index}"):
            select_for_battle(creature)
    with col3:
        if st.button("📤 Share", key=f"share_{index}"):
            share_creature(creature)

    st.markdown("</div>", unsafe_allow_html=True)


def save_creature(creature: Dict[str, Any]):
    creature["created_at"] = datetime.now().isoformat()
    st.session_state.creature_collection.append(creature)
    st.success(f"✅ {creature['name']} added to your collection!")
    st.balloons()


def select_for_battle(creature: Dict[str, Any]):
    if not st.session_state.selected_creature_1:
        st.session_state.selected_creature_1 = creature
        st.info(f"⚔️ {creature['name']} selected as Fighter 1")
    elif not st.session_state.selected_creature_2:
        st.session_state.selected_creature_2 = creature
        st.info(f"⚔️ {creature['name']} selected as Fighter 2")
        st.session_state.show_battle = True
    else:
        st.warning("Both battle slots are filled! Clear selections first.")


def share_creature(creature: Dict[str, Any]):
    # Create a shareable JSON
    share_data = {
        "name": creature.get("name"),
        "types": creature.get("types"),
        "rarity": creature.get("rarity"),
        "stats": creature.get("stats"),
        "abilities": creature.get("abilities"),
    }
    st.code(json.dumps(share_data, indent=2), language="json")
    st.info("📋 Copy this code to share your creature!")


def battle_simulator():
    st.markdown("## ⚔️ Battle Arena")

    if (
        not st.session_state.selected_creature_1
        or not st.session_state.selected_creature_2
    ):
        st.warning("Select two creatures to battle!")
        return

    c1 = st.session_state.selected_creature_1
    c2 = st.session_state.selected_creature_2

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown(f"### {c1['name']}")
        st.markdown(f"**Power:** {sum(c1['stats'].values())}")
        if c1.get("image_url"):
            st.image(c1["image_url"], use_container_width=True)

    with col2:
        st.markdown("### VS")
        if st.button("⚡ FIGHT!", use_container_width=True):
            simulate_battle(c1, c2)

    with col3:
        st.markdown(f"### {c2['name']}")
        st.markdown(f"**Power:** {sum(c2['stats'].values())}")
        if c2.get("image_url"):
            st.image(c2["image_url"], use_container_width=True)

    # Battle log
    if st.session_state.battle_log:
        st.markdown("### 📜 Battle Log")
        for log in st.session_state.battle_log:
            st.write(log)

    # Clear battle
    if st.button("🔄 Clear Battle"):
        st.session_state.selected_creature_1 = None
        st.session_state.selected_creature_2 = None
        st.session_state.battle_log = []
        st.session_state.show_battle = False


def simulate_battle(c1: Dict, c2: Dict):
    st.session_state.battle_log = []

    # Simple battle calculation
    c1_power = sum(c1["stats"].values())
    c2_power = sum(c2["stats"].values())

    c1_hp = c1["stats"]["HP"] * 10
    c2_hp = c2["stats"]["HP"] * 10

    round_num = 1

    while c1_hp > 0 and c2_hp > 0 and round_num <= 10:
        st.session_state.battle_log.append(f"**Round {round_num}**")

        # C1 attacks
        damage = random.randint(c1["stats"]["Attack"] // 2, c1["stats"]["Attack"])
        c2_hp -= damage
        st.session_state.battle_log.append(f"⚔️ {c1['name']} deals {damage} damage!")

        if c2_hp <= 0:
            break

        # C2 attacks
        damage = random.randint(c2["stats"]["Attack"] // 2, c2["stats"]["Attack"])
        c1_hp -= damage
        st.session_state.battle_log.append(f"⚔️ {c2['name']} deals {damage} damage!")

        round_num += 1

    # Determine winner
    if c1_hp > c2_hp:
        st.session_state.battle_log.append(f"🏆 **{c1['name']} WINS!**")
        st.balloons()
    elif c2_hp > c1_hp:
        st.session_state.battle_log.append(f"🏆 **{c2['name']} WINS!**")
        st.balloons()
    else:
        st.session_state.battle_log.append("🤝 **It's a DRAW!**")


def export_collection():
    if not st.session_state.creature_collection:
        st.warning("No creatures to export!")
        return

    # Create JSON export
    export_data = {
        "collection_name": "My Mythical Creatures",
        "export_date": datetime.now().isoformat(),
        "total_creatures": len(st.session_state.creature_collection),
        "creatures": st.session_state.creature_collection,
    }

    json_str = json.dumps(export_data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="mythical_creatures.json">📥 Download Collection JSON</a>'
    st.markdown(href, unsafe_allow_html=True)


def display_gallery():
    st.markdown("## 🏛️ Creature Gallery")

    if not st.session_state.creature_collection:
        st.info("Your collection is empty. Create some creatures to see them here!")
        return

    # Sort options
    sort_by = st.selectbox("Sort by", ["Newest", "Oldest", "Power Level", "Rarity"])

    creatures = st.session_state.creature_collection.copy()

    if sort_by == "Newest":
        creatures.reverse()
    elif sort_by == "Power Level":
        creatures.sort(key=lambda x: sum(x.get("stats", {}).values()), reverse=True)
    elif sort_by == "Rarity":
        rarity_order = ["Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]
        creatures.sort(key=lambda x: rarity_order.index(x.get("rarity", "Common")))

    # Display in grid
    cols = st.columns(3)
    for i, creature in enumerate(creatures):
        with cols[i % 3]:
            st.markdown('<div class="gallery-item">', unsafe_allow_html=True)
            if creature.get("image_url"):
                st.image(creature["image_url"], use_container_width=True)
            st.markdown(f"**{creature['name']}**")
            st.markdown(
                f"{get_rarity_emoji(creature.get('rarity', 'Common'))} {creature.get('rarity', 'Common')}"
            )
            st.markdown(f"⚡ Power: {sum(creature.get('stats', {}).values())}")
            if st.button("View Details", key=f"view_{i}"):
                st.session_state.current_creature = creature
            st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="🐉 Mythical Creature Designer", layout="wide", page_icon="🐉"
    )

    load_css()
    initialize_session_state()
    setup_sidebar()

    # Main title with animation
    st.markdown(
        """
    <h1 style='text-align: center; background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FECA57);
    background-size: 200% 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradient 3s ease infinite;'>
    🐉 Mythical Creature Designer 🦄
    </h1>
    """,
        unsafe_allow_html=True,
    )

    if not st.session_state.openai_key:
        st.warning("🔑 Please enter your OpenAI API key in the sidebar to begin.")
        return

    agent = create_agent()

    # Show battle mode if enabled
    if st.session_state.show_battle:
        battle_simulator()
        st.divider()

    # Main creation interface
    st.markdown("## 🎨 Create Your Creature")

    # Template selection
    col1, col2 = st.columns([1, 3])
    with col1:
        use_template = st.checkbox("Use Template", value=False)
        template = None
        if use_template:
            template = st.selectbox(
                "Choose Template", list(st.session_state.creature_templates.keys())
            )

    with col2:
        if use_template and template:
            default_text = st.session_state.creature_templates[template]
        else:
            default_text = ""

        user_input = st.text_area(
            "Describe your creature's traits:",
            value=default_text,
            placeholder="Example: a dragon that's eco-friendly and loves puzzles, or a cybernetic phoenix with time manipulation powers",
            height=100,
        )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            preferred_type = st.multiselect(
                "Preferred Types",
                ["Fire", "Water", "Earth", "Air", "Shadow", "Light", "Nature", "Tech"],
            )
        with col2:
            min_rarity = st.selectbox(
                "Minimum Rarity",
                ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"],
            )
        with col3:
            power_boost = st.slider("Power Boost", 0, 50, 0)

    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "✨ Generate Creature ✨", use_container_width=True, type="primary"
        ) or ("random_gen" in st.session_state and st.session_state.random_gen):
            if "random_gen" in st.session_state and st.session_state.random_gen:
                # Generate random traits
                random_traits = [
                    "mysterious and ancient",
                    "playful yet powerful",
                    "guardian of sacred places",
                    "master of illusions",
                    "collector of rare artifacts",
                    "singer of cosmic songs",
                    "weaver of dreams",
                ]
                user_input = f"a {random.choice(list(st.session_state.creature_templates.keys())).lower()} that is {random.choice(random_traits)}"
                st.session_state.random_gen = False

            if user_input:
                with st.spinner("🔮 Summoning your creature..."):
                    response = agent.run(user_input)

                    try:
                        # Parse response
                        if hasattr(response, "content"):
                            content = response.content
                        elif hasattr(response, "message"):
                            content = response.message
                        elif isinstance(response, str):
                            content = response
                        else:
                            content = str(response)

                        # Clean content
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()

                        # Parse JSON
                        profile = json.loads(content)

                        # Add generated stats and metadata
                        profile["stats"] = calculate_stats(user_input)
                        if "power_boost" in locals() and power_boost > 0:
                            for stat in profile["stats"]:
                                profile["stats"][stat] = min(
                                    100, profile["stats"][stat] + power_boost
                                )

                        profile["rarity"] = determine_rarity(profile["stats"])
                        profile["types"] = determine_types(
                            user_input, profile.get("backstory", "")
                        )

                        # Override with preferred types if specified
                        if "preferred_type" in locals() and preferred_type:
                            profile["types"] = preferred_type[:2]

                        # Generate image
                        visual_desc = profile.get("visual_description", "")
                        if visual_desc:
                            with st.spinner("🎨 Creating visual representation..."):
                                image_url = generate_image(
                                    st.session_state.openai_key, visual_desc
                                )
                                if image_url:
                                    profile["image_url"] = image_url

                        # Store current creature
                        st.session_state.current_creature = profile

                        # Display the creature
                        display_creature_card(
                            profile, index=len(st.session_state.creature_collection)
                        )

                    except json.JSONDecodeError as e:
                        st.error("❌ Error parsing creature data. Please try again.")
                        st.error(f"JSON Error: {str(e)}")
                        with st.expander("Debug Info"):
                            st.code(
                                content if "content" in locals() else str(response),
                                language="text",
                            )
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                        with st.expander("Debug Info"):
                            st.code(
                                content if "content" in locals() else str(response),
                                language="text",
                            )

    # Display current creature if exists
    if st.session_state.current_creature and "Generate Creature" not in user_input:
        st.divider()
        st.markdown("## 📍 Current Creature")
        display_creature_card(st.session_state.current_creature, index=-1)

    # Gallery section
    st.divider()
    display_gallery()


if __name__ == "__main__":
    main()
