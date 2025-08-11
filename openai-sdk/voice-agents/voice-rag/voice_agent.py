import os
import uuid
import tempfile
from typing import List, Dict, Literal
from datetime import datetime

from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from fastembed import TextEmbedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel

# ── 1. Config ────────────────────────────────────────────────────────────────
COLLECTION_NAME = "tech_docs_collection"
OPENAI_MODEL = "gpt-4o"
TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "nova"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Voice options
VoiceType = Literal[
    "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
]


# ── 2. Pydantic Schemas ──────────────────────────────────────────────────────
class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, str]


class QueryResponse(BaseModel):
    text_response: str
    audio_path: str
    sources: List[str]
    status: str


# ── 3. RAG Components ────────────────────────────────────────────────────────
class TechDocsRAG:
    def __init__(self, qdrant_url: str, qdrant_api_key: str):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.embedding_model = TextEmbedding()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            # Get embedding dimensions
            test_embedding = list(self.embedding_model.embed(["test"]))[0]
            embedding_dim = len(test_embedding)
            
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=embedding_dim,
                    distance=Distance.COSINE
                ),
            )
            print(f"Created collection: {COLLECTION_NAME}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise Exception(f"Failed to create collection: {str(e)}")

    def process_pdf(self, file_path: str, file_name: str) -> List[DocumentChunk]:
        """Process PDF file and return chunks with metadata"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add metadata to each document
            timestamp = datetime.now().isoformat()
            for doc in documents:
                doc.metadata.update({
                    "source_type": "pdf",
                    "file_name": file_name,
                    "timestamp": timestamp,
                    "page_number": str(doc.metadata.get("page", 0))
                })
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            return [
                DocumentChunk(
                    content=chunk.page_content,
                    metadata={k: str(v) for k, v in chunk.metadata.items()}
                )
                for chunk in chunks
            ]
        except Exception as e:
            raise Exception(f"Error processing PDF {file_name}: {str(e)}")

    def store_documents(self, chunks: List[DocumentChunk]):
        """Store document chunks in vector database"""
        try:
            points = []
            for chunk in chunks:
                # Generate embedding
                embedding = list(self.embedding_model.embed([chunk.content]))[0]
                
                # Create point
                point = models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "content": chunk.content,
                        **chunk.metadata
                    }
                )
                points.append(point)
            
            # Upsert to collection
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"Stored {len(points)} document chunks")
        except Exception as e:
            raise Exception(f"Error storing documents: {str(e)}")

    async def search_documents(self, query: str) -> List[Dict]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = list(self.embedding_model.embed([query]))[0]
            
            # Search in vector database
            search_response = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_embedding.tolist(),
                limit=TOP_K_RESULTS,
                with_payload=True,
            )
            
            results = (
                search_response.points 
                if hasattr(search_response, "points") 
                else []
            )
            
            if not results:
                raise Exception(
                    "No relevant documents found in the knowledge base"
                )
            
            return [
                {
                    "content": result.payload.get("content", ""),
                    "source": result.payload.get("file_name", "Unknown Source"),
                    "page": (lambda v: int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) else 0)(
                        result.payload.get("page_number", 0)
                    ),
                    "score": result.score if hasattr(result, "score") else 0.0
                }
                for result in results
                if result.payload
            ]
        except Exception as e:
            raise Exception(f"Error searching documents: {str(e)}")

    async def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """Generate answer using OpenAI with retrieved context"""
        try:
            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                source_info = f"Source {i}: {doc['source']}"
                if doc['page']:
                    source_info += f" (Page {doc['page']})"
                context_parts.append(f"{source_info}\n{doc['content']}")
            
            context = "\n\n".join(context_parts)
            
            # Create prompt for technical documentation
            system_prompt = """You are a technical documentation assistant. Your role is to:
1. Provide clear, accurate explanations of technical concepts
2. Include relevant code examples when applicable
3. Explain complex topics in an accessible way
4. Structure responses for spoken delivery (natural flow, no bullet points)
5. Reference the source documents when relevant
6. Keep responses conversational but informative"""
            
            user_prompt = f"""Based on the following technical documentation:

{context}

Question: {query}

Please provide a comprehensive answer that would be helpful when spoken aloud. Include practical examples and explain technical concepts clearly."""
            
            # Generate response using OpenAI
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")

    async def generate_audio(self, text: str, voice: VoiceType = DEFAULT_VOICE) -> str:
        """Generate audio from text using OpenAI TTS"""
        try:
            client = AsyncOpenAI()
            
            # Generate audio
            audio_response = await client.audio.speech.create(
                model=TTS_MODEL,
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Save to temporary file
            audio_path = os.path.join(
                tempfile.gettempdir(),
                f"tech_docs_response_{uuid.uuid4()}.mp3"
            )
            
            with open(audio_path, "wb") as f:
                f.write(audio_response.content)
            
            return audio_path
        except Exception as e:
            raise Exception(f"Error generating audio: {str(e)}")

    async def answer_query(self, query: str, voice: VoiceType = DEFAULT_VOICE) -> QueryResponse:
        """Complete RAG pipeline: search, generate answer, create audio"""
        try:
            # Search for relevant documents
            context_docs = await self.search_documents(query)
            
            # Generate text answer
            text_response = await self.generate_answer(query, context_docs)
            
            # Generate audio
            audio_path = await self.generate_audio(text_response, voice)
            
            # Extract sources
            sources = list(set([doc["source"] for doc in context_docs]))
            
            return QueryResponse(
                text_response=text_response,
                audio_path=audio_path,
                sources=sources,
                status="success"
            )
        except Exception as e:
            return QueryResponse(
                text_response="",
                audio_path="",
                sources=[],
                status=f"error: {str(e)}"
            )


# ── 4. Helper Functions ──────────────────────────────────────────────────────
def validate_environment():
    """Validate required environment variables"""
    required_vars = ["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")


def create_rag_agent(qdrant_url: str, qdrant_api_key: str) -> TechDocsRAG:
    """Create and return a configured RAG agent"""
    try:
        return TechDocsRAG(qdrant_url, qdrant_api_key)
    except Exception as e:
        raise Exception(f"Failed to create RAG agent: {str(e)}") 



