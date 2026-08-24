import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Step 4: Genre, Humor & Culture")

job_id = st.session_state.get('job_id')
if not job_id:
    st.warning("Please upload a video first.")
    st.stop()

st.write("Adjust the detected metadata for better voice tone and cultural adaptation.")

# Fetch job state
res = requests.get(f"{API_URL}/jobs/{job_id}")
if res.status_code == 200:
    state = res.json().get('state', {})
    
    genre = st.selectbox("Movie Genre", ["Comedy", "Thriller", "Horror", "Action", "Drama", "Romance", "Documentary", "Historical", "Family"], index=0)
    mood = st.text_input("Scene Mood", value=state.get("scene_mood", "neutral"))
    humor = st.selectbox("Humor Type", ["no_humor", "sarcasm", "wordplay", "situational comedy", "irony"])
    
    if st.button("Re-run Cultural Adaptation"):
        with st.spinner("Adapting..."):
            res_trans = requests.post(f"{API_URL}/jobs/{job_id}/translate?genre={genre}")
            if res_trans.status_code == 200:
                st.success("Adaptation complete. Please check the translations again if needed.")
else:
    st.error("Failed to fetch job data.")
