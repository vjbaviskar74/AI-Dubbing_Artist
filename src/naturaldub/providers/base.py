class BaseASRProvider:
    def transcribe(self, audio_path: str) -> dict:
        raise NotImplementedError

class BaseDiarizationProvider:
    def diarize(self, audio_path: str) -> dict:
        raise NotImplementedError

class BaseLLMProvider:
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

class BaseTTSProvider:
    def synthesize(self, text: str, speaker_id: str, output_path: str):
        raise NotImplementedError

class BaseVCProvider:
    def convert(self, source_audio: str, reference_audio: str, output_path: str):
        raise NotImplementedError
