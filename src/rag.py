from langchain_openai import AzureChatOpenAI #type:ignore
from dotenv import load_dotenv #type:ignore
load_dotenv()
import io
llm = AzureChatOpenAI(
    model = 'gpt-4o',
    api_version= '2025-01-01-preview',
    temperature=0
)
from typing import List
from ingest import Ingestor

SYSTEM_PROMPT = (
    "You are a helpful business analyst assistant.\n"
    "When given a question and supporting document excerpts, provide a well-written, "
    "conversational answer formatted in **beautiful Markdown**.\n"
    "The answer should be clear, structured, and engaging, written in natural paragraphs.\n"
    "Use Markdown elements such as **bold**, _italics_, headings, and lists only if they "
    "improve readability — but avoid tables.\n"
    "Do NOT include citations, file names, or page numbers.\n"
    "Base your answer only on the provided excerpts. "
    "If the excerpts do not contain enough information, say so clearly "
    "and suggest what additional details would be helpful."
)

def generate_grounded_answer(query: str, docs: List[object]):
    excerpts = []
    for d in docs:
        text = d.page_content
        if len(text) > 800:
            text = text[:800] + "..."
        excerpts.append(text)

    context = "\n---\n".join(excerpts)
    user_instructions = (
        f"### User Question\n{query}\n\n"
        f"### Relevant Excerpts\n{context}\n\n"
        "### Instructions for Your Response\n"
        "Write a **beautifully formatted Markdown answer** based only on the excerpts above. "
        "Make it flow naturally in paragraph form. "
        "If there’s not enough detail to fully answer, explain that and suggest additional data needed."
    )
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_instructions},
    ]
    resp = llm.invoke(messages)
    return resp.content


def answer_question(ingestor: Ingestor, question: str, k: int = 5):
    results = ingestor.similarity_search(question, k=k)
    top_docs = [r[0] for r in results]
    return generate_grounded_answer(question, top_docs)