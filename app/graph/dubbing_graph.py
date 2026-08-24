from langgraph.graph import StateGraph, START, END
from app.graph.state import DubbingState
from app.graph.nodes import media_node, translation_node, voice_node, sync_qa_node

def build_dubbing_graph():
    builder = StateGraph(DubbingState)
    
    # Add nodes
    builder.add_node("MediaUnderstanding", media_node)
    builder.add_node("TranslationContext", translation_node)
    builder.add_node("VoiceEmotion", voice_node)
    builder.add_node("SyncQA", sync_qa_node)
    
    # Add edges
    builder.add_edge(START, "MediaUnderstanding")
    builder.add_edge("MediaUnderstanding", "TranslationContext")
    builder.add_edge("TranslationContext", "VoiceEmotion")
    builder.add_edge("VoiceEmotion", "SyncQA")
    builder.add_edge("SyncQA", END)
    
    return builder.compile()

# Global graph instance
graph = build_dubbing_graph()
