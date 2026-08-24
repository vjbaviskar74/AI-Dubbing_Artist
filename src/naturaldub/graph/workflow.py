from langgraph.graph import StateGraph, END
from .state import NaturalDubState
from ..agents.media_intelligence import media_intelligence_node
from ..agents.transcreation_director import transcreation_director_node
from ..agents.voice_mastering import voice_mastering_node

def create_workflow() -> StateGraph:
    workflow = StateGraph(NaturalDubState)
    
    # Add nodes
    workflow.add_node("media_intelligence", media_intelligence_node)
    workflow.add_node("transcreation_director", transcreation_director_node)
    workflow.add_node("voice_mastering", voice_mastering_node)
    
    # In a full UI application, we interrupt before these to get human input.
    # For a direct CLI execution, we can just chain them.
    # We will set up the graph to just execute sequentially, but in the Streamlit UI,
    # we will run the pipeline step-by-step manually instead of calling the whole compiled graph,
    # or use checkpointer for human-in-the-loop.
    
    workflow.set_entry_point("media_intelligence")
    workflow.add_edge("media_intelligence", "transcreation_director")
    workflow.add_edge("transcreation_director", "voice_mastering")
    workflow.add_edge("voice_mastering", END)
    
    return workflow.compile()
