import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Step 5: Generate Dubbing")

job_id = st.session_state.get('job_id')
if not job_id:
    st.warning("Please upload a video first.")
    st.stop()

st.write("This step will generate the Marathi voice and mix it with the original video's background audio.")

if st.button("Generate Voice & Mix Audio"):
    with st.spinner("Generating Voice (Emotion Agent)..."):
        res_voice = requests.post(f"{API_URL}/jobs/{job_id}/generate-voice")
        if res_voice.status_code == 200:
            st.success("Voice generation complete.")
            
            with st.spinner("Aligning, Mixing, and Lip-syncing (Sync & QA Agent)..."):
                res_sync = requests.post(f"{API_URL}/jobs/{job_id}/sync-mix-export")
                if res_sync.status_code == 200:
                    st.success("Final video exported successfully! Go to Step 6.")
                else:
                    st.error("Failed during mixing/export.")
        else:
            st.error("Failed during voice generation.")
