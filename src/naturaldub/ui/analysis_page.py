import streamlit as st
from ..agents.media_intelligence import media_intelligence_node

def render_analysis_page():
    st.header("Phase 1b: Media Intelligence & Analysis")
    
    if st.button("Run Media Intelligence"):
        with st.spinner("Analyzing media (Extraction -> Separation -> ASR -> Diarization)..."):
            state = {
                "run_id": st.session_state.run_id,
                "input_video": st.session_state.input_video,
            }
            try:
                new_state = media_intelligence_node(state)
                # Update session state with results
                for k, v in new_state.items():
                    st.session_state[k] = v
                st.success("Media Intelligence complete!")
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                
    if "media_metadata" in st.session_state:
        st.json(st.session_state.media_metadata)
        
    if "speaker_turns" in st.session_state:
        st.subheader("Extracted Speaker Turns")
        st.dataframe(st.session_state.speaker_turns)
        
        if st.button("Proceed to Scene Context"):
            st.session_state.current_phase = "context"
            st.rerun()
