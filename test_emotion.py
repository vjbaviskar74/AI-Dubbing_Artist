import torch
import torch.nn as nn
from transformers import Wav2Vec2Model
from huggingface_hub import hf_hub_download

repo_id = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
weights_path = hf_hub_download(repo_id=repo_id, filename="pytorch_model.bin")
state = torch.load(weights_path, map_location="cpu")
model = Wav2Vec2Model.from_pretrained(repo_id)
msg = model.load_state_dict(state, strict=False)
print("MISSING KEYS:", msg.missing_keys)
print("UNEXPECTED KEYS:", msg.unexpected_keys)
