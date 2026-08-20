from app.services.nlp import NLPProcessor


def test_nlp_processor():
    text = "The quick brown fox jumps over the lazy dog. It was a beautiful day!"
    result = NLPProcessor.process_text(text)
    
    assert result["language"] == "en"
    assert len(result["sentences"]) == 2
    assert "The quick brown fox jumps over the lazy dog." in result["sentences"]
    assert "It was a beautiful day!" in result["sentences"]
    
    # "quick", "brown", "fox", "jump", "lazy", "dog", "beautiful", "day" should be in tokens
    # stop words like "the", "it", "was", "a" should be removed.
    assert "fox" in result["tokens"]
    assert "jump" in result["tokens"] # lemmatized
    assert "the" not in result["tokens"]
    assert "it" not in result["tokens"]
