"""Streamlit UI for the Voice-Based Smart Home Simulator."""
import streamlit as st

from smarthome.pipeline import Pipeline

st.set_page_config(page_title="Voice Smart Home Simulator", page_icon="🏠")
st.title("🏠 Voice-Based Smart Home Simulator")

if "pipeline" not in st.session_state:
    st.session_state.pipeline = Pipeline()
pipeline = st.session_state.pipeline

st.caption("Type a command (voice input plugs into the Whisper adapter).")

st.file_uploader("Optional: upload audio (requires Whisper adapter)", type=["wav", "mp3"])
command = st.text_input("Command", placeholder="e.g. Set AC to 24 degrees")

if st.button("Send") and command:
    result = pipeline.handle(command)
    st.subheader("Recognized text")
    st.write(result.text)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Intent", result.intent, f"conf {result.confidence:.2f}")
    with col2:
        st.metric("Success", "yes" if result.success else "no")
    st.subheader("Slots")
    st.json(result.slots)
    if result.state_changes:
        st.subheader("State changes")
        for c in result.state_changes:
            st.write(f"- {c}")
    st.subheader("Response (TTS)")
    st.success(result.response)

st.subheader("Device states")
st.table(
    [{"device": name, **state} for name, state in pipeline.store.snapshot().items()]
)
