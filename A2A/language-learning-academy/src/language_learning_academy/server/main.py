import structlog
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from language_learning_academy.agent.executor import (
    LLMLanguageLearningAgentExecutor,
)


SERVER_PORT = 9999
SERVER_HOST = '0.0.0.0'

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

def main():
    vocabulary_skill = AgentSkill(
        id='vocabulary_lesson',
        name='Vocabulary Lessons',
        description='Learn new words and phrases in your target language with categorized vocabulary by difficulty level',
        tags=['vocabulary', 'words', 'phrases', 'language learning'],
        examples=[
            'Teach me Spanish vocabulary for beginners',
            'Show me intermediate French words',
            'I want to learn German vocabulary'
        ],
    )

    grammar_skill = AgentSkill(
        id='grammar_lesson',
        name='Grammar Lessons',
        description='Master grammar rules, verb conjugations, and sentence structures in various languages',
        tags=['grammar', 'conjugation', 'tenses', 'rules'],
        examples=[
            'Explain Spanish present tense conjugation',
            'Show me French past tense rules',
            'Teach me German grammar basics'
        ],
    )

    conversation_skill = AgentSkill(
        id='conversation_practice',
        name='Conversation Practice',
        description='Practice real-world conversations with scenario-based dialogues and translations',
        tags=['conversation', 'dialogue', 'practice', 'speaking'],
        examples=[
            'Practice restaurant conversation in Spanish',
            'Show me a French café dialogue',
            'Help me with directions conversation in Italian'
        ],
    )

    quiz_skill = AgentSkill(
        id='language_quiz',
        name='Interactive Quizzes',
        description='Test your knowledge with customizable quizzes on vocabulary, grammar, and translations',
        tags=['quiz', 'test', 'assessment', 'practice'],
        examples=[
            'Quiz me on Spanish vocabulary',
            'Test my French grammar knowledge',
            'Give me a reverse translation quiz in German'
        ],
    )

    info_skill = AgentSkill(
        id='language_info',
        name='Language Information',
        description='Get information about supported languages, available services, and learning levels',
        tags=['info', 'help', 'languages', 'support'],
        examples=[
            'What languages do you support?',
            'Show me available services',
            'Help me get started'
        ],
    )

    public_agent_card = AgentCard(
        name='Language Learning Academy - LLM Edition',
        description='An intelligent AI-powered language learning assistant using real LLMs (GPT-4o/Gemini) with LangGraph for advanced vocabulary, grammar, conversation practice, and personalized tutoring across multiple languages',
        url=f'http://localhost:{SERVER_PORT}/',
        version='2.0.0',
        default_input_modes=['text'],
        default_output_modes=['text', 'application/json'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[
            vocabulary_skill,
            grammar_skill,
            conversation_skill,
            quiz_skill,
            info_skill
        ],
        supports_authenticated_extended_card=True,
    )

    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Language Learning Academy - Premium LLM Edition',
            'description': 'Advanced AI language tutor powered by GPT-4o/Gemini with LangGraph orchestration, featuring personalized learning paths, cultural context, and intelligent conversation practice for authenticated users',
            'version': '2.0.1',
            'skills': [
                vocabulary_skill,
                grammar_skill,
                conversation_skill,
                quiz_skill,
                info_skill,
                AgentSkill(
                    id='personalized_learning',
                    name='Personalized Learning Path',
                    description='Get customized learning recommendations based on your progress and goals (Premium feature)',
                    tags=['personalized', 'custom', 'progress', 'premium'],
                    examples=[
                        'Create a personalized Spanish learning plan',
                        'Track my French learning progress',
                        'Recommend next lessons based on my level'
                    ],
                ),
            ],
        }
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LLMLanguageLearningAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=extended_agent_card,
    )

    logger = structlog.get_logger()
    logger.info(f"Starting Language Learning Academy server on {SERVER_HOST}:{SERVER_PORT}")

    uvicorn.run(server.build(), host=SERVER_HOST, port=SERVER_PORT)

if __name__ == '__main__':
    main()
