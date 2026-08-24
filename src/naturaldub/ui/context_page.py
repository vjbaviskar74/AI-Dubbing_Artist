import streamlit as st
from ..agents.transcreation_director import transcreation_director_node

def render_context_page():
    st.header("Phase 2 & 3: Context Analysis & Transcreation")
    
    if st.button("Run Transcreation Director"):
        with st.spinner("Analyzing scene context and translating dialogue..."):
            state = {k: v for k, v in st.session_state.items() if k in [
                "run_id", "input_video", "media_metadata", "original_audio",
                "vocals_audio", "background_audio", "transcript", "diarization",
                "speaker_turns", "speaker_references"
            ]}
            
            try:
                new_state = transcreation_director_node(state)
                for k, v in new_state.items():
                    st.session_state[k] = v
                st.success("Transcreation complete!")
            except Exception as e:
                st.error(f"Error during transcreation: {e}")
                
    if "scene_context" in st.session_state:
        st.subheader("Scene Context")
        st.json(st.session_state.scene_context)
        
        if st.button("Proceed to Translation Approval"):
            st.session_state.current_phase = "translation"
            st.rerun()
