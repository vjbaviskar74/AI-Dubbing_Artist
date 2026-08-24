import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Step 2: Transcript Review")

job_id = st.session_state.get('job_id')
if not job_id:
    st.warning("Please upload a video first.")
    st.stop()

# Fetch job state
res = requests.get(f"{API_URL}/jobs/{job_id}")
if res.status_code == 200:
    state = res.json().get('state', {})
    segments = state.get('segments', [])
    
    st.write("Review and correct the extracted transcript:")
    updated_segments = []
    
    for i, seg in enumerate(segments):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(f"[{seg.get('start', 0)} - {seg.get('end', 0)}]")
        with col2:
            speaker = st.text_input(f"Speaker {i}", value=seg.get('speaker', 'SPEAKER_01'), key=f"spk_{i}")
            text = st.text_area(f"Text {i}", value=seg.get('text', ''), key=f"txt_{i}")
            updated_segments.append({
                "segment_id": seg.get('segment_id', str(i)),
                "text": text,
                "speaker": speaker,
                "start": seg.get('start', 0),
                "end": seg.get('end', 0)
            })
            
    if st.button("Save Corrections & Continue"):
        import json
        requests.post(f"{API_URL}/jobs/{job_id}/transcript", data={"segments": json.dumps(updated_segments)})
        st.success("Transcript saved! You can proceed to Translation Review.")
else:
    st.error("Failed to fetch job data.")
