from ai_observability.app.observability.hallucination import compute_hallucination_score


def test_reference_vs_heuristic_scores():
    heuristic = compute_hallucination_score("This is definitely true with no doubts")
    reference = compute_hallucination_score("Cats are mammals", reference_text="Cats are mammals with fur")
    assert heuristic["score"] > 0
    assert reference["score"] < 1
