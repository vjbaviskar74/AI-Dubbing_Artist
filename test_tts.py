import traceback
try:
    import gtts
    print("gtts installed successfully")
except Exception as e:
    print("gtts not installed:", e)

try:
    import edge_tts
    print("edge_tts installed successfully")
except Exception as e:
    print("edge_tts not installed:", e)
