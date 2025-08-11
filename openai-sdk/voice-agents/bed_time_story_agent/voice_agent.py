#!/usr/bin/env python3

import asyncio
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel

MODEL_NAME = "gpt-4o"
TTS_MODEL = "gpt-4o-mini-tts"
VOICE = "nova"
WORDS_PER_MIN = 150

DEFAULT_DURATION_MINUTES = 5
MIN_DURATION_MINUTES = 2
MAX_DURATION_MINUTES = 15


class StoryTheme(BaseModel):
    main_character: str
    setting: str
    mood: str = "calm and soothing"
    moral_lesson: Optional[str] = None


class StoryOutput(BaseModel):
    title: str
    story: str
    estimated_duration_minutes: float


async def generate_bedtime_story(
    theme: str,
    age_range: str = "4-8 years",
    duration_minutes: int = DEFAULT_DURATION_MINUTES,
    include_moral: bool = True
) -> StoryOutput:
    try:
        client = AsyncOpenAI()
        word_limit = duration_minutes * WORDS_PER_MIN
        
        system_prompt = """You are a gifted children's storyteller specializing in bedtime stories. 
        Your stories are:
        - Age-appropriate and engaging
        - Calm and soothing in tone
        - Free from scary or overstimulating content
        - Rich with gentle imagery and peaceful scenes
        - Designed to help children relax and prepare for sleep
        
        Always include:
        - A relatable main character
        - Simple, clear language
        - Repetitive, rhythmic elements that promote relaxation
        - A peaceful, satisfying ending"""
        
        user_prompt = f"""Create a bedtime story with these specifications:
        - Theme: {theme}
        - Age range: {age_range}
        - Word count: approximately {word_limit} words (for {duration_minutes} minutes of narration)
        - Include a gentle moral lesson: {include_moral}
        
        Format your response as:
        TITLE: [Story Title]
        
        STORY:
        [The complete story text]
        
        Make the story flow naturally for spoken narration, with good pacing and rhythm."""
        
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("No content in response")
        content = content.strip()
        lines = content.split('\n')
        
        title = ""
        story = ""
        in_story = False
        
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("STORY:"):
                in_story = True
            elif in_story:
                story += line + "\n"
        
        story = story.strip()
        estimated_duration = len(story.split()) / WORDS_PER_MIN
        
        return StoryOutput(
            title=title,
            story=story,
            estimated_duration_minutes=round(estimated_duration, 1)
        )
        
    except Exception as e:
        print(f"Error generating story: {str(e)}")
        raise


async def generate_story_audio(
    text: str,
    voice: str = VOICE,
    output_filename: str = "bedtime_story.mp3"
) -> Path:
    try:
        client = AsyncOpenAI()
        
        tts_instructions = """You are narrating a bedtime story for children. 
        Speak in a calm, gentle, and soothing voice. 
        Use a slow, relaxed pace with natural pauses. 
        Add warmth and kindness to your tone.
        Emphasize the peaceful and calming parts of the story.
        Your goal is to help children feel safe, comfortable, and ready for sleep."""
        
        audio_response = await client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=text,
            instructions=tts_instructions,
            response_format="mp3",
            speed=0.9
        )
        
        output_path = Path(__file__).parent / output_filename
        with open(output_path, "wb", encoding=None) as f:
            f.write(audio_response.content)
        
        print(f"Audio saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise


async def create_bedtime_story_with_audio(
    theme: str,
    age_range: str = "4-8 years",
    duration_minutes: int = DEFAULT_DURATION_MINUTES,
    voice: str = VOICE,
    include_moral: bool = True
) -> tuple[StoryOutput, Path]:
    try:
        print(f"Generating {duration_minutes}-minute bedtime story about '{theme}'...")
        story_output = await generate_bedtime_story(
            theme=theme,
            age_range=age_range,
            duration_minutes=duration_minutes,
            include_moral=include_moral
        )
        
        print(f"Creating audio narration with voice '{voice}'...")
        full_text = f"{story_output.title}\n\n{story_output.story}"
        audio_path = await generate_story_audio(
            text=full_text,
            voice=voice,
            output_filename=f"bedtime_story_{theme.lower().replace(' ', '_')}.mp3"
        )
        
        return story_output, audio_path
        
    except Exception as e:
        print(f"Error in story pipeline: {str(e)}")
        raise


def validate_duration(duration: int) -> int:
    return max(MIN_DURATION_MINUTES, min(duration, MAX_DURATION_MINUTES))


def get_age_appropriate_themes(age_range: str) -> list[str]:
    themes_by_age = {
        "2-4 years": [
            "Friendly animals going to sleep",
            "The moon and stars saying goodnight",
            "A cozy teddy bear's adventure",
            "Gentle rain and sleepy flowers"
        ],
        "4-8 years": [
            "A magical dream garden",
            "The sleepy dragon's bedtime",
            "Adventures in cloudland",
            "The nighttime forest friends",
            "A journey on the dream train"
        ],
        "8-12 years": [
            "The guardian of sweet dreams",
            "A peaceful voyage across the starry sea",
            "The library of sleeping stories",
            "The clockmaker who fixed bedtime"
        ]
    }
    return themes_by_age.get(age_range, themes_by_age["4-8 years"])


if __name__ == "__main__":
    async def test_story():
        story, audio = await create_bedtime_story_with_audio(
            theme="A sleepy bunny looking for the softest cloud to sleep on",
            age_range="4-8 years",
            duration_minutes=5,
            voice="nova"
        )
        print(f"\n📖 {story.title}")
        print(f"⏱️  Duration: {story.estimated_duration_minutes} minutes")
        print(f"🎵 Audio saved: {audio}")
        print(f"\n{story.story[:200]}...")
    
    asyncio.run(test_story()) 