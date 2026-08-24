import streamlit as st
import os

from .ui.sidebar import render_sidebar
from .ui.upload_page import render_upload_page
from .ui.analysis_page import render_analysis_page
from .ui.context_page import render_context_page
from .ui.translation_page import render_translation_page
from .ui.voice_page import render_voice_page

st.set_page_config(page_title="NaturalDub AI", layout="wide")

def main():
    if "current_phase" not in st.session_state:
        st.session_state.current_phase = "upload"
        
    render_sidebar()
    
    phase = st.session_state.current_phase
    
    if phase == "upload":
        render_upload_page()
    elif phase == "analysis":
        render_analysis_page()
    elif phase == "context":
        render_context_page()
    elif phase == "translation":
        render_translation_page()
    elif phase == "voice":
        render_voice_page()

if __name__ == "__main__":
    main()
