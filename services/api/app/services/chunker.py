
import tiktoken


class DocumentChunker:
    """Service responsible for splitting documents into overlapping token chunks."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Use tiktoken to accurately count tokens for common models (or general approximation for open source)
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str) -> list[dict[str, str | int]]:
        """
        Splits text into chunks of specified token size with overlap.
        Preserves paragraph boundaries where possible.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk_text = ""
        current_chunk_tokens = 0
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph_tokens = self.count_tokens(paragraph)

            # If a single paragraph is larger than chunk size, we need to split it aggressively
            # (In a real app we'd use a RecursiveCharacterTextSplitter for this, but keeping it simple here)
            if paragraph_tokens > self.chunk_size:
                # Flush current chunk if any
                if current_chunk_text:
                    chunks.append(self._finalize_chunk(current_chunk_text, chunk_index))
                    chunk_index += 1
                    current_chunk_text = ""
                    current_chunk_tokens = 0
                
                # Split huge paragraph roughly by sentences or words
                words = paragraph.split(" ")
                temp_text = ""
                for word in words:
                    temp_tokens = self.count_tokens(temp_text + " " + word)
                    if temp_tokens > self.chunk_size:
                        chunks.append(self._finalize_chunk(temp_text, chunk_index))
                        chunk_index += 1
                        # Handle overlap
                        overlap_words = temp_text.split(" ")[-10:] # rough overlap
                        temp_text = " ".join(overlap_words) + " " + word
                    else:
                        temp_text += " " + word if temp_text else word
                
                if temp_text:
                    current_chunk_text = temp_text
                    current_chunk_tokens = self.count_tokens(temp_text)
                continue

            if current_chunk_tokens + paragraph_tokens > self.chunk_size:
                chunks.append(self._finalize_chunk(current_chunk_text, chunk_index))
                chunk_index += 1
                
                # Keep last paragraph for overlap if it's not too big
                overlap_text = current_chunk_text.split("\n\n")[-1]
                if self.count_tokens(overlap_text) > self.chunk_overlap:
                    # just take words
                    overlap_text = " ".join(current_chunk_text.split(" ")[-20:])

                current_chunk_text = overlap_text + "\n\n" + paragraph if overlap_text else paragraph
                current_chunk_tokens = self.count_tokens(current_chunk_text)
            else:
                current_chunk_text += "\n\n" + paragraph if current_chunk_text else paragraph
                current_chunk_tokens += paragraph_tokens

        if current_chunk_text:
            chunks.append(self._finalize_chunk(current_chunk_text, chunk_index))

        return chunks

    def _finalize_chunk(self, text: str, index: int) -> dict[str, str | int]:
        return {
            "chunk_index": index,
            "content": text.strip(),
            "token_count": self.count_tokens(text.strip())
        }
