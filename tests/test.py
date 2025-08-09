from src.ingest import Ingestor
from src.rag import answer_question

def test_pipeline():
    ing = Ingestor()
    ing.ingest_txt('tests/fixtures/sample.txt')
    ing.build_index()
    ans = answer_question(ing, 'What is the refund policy?', k=2)
    assert isinstance(ans, str)
    assert len(ans) > 0