import traceback
try:
    import librosa
    print("librosa imported successfully")
except Exception as e:
    print("librosa failed:")
    traceback.print_exc()

try:
    from kokoro import KPipeline
    print("kokoro imported successfully")
except Exception as e:
    print("kokoro failed:")
    traceback.print_exc()
