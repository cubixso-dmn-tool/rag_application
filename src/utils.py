import re
from typing import List
from nltk.tokenize import sent_tokenize #type:ignore
import nltk #type:ignore
nltk.download('punkt_tab', quiet=True)

def chunk_text_sentence_based(text: str, chunk_size: int = 500, overlap: int = 150) -> List[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        words = re.findall(r"\w+", sentence)
        if current_length + len(words) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(words)
        else:
            chunks.append(" ".join(current_chunk))
            overlap_sentences = []
            if overlap > 0:
                overlap_words = []
                while current_chunk and len(overlap_words) < overlap:
                    last_sentence = current_chunk.pop()
                    overlap_words = re.findall(r"\w+", last_sentence) + overlap_words
                    overlap_sentences.insert(0, last_sentence)
            current_chunk = overlap_sentences + [sentence]
            current_length = sum(len(re.findall(r"\w+", s)) for s in current_chunk)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks