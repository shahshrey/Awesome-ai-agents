# app.py - Streamlit UI for Cooking Recipe Voice Agent
import streamlit as st
import asyncio
import os
from pathlib import Path
from voice_agent import generate_cooking_guide

st.set_page_config(
    page_title="AI Cooking Recipe Voice Guide", page_icon="🍳", layout="wide"
)


def run_async(func, *args, **kwargs):
    """Handle asyncio in Streamlit."""
    try:
        return asyncio.run(func(*args, **kwargs))
    except RuntimeError:
        # Handle case where event loop is already running
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))


def init_session_state():
    """Initialize session state variables."""
    if "ingredients_list" not in st.session_state:
        st.session_state.ingredients_list = []
    if "generated_recipe" not in st.session_state:
        st.session_state.generated_recipe = None
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None


# Sidebar - API keys & voice picker
with st.sidebar:
    st.title("🔑 Settings")
    openai_key = st.text_input("OpenAI API Key", type="password")
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        st.success("API key saved!")

    st.markdown("---")
    st.markdown("### 🎤 Voice Settings")
    voice = st.selectbox(
        "Select Voice Guide",
        ["nova", "coral", "echo", "fable", "alloy", "ash", "onyx", "sage", "shimmer"],
        index=0,
        help="Choose the voice for your cooking guide",
    )

    st.markdown("---")
    st.markdown("### 📖 About")
    st.info(
        "This AI cooking assistant helps you create delicious recipes "
        "from your available ingredients and provides step-by-step "
        "voice guidance for cooking!"
    )


# Main app
init_session_state()

st.title("🍳 AI Cooking Recipe Voice Guide")
st.markdown(
    "Get personalized recipes based on your ingredients with "
    "voice-guided cooking instructions! Simply add your available "
    "ingredients, customize preferences, and let AI create the "
    "perfect recipe."
)

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🥘 Add Your Ingredients or Recipe name")

    # Ingredient input
    new_ingredient = st.text_input(
        "Enter an ingredient:", placeholder="e.g., chicken breast, tomatoes, pasta..."
    )

    if st.button("Add Ingredient", type="secondary"):
        if new_ingredient and new_ingredient not in st.session_state.ingredients_list:
            st.session_state.ingredients_list.append(new_ingredient.strip())
            st.success(f"Added: {new_ingredient}")
        elif new_ingredient in st.session_state.ingredients_list:
            st.warning("This ingredient is already in your list!")

    # Display current ingredients
    if st.session_state.ingredients_list:
        st.markdown("#### Your Ingredients:")
        for idx, ingredient in enumerate(st.session_state.ingredients_list):
            col_ing, col_del = st.columns([4, 1])
            with col_ing:
                st.write(f"• {ingredient}")
            with col_del:
                if st.button("❌", key=f"del_{idx}"):
                    st.session_state.ingredients_list.pop(idx)
                    st.rerun()

    # Preferences
    st.markdown("### 🍽️ Preferences")
    dietary_preferences = st.text_input(
        "Dietary restrictions/preferences:",
        placeholder="e.g., vegetarian, gluten-free, low-carb...",
    )

    cuisine_type = st.selectbox(
        "Preferred cuisine type:",
        [
            "Any",
            "Italian",
            "Asian",
            "Mexican",
            "Indian",
            "Mediterranean",
            "American",
            "French",
            "Thai",
            "Japanese",
            "Greek",
            "Spanish",
        ],
        index=0,
    )

with col2:
    st.markdown("### 👨‍🍳 Generate Recipe")

    # Check if ready to generate
    if not openai_key:
        msg = "👈 Please enter your OpenAI API key in the sidebar first!"
        st.warning(msg)
    elif not st.session_state.ingredients_list:
        st.info("👈 Add at least one ingredient to get started!")
    else:
        if st.button("🎯 Generate Recipe & Voice Guide", type="primary"):
            with st.spinner("Creating your personalized recipe..."):
                try:
                    # Generate recipe and audio
                    cuisine = cuisine_type.lower() if cuisine_type != "Any" else "any"
                    recipe, audio_path = run_async(
                        generate_cooking_guide,
                        st.session_state.ingredients_list,
                        dietary_preferences,
                        cuisine,
                        voice,
                    )

                    st.session_state.generated_recipe = recipe
                    st.session_state.audio_path = audio_path
                    st.success("Recipe generated successfully!")

                except Exception as e:
                    st.error(f"Error generating recipe: {str(e)}")

# Display generated recipe
if st.session_state.generated_recipe:
    st.markdown("---")
    st.markdown("## 📋 Your Recipe")

    recipe = st.session_state.generated_recipe

    # Recipe header
    col_title, col_info = st.columns([2, 1])
    with col_title:
        st.markdown(f"### {recipe.title}")
    with col_info:
        st.markdown(f"**Servings:** {recipe.servings}")
        st.markdown(f"**Prep Time:** {recipe.prep_time}")
        st.markdown(f"**Cook Time:** {recipe.cook_time}")

    # Ingredients
    st.markdown("#### 🥄 Ingredients")
    cols = st.columns(2)
    for idx, ingredient in enumerate(recipe.ingredients):
        with cols[idx % 2]:
            st.write(f"• {ingredient}")

    # Instructions
    st.markdown("#### 📝 Instructions")
    for i, instruction in enumerate(recipe.instructions, 1):
        st.write(f"**Step {i}:** {instruction}")

    # Tips
    if recipe.tips:
        st.markdown("#### 💡 Pro Tips")
        st.info(recipe.tips)

    # Audio guide
    audio_exists = (
        st.session_state.audio_path and Path(st.session_state.audio_path).exists()
    )
    if audio_exists:
        st.markdown("---")
        st.markdown("### 🎧 Voice-Guided Cooking")
        voice_msg = f"Listen to your personalized cooking guide " f"(Voice: {voice}):"
        st.markdown(voice_msg)

        st.audio(str(st.session_state.audio_path), format="audio/mp3")

        # Download button
        with open(st.session_state.audio_path, "rb") as audio_file:
            file_name = (
                f"cooking_guide_" f"{recipe.title.replace(' ', '_').lower()}.mp3"
            )
            st.download_button(
                label="📥 Download Voice Guide",
                data=audio_file.read(),
                file_name=file_name,
                mime="audio/mp3",
            )

    # Clear/Reset button
    st.markdown("---")
    if st.button("🔄 Start New Recipe"):
        st.session_state.ingredients_list = []
        st.session_state.generated_recipe = None
        st.session_state.audio_path = None
        st.rerun()
