def test_audio_extraction_exists():
    from app.tools.ffmpeg_tools import extract_audio
    assert callable(extract_audio)
