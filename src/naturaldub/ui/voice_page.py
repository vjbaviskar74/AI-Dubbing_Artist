import streamlit as st
from ..agents.voice_mastering import voice_mastering_node

def render_voice_page():
    st.header("Phase 4 & 5: Voice Production & Final Mastering")
    
    if st.button("Run Voice Mastering Agent"):
        with st.spinner("Generating TTS, converting voices, aligning, and mixing..."):
            state = {k: v for k, v in st.session_state.items() if k in [
                "run_id", "input_video", "media_metadata", "original_audio",
                "vocals_audio", "background_audio", "transcript", "diarization",
                "speaker_turns", "speaker_references", "scene_context", 
                "translations", "approved_script"
            ]}
            
            try:
                new_state = voice_mastering_node(state)
                for k, v in new_state.items():
                    st.session_state[k] = v
                st.success("Mastering complete!")
            except Exception as e:
                st.error(f"Error during voice mastering: {e}")
                
    if "output_video" in st.session_state:
        st.subheader("Final Dubbed Video")
        st.video(st.session_state.output_video)
        
        st.subheader("QA Report")
        st.json(st.session_state.qa_report)
