import traceback
try:
    import scipy.io
    print("scipy.io imported successfully")
except Exception as e:
    print("scipy.io failed:")
    traceback.print_exc()

try:
    import soundfile
    print("soundfile imported successfully")
except Exception as e:
    print("soundfile failed:")
    traceback.print_exc()
