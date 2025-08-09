import os
from dotenv import load_dotenv  # type:ignore
from ingest import Ingestor
from rag import answer_question

load_dotenv()
# Get absolute path to one directory above the current script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def ingest_documents_and_get_answer(knowledge_base_path, user_query):
    ingestor = Ingestor()
    ingestor.ingest_folder(knowledge_base_path)
    ingestor.build_index()
    response = answer_question(ingestor, user_query, k=5)
    print(response)

if __name__ == '__main__':
    query = "What all decision can be inferred from this document"
    knowledge_base_folder = os.path.join(PROJECT_ROOT, "knowledge_base")
    ingest_documents_and_get_answer(knowledge_base_folder, query)