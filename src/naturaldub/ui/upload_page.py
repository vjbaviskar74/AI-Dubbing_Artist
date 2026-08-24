import streamlit as st
import uuid
import os
from pathlib import Path
from ..config import settings

def render_upload_page():
    st.header("Phase 1: Upload Video")
    
    uploaded_file = st.file_uploader("Upload a video (MP4, MKV, MOV, WebM)", type=["mp4", "mkv", "mov", "webm"])
    
    if uploaded_file is not None:
        if "run_id" not in st.session_state:
            st.session_state.run_id = str(uuid.uuid4())
            
        run_id = st.session_state.run_id
        
        uploads_dir = settings.default.paths.absolute_path(settings.base_dir, "runs_dir") / run_id / "raw"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = uploads_dir / uploaded_file.name
        
        if not video_path.exists():
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
        st.session_state.input_video = str(video_path)
        st.video(str(video_path))
        
        if st.button("Proceed to Analysis"):
            st.session_state.current_phase = "analysis"
            st.rerun()
