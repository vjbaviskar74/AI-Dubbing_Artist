def test_evaluation_returns_19_metrics():
    from app.tools.evaluation_tools import evaluate_output
    report = evaluate_output({})
    assert "translation_quality" in report
    assert "overall_score" in report
    assert len(report.keys()) >= 19
