# backend/app/services/rag.py
"""
Purpose: Implement the Retrieval-Augmented Generation (RAG) system.
Responsibilities:
- Create vector representations for text chunks via Gemini text-embedding-004.
- Compute cosine similarity rankings between questions and document chunks.
- Retrieve the top K most relevant text context chunks.
- Format strict system instructions to guarantee grounding (no hallucinations).
- Persist ChatMessage histories.
"""

import math
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self, api_key, chat_model="gemini-3.1-flash-lite", embedding_model="models/text-embedding-004"):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.embedding_model = embedding_model
            self.chat_model = chat_model
            logger.info(f"RAGEngine initialized successfully with chat model {self.chat_model}.")
        else:
            self.embedding_model = embedding_model
            self.chat_model = chat_model
            logger.warning("RAGEngine: GEMINI_API_KEY is not configured.")

    def generate_embedding(self, text):
        """
        Calls Gemini embedding API to generate a vector representation of text.
        Returns a list of floats.
        """
        if not self.api_key:
            return None
        
        try:
            # Generate embedding
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result.get('embedding', [])
        except Exception as e:
            logger.error(f"Error generating embedding for text with {self.embedding_model}: {e}")
            if self.embedding_model != "models/embedding-001":
                logger.info("Retrying embedding generation with fallback model models/embedding-001...")
                try:
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    return result.get('embedding', [])
                except Exception as ex:
                    logger.error(f"Fallback embedding generation also failed: {ex}")
            return None

    def generate_query_embedding(self, text):
        """
        Generate embedding specifically optimized for search queries.
        """
        if not self.api_key:
            return None
        
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            return result.get('embedding', [])
        except Exception as e:
            logger.error(f"Error generating query embedding with {self.embedding_model}: {e}")
            if self.embedding_model != "models/embedding-001":
                logger.info("Retrying query embedding generation with fallback model models/embedding-001...")
                try:
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_query"
                    )
                    return result.get('embedding', [])
                except Exception as ex:
                    logger.error(f"Fallback query embedding generation also failed: {ex}")
            return None

    @staticmethod
    def _cosine_similarity(v1, v2):
        """
        Computes cosine similarity between two vector lists.
        Pure Python fallback to eliminate compiled library dependencies.
        """
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_v1 = math.sqrt(sum(a * a for a in v1))
        magnitude_v2 = math.sqrt(sum(b * b for b in v2))
        
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0
        
        return dot_product / (magnitude_v1 * magnitude_v2)

    @staticmethod
    def _keyword_similarity(query, text):
        """
        Simple fallback similarity score based on word matching.
        Used if vector embeddings are unavailable.
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        if not query_words:
            return 0.0
        # Compute simple word overlap percentage
        overlap = query_words.intersection(text_words)
        return len(overlap) / len(query_words)

    def retrieve_context(self, query, chunks, top_k=5):
        """
        Ranks chunks by similarity to query and returns the top_k chunks.
        """
        if not chunks:
            return []

        query_emb = self.generate_query_embedding(query)
        ranked_chunks = []

        if query_emb:
            # 1. Vector Search
            for chunk in chunks:
                similarity = 0.0
                if chunk.embedding:
                    similarity = self._cosine_similarity(query_emb, chunk.embedding)
                else:
                    # Fallback to word matching if single chunk is missing embedding
                    similarity = self._keyword_similarity(query, chunk.chunk_text)
                ranked_chunks.append((chunk, similarity))
        else:
            # 2. Text Keyword Fallback Search
            logger.warning("Query embedding generation failed, falling back to word match matching.")
            for chunk in chunks:
                similarity = self._keyword_similarity(query, chunk.chunk_text)
                ranked_chunks.append((chunk, similarity))

        # Sort descending by similarity
        ranked_chunks.sort(key=lambda x: x[1], reverse=True)
        top_results = [chunk for chunk, sim in ranked_chunks[:top_k]]
        
        logger.info(f"RAG retrieved {len(top_results)} chunks. Top similarity: {ranked_chunks[0][1] if ranked_chunks else 0}")
        return top_results

    def query_document(self, query, chunks, chat_history_list=None):
        """
        Answers user query using document chunks context and historical dialogue.
        Guarantees strict grounding.
        """
        if not self.api_key:
            return "Gemini API is not configured. Please supply an API key."

        # 1. Retrieve top context chunks
        relevant_chunks = self.retrieve_context(query, chunks, top_k=5)
        
        # 2. Formulate context text block
        context_blocks = []
        for i, chunk in enumerate(relevant_chunks):
            context_blocks.append(f"[Chunk {chunk.chunk_index}]: {chunk.chunk_text}")
        
        context_str = "\n\n".join(context_blocks)

        # 3. Format chat history
        history_str = ""
        if chat_history_list:
            history_blocks = []
            for msg in chat_history_list[-6:]: # Keep last 6 exchanges to avoid bloating token sizes
                role = "User" if msg.sender == "user" else "Assistant"
                history_blocks.append(f"{role}: {msg.message}")
            history_str = "\n".join(history_blocks)

        # 4. Formulate prompt
        prompt = (
            f"Document Context:\n{context_str}\n\n"
        )
        if history_str:
            prompt += f"Recent Chat History:\n{history_str}\n\n"
            
        prompt += (
            f"User Question: {query}\n\n"
            "Instructions:\n"
            "You are a strict QA assistant. Answer the User Question based ONLY on the provided Document Context. "
            "Do not extrapolate, assume, or pull details from outside. "
            "If the answer cannot be found in the Document Context, you MUST answer with EXACTLY this sentence: "
            "\"The uploaded document does not contain enough information to answer this question.\""
        )

        system_instruction = (
            "You are a document-grounded search assistant. "
            "Your output must be directly sourced from the provided text segments. "
            "If the answer is not present, you must output: 'The uploaded document does not contain enough information to answer this question.'"
        )

        try:
            model = genai.GenerativeModel(
                self.chat_model,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error executing grounded chat query: {e}")
            return f"Error executing query: {str(e)}"
