import sys
import types
sys.modules['numba.experimental.jitclass._box'] = types.ModuleType('numba.experimental.jitclass._box')

try:
    import librosa
    print("Librosa imported successfully with mocked _box!")
except Exception as e:
    import traceback
    traceback.print_exc()
