from app.graph.state import DubbingState

# Edges logic (conditional edges can be added here)
# For MVP, we use a linear flow with manual pause points 
# which will be handled by the FastAPI/UI state machine rather than LangGraph pauses.

def should_review_transcript(state: DubbingState) -> str:
    # Always returning 'continue' for automated flow, 
    # but in advanced setup this would return 'human_review' if confidence is low.
    return "continue"
