import pytest

from app.services.embedding import EmbeddingEngine


# Note: this will download the model the first time it runs, which takes a moment.
@pytest.fixture(scope="module")
def engine():
    return EmbeddingEngine.get_instance()

def test_embed_text(engine):
    text = "Machine learning is a field of study in artificial intelligence."
    vector = engine.embed_text(text)
    
    assert isinstance(vector, list)
    assert len(vector) == engine.vector_dim
    assert isinstance(vector[0], float)

def test_embed_batch(engine):
    texts = [
        "Deep learning leverages neural networks.",
        "Natural language processing processes text."
    ]
    vectors = engine.embed_batch(texts)
    
    assert len(vectors) == 2
    assert len(vectors[0]) == engine.vector_dim
    assert len(vectors[1]) == engine.vector_dim
