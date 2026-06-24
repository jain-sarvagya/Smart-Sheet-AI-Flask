# backend/app/services/chunker.py
"""
Purpose: Split documents into semantically coherent text chunks.
Responsibilities:
- Support configurable chunk size and overlap character thresholds.
- Attempt to split at sentence boundaries (.!?) to keep context intact.
- Yield list of dictionary records containing index and text block values.
"""

import re
import logging

logger = logging.getLogger(__name__)

class Chunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        """
        Splits text into chunks of roughly self.chunk_size characters,
        with self.chunk_overlap characters of overlap, preserving sentence boundaries
        where possible.
        """
        if not text:
            return []

        # Standardize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split text into sentences using simple regex
        # This matches periods, question marks, and exclamation marks followed by a space.
        sentence_ends = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_ends, text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_idx = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_len = len(sentence)
            
            # If a single sentence exceeds the chunk size, we must force-split it
            if sentence_len > self.chunk_size:
                # If we have accumulated text, save it first
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "chunk_text": chunk_text,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
                    current_chunk = []
                    current_length = 0
                
                # Split long sentence by characters
                start = 0
                while start < sentence_len:
                    end = min(start + self.chunk_size, sentence_len)
                    # Pull character block
                    chunks.append({
                        "chunk_text": sentence[start:end],
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
                    start += (self.chunk_size - self.chunk_overlap)
                continue

            # Check if adding the next sentence exceeds limits
            # Adding +1 for the space character
            if current_length + sentence_len + (1 if current_chunk else 0) > self.chunk_size:
                # Save the current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_text": chunk_text,
                    "chunk_index": chunk_idx
                })
                chunk_idx += 1
                
                # Build overlap logic: backtracking sentences to create overlap
                overlap_text = []
                overlap_len = 0
                # Go backwards from the end of current_chunk to construct overlap
                for prev_sent in reversed(current_chunk):
                    if overlap_len + len(prev_sent) + (1 if overlap_text else 0) <= self.chunk_overlap:
                        overlap_text.insert(0, prev_sent)
                        overlap_len += len(prev_sent) + 1
                    else:
                        break
                
                current_chunk = overlap_text + [sentence]
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk) - 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_len + (1 if len(current_chunk) > 1 else 0)

        # Append last remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "chunk_text": chunk_text,
                "chunk_index": chunk_idx
            })

        logger.info(f"Chunked document text into {len(chunks)} segments (size={self.chunk_size}, overlap={self.chunk_overlap})")
        return chunks
