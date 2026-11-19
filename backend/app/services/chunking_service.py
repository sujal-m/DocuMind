from typing import List, Dict, Any
import re
from backend.app.core.config import settings

class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        # Default ~500 words/tokens, ~1500 chars
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _split_text_recursively(self, text: str, max_chars: int, overlap_chars: int) -> List[str]:
        """
        Splits text hierarchically using semantic delimiters:
        Paragraphs (\n\n) -> Sentences (\n, . ) -> Words ( ) -> Characters.
        """
        if len(text) <= max_chars:
            return [text.strip()] if text.strip() else []

        separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
        
        def split_with_separators(t: str, sep_list: List[str]) -> List[str]:
            if not sep_list:
                # Last resort: slice by character
                chunks = []
                for i in range(0, len(t), max_chars - overlap_chars):
                    c = t[i:i + max_chars].strip()
                    if c:
                        chunks.append(c)
                return chunks

            sep = sep_list[0]
            parts = t.split(sep)
            chunks = []
            current_chunk = ""

            for part in parts:
                candidate = f"{current_chunk}{sep}{part}" if current_chunk else part
                if len(candidate) <= max_chars:
                    current_chunk = candidate
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # If this single part itself exceeds max_chars, recurse on it with next separator
                    if len(part) > max_chars:
                        sub_chunks = split_with_separators(part, sep_list[1:])
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = part

            if current_chunk:
                chunks.append(current_chunk.strip())

            return chunks

        raw_chunks = split_with_separators(text, separators)
        
        # Merge or apply overlap
        final_chunks = []
        for i, chunk in enumerate(raw_chunks):
            if not chunk:
                continue
            final_chunks.append(chunk)

        return final_chunks

    def chunk_pages(
        self,
        pages_data: List[Dict[str, Any]],
        document_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunks page-indexed text while preserving page number and sequential chunk index.
        Input: [{'page_number': 1, 'text': '...'}, ...]
        Output: [{'document_id': str, 'chunk_index': int, 'page_number': int, 'content': str, 'token_count': int}]
        """
        # Convert rough token size to char approximation (1 token ~= 4 chars)
        max_chars = self.chunk_size * 4
        overlap_chars = self.chunk_overlap * 4

        all_chunks = []
        global_chunk_index = 0

        for page in pages_data:
            page_num = page.get("page_number", 1)
            raw_text = page.get("text", "").strip()
            if not raw_text:
                continue

            page_chunks = self._split_text_recursively(raw_text, max_chars, overlap_chars)
            for c_text in page_chunks:
                # Estimate token count (simple whitespace split + punctuation approx)
                words = re.findall(r'\S+', c_text)
                token_count = max(1, len(words))

                all_chunks.append({
                    "document_id": document_id,
                    "chunk_index": global_chunk_index,
                    "page_number": page_num,
                    "content": c_text,
                    "token_count": token_count
                })
                global_chunk_index += 1

        return all_chunks

