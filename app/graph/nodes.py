from app.graph.state import DubbingState
from app.agents.media_agent import run_media_agent
from app.agents.translation_agent import run_translation_agent
from app.agents.voice_emotion_agent import run_voice_emotion_agent
from app.agents.sync_qa_agent import run_sync_qa_agent

# Node wrappers for LangGraph

def media_node(state: DubbingState) -> DubbingState:
    return run_media_agent(state)

def translation_node(state: DubbingState) -> DubbingState:
    return run_translation_agent(state)

def voice_node(state: DubbingState) -> DubbingState:
    return run_voice_emotion_agent(state)

def sync_qa_node(state: DubbingState) -> DubbingState:
    return run_sync_qa_agent(state)
