import os
from PyPDF2 import PdfReader #type:ignore
from langchain_core.documents import Document #type:ignore
from langchain_community.vectorstores import FAISS #type:ignore
from langchain_openai import AzureOpenAIEmbeddings #type:ignore
from utils import chunk_text_sentence_based
from dotenv import load_dotenv #type:ignore
load_dotenv()
class Ingestor:
    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-12-01-preview"
)
        self.index = None
        self.documents = []

    def ingest_pdf(self, path: str, meta: dict = None):
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            self.documents.append(Document(page_content=text, metadata={**(meta or {}), 'source': path, 'page': i+1}))

    def ingest_txt(self, path: str, chunk_size: int = 500, overlap: int = 150, meta: dict = None):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk_text_sentence_based(text, chunk_size=chunk_size, overlap=overlap)
        for chunk in chunks:
            self.documents.append(Document(page_content=chunk, metadata={**(meta or {}), 'source': path}))

    def build_index(self):
        texts = [d.page_content for d in self.documents]
        metadatas = [d.metadata for d in self.documents]
        self.index = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        return self.index

    def similarity_search(self, query: str, k: int = 5):
        return self.index.similarity_search_with_score(query, k=k)