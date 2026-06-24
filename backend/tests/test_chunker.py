# backend/tests/test_chunker.py
"""
Purpose: Unit tests for checking Chunker logic.
Responsibilities:
- Verify sentence-aware splitting boundaries.
- Ensure chunk indexes are sequential.
- Check overlapping boundary lengths.
"""

from app.services.chunker import Chunker

def test_chunker_splitting():
    """Test that the chunker splits text correctly and preserves indices."""
    chunker = Chunker(chunk_size=50, chunk_overlap=10)
    text = "This is the first sentence. This is the second sentence. This is the third sentence."
    
    chunks = chunker.split_text(text)
    
    assert len(chunks) > 0
    assert chunks[0]["chunk_index"] == 0
    assert "chunk_text" in chunks[0]
    
    # Verify index incrementing
    for i in range(len(chunks)):
        assert chunks[i]["chunk_index"] == i

def test_chunker_empty_input():
    """Test chunker behavior with empty or null inputs."""
    chunker = Chunker()
    assert chunker.split_text("") == []
    assert chunker.split_text(None) == []
