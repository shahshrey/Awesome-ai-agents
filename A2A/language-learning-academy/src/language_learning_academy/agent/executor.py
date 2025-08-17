import logging
import os

from collections.abc import AsyncIterable
from typing import Any, Literal

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


memory = MemorySaver()

@tool(description="Get vocabulary lesson for language learning")
def get_vocabulary_lesson(
    language: str = 'spanish',
    level: str = 'beginner',
    category: str = 'general',
    count: int = 5
):
    return f"Vocabulary lesson request: {count} {category} words in {language} for {level} level"

@tool(description="Get grammar lesson for language learning")
def get_grammar_lesson(
    language: str = 'spanish',
    topic: str = 'present_tense',
    level: str = 'beginner'
):
    return f"Grammar lesson request: {topic} in {language} for {level} level"

@tool(description="Get conversation practice scenarios")
def get_conversation_practice(
    language: str = 'spanish',
    scenario: str = 'restaurant',
    level: str = 'beginner'
):
    return f"Conversation practice request: {scenario} scenario in {language} for {level} level"

@tool(description="Create language learning quiz")
def create_language_quiz(
    language: str = 'spanish',
    quiz_type: str = 'vocabulary',
    level: str = 'beginner',
    questions: int = 5
):
    return f"Quiz request: {questions} {quiz_type} questions in {language} for {level} level"

@tool(description="Translate text with context")
def translate_with_context(
    text: str,
    source_language: str = 'english',
    target_language: str = 'spanish',
    context: str = 'general'
):
    return f"Translation request: '{text}' from {source_language} to {target_language} in {context} context"

class ResponseFormat(BaseModel):
    status: Literal['input_required', 'completed', 'error'] = 'completed'
    message: str

class LanguageLearningAgent:
    SYSTEM_INSTRUCTION = (
        'You are an expert language learning tutor with deep knowledge of multiple languages and pedagogical methods. '
        'Use the available tools to provide vocabulary lessons, grammar explanations, conversation practice, quizzes, and translations. '
        'Always provide clear, structured responses with practical examples, cultural context, and pronunciation guidance when relevant. '
        'Support these languages: Spanish, French, German, Italian, Portuguese, Japanese, Chinese, Korean. '
        'Adapt your teaching style to beginner, intermediate, or advanced levels. '
        'Format responses with proper markdown for readability. '
        'If users ask about anything other than language learning, politely redirect them to language-related topics.'
    )

    FORMAT_INSTRUCTION = (
        'Set response status to input_required if the user needs to provide more information to complete the request. '
        'Set response status to error if there is an error while processing the request. '
        'Set response status to completed if the request is complete and helpful.'
    )

    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0.7,
        )
        self.tools = [
            get_vocabulary_lesson,
            get_grammar_lesson,
            get_conversation_practice,
            create_language_quiz,
            translate_with_context
        ]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION, ResponseFormat),
        )

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                tool_name = message.tool_calls[0]['name']
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'Preparing {tool_name.replace("_", " ")}...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Creating personalized language lesson...',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == 'input_required':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                'Unable to process your language learning request at the moment. '
                'Please check your LLM API configuration and try again.'
            ),
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

class LLMLanguageLearningAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = LanguageLearningAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.stream(query, task.context_id):
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']

                if not is_task_complete and not require_user_input:
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'],
                            task.context_id,
                            task.id,
                        ),
                    )
                elif require_user_input:
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item['content'],
                            task.context_id,
                            task.id,
                        ),
                        final=True,
                    )
                    break
                else:
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='language_learning_result',
                    )
                    await updater.complete()
                    break

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f'An error occurred while streaming the response: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())
