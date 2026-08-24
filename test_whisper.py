import os
import sys
import types

# 1. Force Numba to run in Pure Python mode (disable C-compilation)
os.environ["NUMBA_DISABLE_JIT"] = "1"

# 2. Mock the blocked C-extension so the import doesn't crash
if 'numba.experimental.jitclass._box' not in sys.modules:
    mock_module = types.ModuleType('numba.experimental.jitclass._box')
    class Box:
        pass
    mock_module.Box = Box
    mock_module.box_get_dataptr = lambda x: None
    sys.modules['numba.experimental.jitclass._box'] = mock_module

try:
    import whisper
    print("Whisper imported successfully in Pure Python mode!")
except Exception as e:
    import traceback
    traceback.print_exc()
