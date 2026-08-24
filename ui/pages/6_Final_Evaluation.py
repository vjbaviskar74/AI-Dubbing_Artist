import streamlit as st
import requests
import json
import os

API_URL = "http://localhost:8000"

st.title("Step 6: Final Evaluation")

job_id = st.session_state.get('job_id')
if not job_id:
    st.warning("Please upload a video first.")
    st.stop()

# Fetch job state
res = requests.get(f"{API_URL}/jobs/{job_id}")
if res.status_code == 200:
    state = res.json().get('state', {})
    
    video_path = state.get('final_video_path')
    report_path = state.get('evaluation_report_path')
    
    if video_path and os.path.exists(video_path):
        st.write("### Final Dubbed Video")
        st.video(video_path)
    else:
        st.warning("Final video not available yet. Please complete Step 5.")
        
    if report_path and os.path.exists(report_path):
        st.write("### Evaluation Metrics")
        with open(report_path, "r") as f:
            report_data = json.load(f)
            st.json(report_data)
            
    st.write("### Artifacts")
    if video_path:
        st.markdown(f"[Download Final Video]({API_URL}/artifacts/{job_id}/download/video)")
    if state.get('mixed_audio_path'):
        st.markdown(f"[Download Mixed Audio]({API_URL}/artifacts/{job_id}/download/audio)")
else:
    st.error("Failed to fetch job data.")
