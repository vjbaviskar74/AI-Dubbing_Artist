import asyncio
import edge_tts

async def list_hindi_voices():
    voices = await edge_tts.list_voices()
    for v in voices:
        if "hi-IN" in v["ShortName"] or "mr-IN" in v["ShortName"]:
            print(v["ShortName"], "-", v["Gender"])

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(list_hindi_voices())
finally:
    loop.close()
