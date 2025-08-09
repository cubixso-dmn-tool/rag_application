import os
from dotenv import load_dotenv  # type:ignore
from ingest import Ingestor
from rag import answer_question

load_dotenv()
# Get absolute path to one directory above the current script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def demo(question):
    ing = Ingestor()

    # Absolute path from one level above
    pdf_path = os.path.join(
        PROJECT_ROOT,
        "knowledge_base",
        "2024 USAA ANALYSIS case study.pdf"
    )

    ing.ingest_pdf(pdf_path, meta={'type': 'policy'})
    # txt_path = os.path.join(PROJECT_ROOT, "data", "notes.txt")
    # ing.ingest_txt(txt_path)

    ing.build_index()
    answer = answer_question(ing, question, k=5)
    print(answer)

if __name__ == '__main__':
    question = "What all decision can be inferred from this document"
    demo(question)
