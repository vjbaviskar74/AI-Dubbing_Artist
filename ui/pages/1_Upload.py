import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Step 1: Upload Video & Select Dubbing Mode")

mode = st.radio(
    "Select Dubbing Mode:",
    [
        "Mode 1: Blind Mode (Video Only - AI guesses characters from audio)",
        "Mode 2: Studio Mode (Video + Official Script - 100% accurate character names & text proofreading)"
    ]
)

video_file = st.file_uploader("Upload Movie Clip (30s - 2min)", type=["mp4", "mkv", "avi"])

script_file = None
script_text = ""

if "Studio Mode" in mode:
    st.markdown("### 🎬 Studio Mode Script Setup")
    st.info("The uploaded script guarantees 100% accurate character naming and error fixing while keeping Whisper's exact millisecond timestamps!")
    script_file = st.file_uploader("Upload Official English Script (.txt, .srt, .md)", type=["txt", "srt", "md"])
    script_text = st.text_area("Or Paste Script Dialogue Here (e.g., 'BATMAN: I will be back...')", height=120)

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Source Language", ["English", "Hindi"])
with col2:
    target_lang = st.selectbox("Target Language", ["Hindi", "Marathi"])

consent = st.checkbox("I confirm that voice cloning usage is authorized and consensual.")

if st.button("Start Dubbing Job", type="primary"):
    if not video_file:
        st.error("Please upload a video file.")
    elif not consent:
        st.error("Please check the consent box to proceed.")
    elif "Studio Mode" in mode and not script_file and not script_text.strip():
        st.error("In Studio Mode, please upload a script file or paste script text!")
    else:
        with st.spinner("Creating job and uploading media..."):
            files = {"file": (video_file.name, video_file.getvalue(), video_file.type)}
            if script_file:
                files["script_file"] = (script_file.name, script_file.getvalue(), script_file.type)
                
            data = {
                "source_language": source_lang,
                "target_language": target_lang,
                "consent_verified": str(consent).lower(),
                "script_text": script_text.strip() if script_text else ""
            }
            res = requests.post(f"{API_URL}/jobs/", files=files, data=data)
            if res.status_code == 200:
                job_id = res.json()["job_id"]
                st.session_state['job_id'] = job_id
                st.success(f"Job created! ID: {job_id}")
                
                with st.spinner("Running Media Agent (Extract, Separate, Transcribe, Diarize, Studio Align & Proofread)..."):
                    process_res = requests.post(f"{API_URL}/jobs/{job_id}/process-media")
                    if process_res.status_code == 200:
                        st.success("Media processing & Studio Mode alignment complete! Go to Step 2.")
            else:
                st.error("Failed to create job.")
