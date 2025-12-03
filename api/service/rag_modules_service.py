from typing import List, Dict, Any, Tuple
from service.gemini_service import gemini_service
from service.pinecone_service import pinecone_service
import logging
import uuid
import re

logger = logging.getLogger(__name__)

class RAGModulesService:
    """
    Implements the core modules of a Modular RAG system, based on advanced
    techniques discussed in contemporary research.
    """
    def __init__(self):
        # Configuration for Small-to-Big chunking
        self.child_chunk_size = 300  # Smaller chunks for better retrieval accuracy
        self.parent_chunk_size = 1000 # Larger parent chunks for better context
        self.chunk_overlap = 100

    async def indexing_module(self, document: Dict[str, Any]) -> bool:
        """
        [Module: Indexing] Implements a "Small-to-Big" chunking and embedding strategy.
        Smaller, more granular chunks are embedded for retrieval, but are linked to
        larger parent chunks that provide more context for the generation model.
        
        Concept from Paper: Chunk Optimization -> Small-to-Big
        """
        try:
            # 1. Chunk the document into parent and child chunks
            parent_chunks, child_chunks = self._chunk_document_small_to_big(
                document["content"], document.get("title", "")
            )
            
            # 2. Generate embeddings for each CHILD chunk
            vectors = []
            failed_embeddings = 0
            
            for i, child_chunk in enumerate(child_chunks):
                logger.info(f"Processing chunk {i+1}/{len(child_chunks)} for embeddings")
                embedding = await gemini_service.get_embedding(child_chunk["content"])
                
                if embedding and len(embedding) > 0:
                    vectors.append({
                        "id": child_chunk["id"],
                        "values": embedding,
                        "metadata": {
                            "content": child_chunk["content"], # The small chunk content
                            "parent_id": child_chunk["parent_id"],
                            "title": document.get("title", ""),
                            "chunk_index": i,
                            "is_fallback": len(embedding) == 768 and all(isinstance(x, float) for x in embedding[:3]),
                            **document.get("metadata", {})
                        }
                    })
                else:
                    failed_embeddings += 1
                    logger.warning(f"Failed to get embedding for chunk {i+1}")
            
            if failed_embeddings > 0:
                logger.warning(f"Failed to generate embeddings for {failed_embeddings}/{len(child_chunks)} chunks")
            
            if not vectors:
                logger.error("No embeddings were generated successfully")
                return False
            
            # 3. Store child vectors and parent chunks
            if vectors:
                # Store child vectors in Pinecone for retrieval
                await pinecone_service.upsert_vectors(vectors)
                
                # Store parent chunks in a separate store (e.g., another Pinecone namespace, a docstore, or cache)
                # For simplicity, we'll assume a method exists to store/retrieve them.
                await pinecone_service.store_parent_chunks(parent_chunks)
                
                logger.info(f"Indexed {len(vectors)} child chunks for document '{document.get('title', 'Unknown')}'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in indexing module: {e}")
            return False

    async def pre_retrieval_module(self, query: str) -> str:
        """
        [Module: Pre-Retrieval] Enhances the query using Hypothetical Document Embeddings (HyDE).
        It generates a hypothetical answer to the query, which is often semantically closer
        to the target document chunks than the query itself.

        Concept from Paper: Query Transformation -> HyDE (Hypothetical Document Embeddings)
        """
        try:
            hyde_prompt = (
                f"Please write a short, hypothetical passage that answers the following question. "
                f"This passage will be used to retrieve relevant documents.\n\nQuestion: {query}"
            )
            hypothetical_answer = await gemini_service.generate_answer(hyde_prompt)
            enhanced_query = f"{query}\n\n{hypothetical_answer}"
            logger.info(f"Generated hypothetical document for query: '{query}'")
            return enhanced_query # The embedding of this is used for retrieval
        except Exception as e:
            logger.error(f"Error in pre-retrieval (HyDE) module: {e}")
            return query  # Fallback to original query

    async def retrieval_module(self, query: str, top_k: int = 10, username: str = None, documents: List[str] = None) -> List[Dict[str, Any]]:
        """
        [Module: Retrieval] Retrieves relevant PARENT chunks using the Small-to-Big strategy.
        1. Embed the (potentially enhanced) query.
        2. Retrieve the top_k CHILD chunks from Pinecone (filtered by username and documents if provided).
        3. Fetch the corresponding PARENT chunks linked to these child chunks.

        Concept from Paper: Small-to-Big Retrieval
        """
        try:
            query_embedding = await gemini_service.get_embedding(query)
            if not query_embedding or len(query_embedding) == 0:
                logger.warning("Failed to get query embedding")
                return []

            # 1. Retrieve the top CHILD chunks (filtered by username and documents)
            child_results = await pinecone_service.query_vectors(query_embedding, top_k, username=username, documents=documents)
            
            if not child_results:
                if username:
                    logger.warning(f"No child chunks retrieved for user '{username}'")
                else:
                    logger.warning("No child chunks retrieved from vector search")
                return []
            
            # 2. Get the unique IDs of the parent chunks
            parent_ids = []
            for res in child_results:
                metadata = res.get('metadata', {})
                if 'parent_id' in metadata:
                    parent_id = metadata['parent_id']
                    if parent_id not in parent_ids:
                        parent_ids.append(parent_id)
            
            if not parent_ids:
                logger.warning("No parent IDs found in child chunk metadata")
                return []

            # 3. Fetch the full PARENT chunks from the document store
            parent_chunks = await pinecone_service.fetch_parent_chunks(parent_ids)
            
            if not parent_chunks:
                logger.warning("No parent chunks found in document store")
                return []
            
            logger.info(f"Retrieved {len(parent_chunks)} parent chunks for user '{username or 'all users'}'")
            return list(parent_chunks.values())
            
        except Exception as e:
            logger.error(f"Error in retrieval module: {e}")
            return []

    async def post_retrieval_module(self, chunks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        [Module: Post-Retrieval] Reranks the retrieved parent chunks using a model-based reranker.
        This provides a more accurate relevance score than vector similarity alone, as it
        evaluates the (query, chunk) pair directly.

        Concept from Paper: Rerank -> Model-base rerank
        """
        try:
            if not chunks:
                return []
            
            # Use Gemini as a cross-encoder to rerank documents
            reranked_chunks = await gemini_service.rerank_documents(query=query, documents=chunks)
            
            # Keep the top 5 most relevant chunks after reranking
            final_chunks = reranked_chunks[:5]
            
            logger.info(f"Reranked {len(chunks)} chunks, keeping top {len(final_chunks)}")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error in post-retrieval (reranking) module: {e}")
            return chunks[:5] # Fallback to original top-k

    async def generation_module(self, query: str, context_chunks: List[Dict[str, Any]], chat_history: List[Dict[str, Any]] = None) -> str:
        """
        [Module: Generation] Generates detailed, comprehensive answers optimized for TTS.
        Uses full chat history and retrieved context for complete, thorough responses.
        NO length limits - responses can be as long as needed to fully answer the question.
        
        Args:
            query: The user's current question
            context_chunks: Retrieved and reranked document chunks
            chat_history: Previous messages in the conversation (optional)
        """
        try:
            # Build context from chunks - include ALL retrieved content
            context_parts = [chunk.get("metadata", {}).get("content", "") for chunk in context_chunks]
            context = "\n\n---\n\n".join(context_parts)
            
            # Build conversation history string - include full history for context
            conversation_context = ""
            if chat_history and len(chat_history) > 0:
                # Include up to last 20 messages for better context understanding
                recent_history = chat_history[-20:]
                history_parts = []
                for msg in recent_history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        history_parts.append(f"User: {content}")
                    else:
                        # Include full assistant responses for complete context
                        history_parts.append(f"Assistant: {content}")
                
                conversation_context = "\n".join(history_parts)
            
            # Build the TTS-optimized prompt that allows LONG, DETAILED responses
            prompt = f"""You are a knowledgeable, thorough assistant. Your responses will be read aloud using text-to-speech.

YOUR PRIMARY GOAL: Provide COMPLETE, DETAILED, and COMPREHENSIVE answers. Do NOT summarize or shorten your response unless the user explicitly asks for a summary.

RESPONSE LENGTH RULES:
1. Give FULL explanations. Do not cut information short.
2. Include ALL relevant details from the provided documents.
3. Use as many paragraphs as needed to fully answer the question.
4. Do NOT limit yourself to brief responses. Thorough answers are preferred.
5. Only summarize if the user specifically requests a summary.

TTS FORMAT RULES (for spoken clarity):
1. Write in clear, complete sentences that flow naturally when spoken.
2. Use plain text paragraphs only. No bullet points, numbered lists, or markdown.
3. Never use symbols like asterisks, hashes, underscores, backticks, or emojis.
4. Spell out abbreviations: "for example" not "e.g.", "that is" not "i.e."
5. Use natural, conversational language as if explaining to someone in person.
6. Separate ideas into distinct paragraphs for better listening comprehension.
7. Use transitional phrases like "Additionally", "Furthermore", "On the other hand" to connect ideas.

CONTENT RULES:
1. Base your answer strictly on the provided document context.
2. Extract and present ALL important information relevant to the question.
3. If asked about something not in the documents, clearly state that.
4. Use the conversation history to understand references like "this", "that", "earlier", "previous".
5. Provide context and background when helpful for understanding.
6. Explain concepts thoroughly rather than giving brief overviews.

{f'CONVERSATION HISTORY (use this to understand context and references):\n{conversation_context}\n\n' if conversation_context else ''}DOCUMENT CONTEXT (base your answer on this information):
{context}

USER QUESTION: {query}

Provide a complete, detailed answer. Do not artificially shorten your response. Include all relevant information from the documents."""
            
            answer = await gemini_service.generate_answer(prompt)
            
            # Clean up any formatting that might have slipped through
            # NOTE: This does NOT truncate or shorten the response
            answer = self._clean_for_tts(answer)
            
            logger.info(f"Generated detailed TTS-friendly answer for query: {query[:50]}... (length: {len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"Error in generation module: {e}")
            return "I apologize, but I encountered an error while generating the answer."
    
    def _clean_for_tts(self, text: str) -> str:
        """
        Clean text to be fully TTS-compatible.
        Removes all formatting and symbols that break text-to-speech.
        """
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove inline code
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```[a-z]*\n?(.+?)\n?```', r'\1', text, flags=re.DOTALL)
        
        # Remove bullet points and convert to sentences
        text = re.sub(r'^\s*[-•●◦▪]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Remove emojis (common Unicode ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Replace common abbreviations
        text = text.replace(' e.g. ', ' for example ')
        text = text.replace(' i.e. ', ' that is ')
        text = text.replace(' etc.', ' and so on.')
        text = text.replace(' vs. ', ' versus ')
        text = text.replace(' vs ', ' versus ')
        
        # Remove excessive whitespace and normalize
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _remove_markdown_formatting(self, text: str) -> str:
        """
        Helper method to remove common Markdown formatting from text.
        """
        # Remove bold formatting (**text** or __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Remove italic formatting (*text* or _text_)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Remove headers (# or ## or ### etc.)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove inline code (`code`)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove code blocks (```code```)
        text = re.sub(r'```[a-z]*\n(.+?)\n```', r'\1', text, flags=re.DOTALL)
        
        return text.strip()

    def _chunk_document_small_to_big(self, content: str, title: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Private helper for the "Small-to-Big" chunking strategy.
        - Parent Chunks: Larger, overlapping segments for context.
        - Child Chunks: Smaller sentences within each parent chunk for retrieval.
        """
        parent_chunks = []
        child_chunks = []
        
        # Create parent chunks
        start = 0
        while start < len(content):
            end = start + self.parent_chunk_size
            parent_content = content[start:end].strip()
            if parent_content:
                parent_id = f"parent_{uuid.uuid4().hex}"
                parent_chunks.append({
                    "id": parent_id,
                    "metadata": {"content": parent_content, "title": title}
                })
                
                # Create child chunks from this parent chunk
                # Using sentence splitting for smaller, more semantic units
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', parent_content)
                for sentence in sentences:
                    if len(sentence.strip()) > 20: # Filter out very short sentences
                        child_chunks.append({
                            "id": f"child_{uuid.uuid4().hex}",
                            "content": sentence.strip(),
                            "parent_id": parent_id
                        })

            start += self.parent_chunk_size - self.chunk_overlap
            
        return parent_chunks, child_chunks


# Singleton instance
rag_modules_service = RAGModulesService()
