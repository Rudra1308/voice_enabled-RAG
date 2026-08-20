from app.services.chunker import DocumentChunker


def test_document_chunker():
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    
    text = (
        "Paragraph 1: The quick brown fox jumps over the lazy dog. " * 5 + "\n\n" +
        "Paragraph 2: It was a beautiful day in the neighborhood. " * 5 + "\n\n" +
        "Paragraph 3: To be or not to be, that is the question. " * 5
    )
    
    chunks = chunker.chunk_text(text)
    
    # We expect multiple chunks since 50 tokens is small
    assert len(chunks) > 1
    
    for c in chunks:
        assert c["token_count"] <= 60  # Allow some small buffer due to overlap logic
        assert "chunk_index" in c
        assert "content" in c
        assert len(c["content"]) > 0

    # Ensure all original text is somewhat represented
    full_chunk_text = " ".join([c["content"] for c in chunks])
    assert "Paragraph 1" in full_chunk_text
    assert "Paragraph 3" in full_chunk_text
