import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.title("NaturalDub AI")
        
        st.header("Configuration")
        
        groq_api_key = st.text_input("GROQ API Key", type="password", value=os.environ.get("GROQ_API_KEY", ""))
        hf_token = st.text_input("Hugging Face Token", type="password", value=os.environ.get("HF_AUTH_TOKEN", ""))
        openrouter_api_key = st.text_input("OpenRouter API Key", type="password", value=os.environ.get("OPENROUTER_API_KEY", ""))
        sarvam_api_key = st.text_input("Sarvam API Key", type="password", value=os.environ.get("SARVAM_API_KEY", ""))
        
        if groq_api_key:
            os.environ["GROQ_API_KEY"] = groq_api_key
        if hf_token:
            os.environ["HF_AUTH_TOKEN"] = hf_token
        if openrouter_api_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        if sarvam_api_key:
            os.environ["SARVAM_API_KEY"] = sarvam_api_key
            
        st.header("Project State")
        if st.button("Reset Run"):
            st.session_state.clear()
            st.rerun()
