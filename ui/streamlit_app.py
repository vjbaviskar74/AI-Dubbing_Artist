import streamlit as st

st.set_page_config(
    page_title="NATURALDUB-AI",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 NATURALDUB-AI")
st.subheader("Emotion, Humor and Culture Preserving Regional Movie Dubbing System")

st.markdown("""
Welcome to the MVP of **NATURALDUB-AI**. 
This system converts short English/Hindi movie clips into Marathi while attempting to preserve:
- Emotion & Tone
- Humor (Sarcasm, jokes)
- Cultural context
- Background music

**Workflow:**
1. Upload video (30s to 2min)
2. Review extracted transcript
3. Review translated dialogue
4. Adjust genre, humor, and cultural metadata
5. Generate dubbing (Voice & Mix)
6. View final evaluation and download
""")

# Initialize session state for Job ID
if 'job_id' not in st.session_state:
    st.session_state['job_id'] = None
