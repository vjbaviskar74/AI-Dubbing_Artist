import asyncio
import edge_tts
import os

async def test_multi():
    text = "नमस्ते, हम इसे सुलझा लेंगे। चिंता मत कीजिए।"
    voices = [
        "hi-IN-MadhurNeural",
        "en-US-BrianMultilingualNeural",
        "en-US-AndrewMultilingualNeural",
        "fr-FR-RemyMultilingualNeural",
        "hi-IN-SwaraNeural",
        "en-US-AvaMultilingualNeural",
        "en-US-EmmaMultilingualNeural",
        "fr-FR-VivienneMultilingualNeural"
    ]
    for v in voices:
        try:
            out = f"test_{v}.mp3"
            comm = edge_tts.Communicate(text, v)
            await comm.save(out)
            print(f"Success for {v}: size={os.path.getsize(out)}")
        except Exception as e:
            print(f"Failed for {v}: {e}")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(test_multi())
finally:
    loop.close()
