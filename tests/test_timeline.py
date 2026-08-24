def test_alignment_exists():
    from app.tools.alignment_tools import align_audio_duration
    assert callable(align_audio_duration)
