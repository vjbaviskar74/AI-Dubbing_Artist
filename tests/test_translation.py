def test_translation_exists():
    from app.tools.translation_tools import translate_segments_to_marathi
    res = translate_segments_to_marathi([{"original_text": "Hello"}], {"genre": "Drama"})
    assert "success" in res
    assert "translations" in res
