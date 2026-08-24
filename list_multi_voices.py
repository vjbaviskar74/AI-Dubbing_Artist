import asyncio
import edge_tts

async def list_multi_voices():
    voices = await edge_tts.list_voices()
    for v in voices:
        if "Multilingual" in v["ShortName"] or "hi-" in v["ShortName"]:
            print(v["ShortName"], "-", v["Gender"])

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(list_multi_voices())
finally:
    loop.close()
