import streamlit as st

def render_translation_page():
    st.header("Phase 3b: Translation Review & Approval")
    
    if "translations" not in st.session_state:
        st.warning("No translations found. Run the Transcreation Director first.")
        return
        
    st.write("Review the timing-aware translations below.")
    
    approved_script = []
    
    for i, seg in enumerate(st.session_state.translations):
        st.markdown(f"**Turn {seg['turn_id']}** - Speaker: {seg['speaker_id']} ({seg['target_duration']}s)")
        st.write(f"Source: {seg['source_text']}")
        
        edited_text = st.text_input(f"Translation (Turn {seg['turn_id']})", value=seg['translated_text'], key=f"trans_{i}")
        
        # Keep track of edits
        new_seg = seg.copy()
        new_seg['translated_text'] = edited_text
        new_seg['is_approved'] = True
        approved_script.append(new_seg)
        st.divider()
        
    if st.button("Approve Script & Proceed to Voice Production"):
        st.session_state.approved_script = approved_script
        st.session_state.current_phase = "voice"
        st.rerun()
