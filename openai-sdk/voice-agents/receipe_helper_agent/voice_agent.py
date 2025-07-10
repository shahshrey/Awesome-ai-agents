# voice_agent.py - Simple Pattern for Cooking Recipe Voice Agent
from pathlib import Path
from typing import List, Literal
from openai import AsyncOpenAI
from pydantic import BaseModel

# ── 1. Config ────────────────────────────────────────────────────────────────
MODEL_NAME = "gpt-4o"
TTS_MODEL = "gpt-4o-mini-tts"
VOICE = "nova"  # default, override in UI
WORDS_PER_MIN = 150  # pacing heuristic

VoiceType = Literal[
    "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
]


# ── 2. Pydantic Schemas ──────────────────────────────────────────────────────
class RecipeOutput(BaseModel):
    title: str
    servings: int
    prep_time: str
    cook_time: str
    ingredients: List[str]
    instructions: List[str]
    tips: str


# ── 3. Core Worker ───────────────────────────────────────────────────────────
async def generate_recipe(
    ingredients: List[str], dietary_preferences: str = "", cuisine_type: str = "any"
) -> RecipeOutput:
    """Generate a recipe based on provided ingredients."""
    client = AsyncOpenAI()

    dietary_text = dietary_preferences if dietary_preferences else "None specified"

    prompt = (
        f"You are a professional chef and cooking instructor. "
        f"Create a delicious recipe using these ingredients:\n\n"
        f"Ingredients available: {', '.join(ingredients)}\n"
        f"Dietary preferences: {dietary_text}\n"
        f"Cuisine type: {cuisine_type}\n\n"
        f"Please provide a complete recipe with:\n"
        f"1. Recipe title\n"
        f"2. Number of servings\n"
        f"3. Prep time\n"
        f"4. Cook time\n"
        f"5. Complete ingredient list with measurements\n"
        f"6. Step-by-step instructions\n"
        f"7. Pro tips or variations\n\n"
        f"Format your response as JSON matching this structure:\n"
        f"{{\n"
        f'    "title": "Recipe Name",\n'
        f'    "servings": 4,\n'
        f'    "prep_time": "15 minutes",\n'
        f'    "cook_time": "30 minutes",\n'
        f'    "ingredients": ["1 cup ingredient 1", "2 tbsp ingredient 2"],\n'
        f'    "instructions": ["Step 1...", "Step 2..."],\n'
        f'    "tips": "Pro tip or variation..."\n'
        f"}}"
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional chef who creates "
                    "clear, easy-to-follow recipes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    import json

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in response")
    recipe_data = json.loads(content)
    return RecipeOutput(**recipe_data)


async def create_voice_script(recipe: RecipeOutput) -> str:
    """Convert recipe to a natural voice script for cooking guidance."""
    title_line = (
        f"Welcome to your cooking guide! " f"Today we're making {recipe.title}."
    )

    timing_line = (
        f"This recipe serves {recipe.servings} and takes about "
        f"{recipe.prep_time} to prepare and {recipe.cook_time} to cook."
    )

    script = f"""{title_line}

{timing_line}

Let's start with gathering our ingredients. You'll need:
{', '.join(recipe.ingredients)}.

Now, let's cook together:

"""

    for i, instruction in enumerate(recipe.instructions, 1):
        script += f"Step {i}: {instruction}\n\n"

    if recipe.tips:
        script += f"Here's a pro tip: {recipe.tips}\n\n"

    script += "And there you have it! Your delicious meal is ready. Enjoy!"

    return script


async def tts(text: str, voice: VoiceType = "nova") -> Path:
    """Convert text to speech and save as MP3."""
    client = AsyncOpenAI()
    out_path = Path(__file__).parent / "recipe_guide.mp3"

    instructions = (
        "You are a friendly, encouraging cooking instructor. "
        "Speak clearly and at a moderate pace, with enthusiasm "
        "about the cooking process. Add natural pauses between steps."
    )

    audio_response = await client.audio.speech.create(
        model=TTS_MODEL, voice=voice, input=text, instructions=instructions
    )

    out_path.write_bytes(audio_response.content)
    return out_path


async def generate_cooking_guide(
    ingredients: List[str],
    dietary_preferences: str = "",
    cuisine_type: str = "any",
    voice: VoiceType = "nova",
) -> tuple[RecipeOutput, Path]:
    """Generate complete cooking guide with recipe and voice output."""
    # Generate recipe
    recipe = await generate_recipe(ingredients, dietary_preferences, cuisine_type)

    # Create voice script
    voice_script = await create_voice_script(recipe)

    # Generate audio
    audio_path = await tts(voice_script, voice)

    return recipe, audio_path
