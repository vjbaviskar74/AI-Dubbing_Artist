import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Step 3: Translation Review")

job_id = st.session_state.get('job_id')
if not job_id:
    st.warning("Please upload a video first.")
    st.stop()

if st.button("Run Translation Agent"):
    with st.spinner("Translating to Marathi..."):
        res = requests.post(f"{API_URL}/jobs/{job_id}/translate")
        if res.status_code == 200:
            st.success("Translation generated!")
            st.rerun()

# Fetch job state
res = requests.get(f"{API_URL}/jobs/{job_id}")
if res.status_code == 200:
    state = res.json().get('state', {})
    translations = state.get('translations', [])
    
    if translations:
        st.write("Review and edit the Marathi translations:")
        for i, t in enumerate(translations):
            st.markdown(f"**Original:** {t.get('original_text')}")
            translated = st.text_area(f"Translation {i}", value=t.get('translated_text', ''), key=f"tr_{i}")
            
        if st.button("Save Approved Translations"):
            import json
            updated = []
            for i, t in enumerate(translations):
                updated.append({
                    "segment_id": t.get("segment_id", str(i)),
                    "original_text": t.get("original_text", ""),
                    "translated_text": st.session_state[f"tr_{i}"],
                    "adapted_text": st.session_state[f"tr_{i}"]
                })
            requests.post(f"{API_URL}/jobs/{job_id}/translations-update", data={"translations": json.dumps(updated)})
            st.success("Translations saved!")
else:
    st.error("Failed to fetch job data.")
