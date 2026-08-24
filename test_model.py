import torch
import torch.nn as nn
from transformers import Wav2Vec2Model

class AgeGenderModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.wav2vec2 = Wav2Vec2Model.from_pretrained('audeering/wav2vec2-large-robust-24-ft-age-gender')
        self.age = nn.ModuleDict({'dense': nn.Linear(1024, 1024), 'out_proj': nn.Linear(1024, 1)})
        self.gender = nn.ModuleDict({'dense': nn.Linear(1024, 1024), 'out_proj': nn.Linear(1024, 3)})

model = AgeGenderModel()
state = torch.load('C:\\\\Users\\\\VEDANT\\\\.cache\\\\huggingface\\\\hub\\\\models--audeering--wav2vec2-large-robust-24-ft-age-gender\\\\snapshots\\\\2e430ab28549f99f3bd20c5e7514a60f64be87cf\\\\pytorch_model.bin', map_location='cpu')
msg = model.load_state_dict(state, strict=False)
print("MISSING KEYS:", msg.missing_keys)
print("UNEXPECTED KEYS:", msg.unexpected_keys)
