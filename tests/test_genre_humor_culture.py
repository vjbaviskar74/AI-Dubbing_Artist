def test_genre_humor_culture():
    from app.tools.genre_tools import detect_or_assign_genre
    from app.tools.humor_tools import detect_humor_type
    
    res = detect_or_assign_genre("funny joke")
    assert "genre" in res
    
    humor = detect_humor_type("funny joke", "Comedy")
    assert humor["humor_present"] is True
