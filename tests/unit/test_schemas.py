import pytest
from naturaldub.schemas.media import MediaMetadata

def test_media_metadata_valid():
    metadata = MediaMetadata(
        filename="test.mp4",
        duration=10.5,
        channels=2,
        sample_rate=48000
    )
    assert metadata.filename == "test.mp4"
    assert metadata.duration == 10.5
    assert metadata.channels == 2
    assert metadata.sample_rate == 48000
