import asyncio
import edge_tts
import os

def test_azure():
    text = "नमस्ते, यह एक परीक्षण आवाज है।"
    voice = "hi-IN-MadhurNeural"
    output_path = "test_azure.mp3"
    
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_generate())
    finally:
        loop.close()
        
    print(f"Generated file size: {os.path.getsize(output_path)} bytes")

test_azure()
