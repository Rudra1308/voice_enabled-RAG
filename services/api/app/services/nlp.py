
import spacy

# We need to make sure the english model is installed.
# We will do a try-except to load it, and if it fails, we will instruct how to download it.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    import sys
    print("Downloading spaCy model en_core_web_sm...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class NLPProcessor:
    """Service responsible for cleaning and tokenizing text using spaCy."""

    @staticmethod
    def process_text(text: str) -> dict:
        """
        Runs the full NLP pipeline on a text chunk.
        Returns cleaned text, tokens, and sentence boundaries.
        """
        doc = nlp(text)

        # Sentence segmentation
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        # Tokenization & stop-word removal (lemmatization)
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]

        # Cleaned text (reconstructing without extra whitespace)
        cleaned_text = " ".join([token.text for token in doc if not token.is_space])

        return {
            "language": doc.lang_,
            "sentences": sentences,
            "tokens": tokens,
            "cleaned_text": cleaned_text
        }
