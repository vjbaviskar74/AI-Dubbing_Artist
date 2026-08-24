import traceback
import numpy as np
try:
    import librosa
    y = np.zeros(24000, dtype=np.float32)
    print("running time stretch...")
    librosa.effects.time_stretch(y, rate=1.2)
    print("running pitch shift...")
    librosa.effects.pitch_shift(y, sr=24000, n_steps=2.0)
    print("librosa effects ran successfully!")
except Exception as e:
    print("librosa effects failed:")
    traceback.print_exc()
