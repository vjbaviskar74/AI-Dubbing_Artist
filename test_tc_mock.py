import sys
import types
import warnings

# Mock torchcodec so pyannote never tries to load libtorchcodec_core8.dll!
if 'torchcodec' not in sys.modules:
    mock_tc = types.ModuleType('torchcodec')
    sys.modules['torchcodec'] = mock_tc
if 'torchcodec.decoders' not in sys.modules:
    mock_tcd = types.ModuleType('torchcodec.decoders')
    sys.modules['torchcodec.decoders'] = mock_tcd

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from pyannote.audio import Pipeline
        print("pyannote.audio imported without any torchcodec DLL tracebacks!")
    except Exception as e:
        print("Import error:", e)
