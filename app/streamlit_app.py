"""Streamlit UI — Voice-Based Smart Home Simulator.

Features:
  • Live browser microphone capture (audio-recorder-streamlit)
  • Text input fallback
  • 3D glassmorphism dark-theme dashboard
  • Per-device glowing status cards
"""
from __future__ import annotations

import streamlit as st

from smarthome.asr import BrowserAudioASR
from smarthome.pipeline import Pipeline

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Home Simulator",
    page_icon="🏠",
    layout="wide",
)

# ── Global CSS — 3D glassmorphism dark theme ──────────────────────────────────
st.markdown("""
<style>
/* ---------- base ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"]  { background: transparent; }

/* ---------- gradient title ---------- */
.hero-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 50%, #ff7b72 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 0 18px rgba(88,166,255,0.45));
    margin-bottom: 0.2rem;
}
.hero-sub {
    text-align: center;
    color: #8b949e;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* ---------- mic section ---------- */
.mic-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}
.mic-label {
    font-size: 0.85rem;
    color: #8b949e;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ---------- glass card ---------- */
.glass-card {
    background: rgba(22, 27, 34, 0.75);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4),
                inset 0 1px 0 rgba(255,255,255,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 1rem;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 40px rgba(0,0,0,0.55),
                inset 0 1px 0 rgba(255,255,255,0.08);
}

/* ---------- device grid ---------- */
.device-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.device-card {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    position: relative;
    overflow: hidden;
}
.device-card:hover {
    transform: translateY(-4px) scale(1.01);
}
.device-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}

/* glow colours per type */
.type-light::before   { background: linear-gradient(90deg,#f9c74f,#f8961e); }
.type-ac::before      { background: linear-gradient(90deg,#48cae4,#0096c7); }
.type-fan::before     { background: linear-gradient(90deg,#80ffdb,#48cae4); }
.type-tv::before      { background: linear-gradient(90deg,#c77dff,#7b2d8b); }
.type-lock::before    { background: linear-gradient(90deg,#f72585,#b5179e); }
.type-curtain::before { background: linear-gradient(90deg,#ffd166,#ef8c8c); }
.type-garage::before  { background: linear-gradient(90deg,#adb5bd,#6c757d); }
.type-heater::before  { background: linear-gradient(90deg,#ff6b6b,#ee9b00); }
.type-sensor::before  { background: linear-gradient(90deg,#52b788,#40916c); }

.device-icon  { font-size: 2rem; margin-bottom: 0.4rem; }
.device-name  { font-size: 0.95rem; font-weight: 600; color: #e6edf3; }
.device-room  { font-size: 0.75rem; color: #8b949e; margin-bottom: 0.5rem; }
.device-value { font-size: 0.85rem; color: #58a6ff; margin-top: 0.3rem; }

.badge-on  {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(63,185,80,0.15);
    color: #3fb950;
    border: 1px solid rgba(63,185,80,0.4);
    box-shadow: 0 0 8px rgba(63,185,80,0.3);
}
.badge-off {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(139,148,158,0.12);
    color: #8b949e;
    border: 1px solid rgba(139,148,158,0.25);
}

/* ---------- response card ---------- */
.response-card {
    background: rgba(22,27,34,0.85);
    border: 1px solid rgba(88,166,255,0.25);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 0 24px rgba(88,166,255,0.12);
    margin-top: 1rem;
}
.response-text {
    font-size: 1.05rem;
    color: #e6edf3;
    margin-bottom: 0.6rem;
}
.intent-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    background: rgba(188,140,255,0.15);
    color: #bc8cff;
    border: 1px solid rgba(188,140,255,0.35);
    margin-right: 0.5rem;
}
.conf-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    background: rgba(88,166,255,0.12);
    color: #58a6ff;
    border: 1px solid rgba(88,166,255,0.3);
}
.success-yes {
    color: #3fb950; font-weight: 700;
}
.success-no {
    color: #f85149; font-weight: 700;
}

/* ---------- section heading ---------- */
.section-heading {
    font-size: 1rem;
    font-weight: 700;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.6rem;
}

/* ---------- Streamlit widget overrides ---------- */
div[data-testid="stTextInput"] input {
    background: rgba(22,27,34,0.9) !important;
    border: 1px solid rgba(88,166,255,0.3) !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
    padding: 0.6rem 1rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
}
button[kind="primary"], .stButton > button {
    background: linear-gradient(135deg,#58a6ff,#bc8cff) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0d1117 !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.8rem !important;
    box-shadow: 0 4px 15px rgba(88,166,255,0.35) !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "pipeline" not in st.session_state:
    st.session_state.pipeline = Pipeline()
if "asr" not in st.session_state:
    st.session_state.asr = BrowserAudioASR(model_size="base")
if "last_result" not in st.session_state:
    st.session_state.last_result = None

pipeline: Pipeline = st.session_state.pipeline
asr: BrowserAudioASR = st.session_state.asr

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🏠 Smart Home Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Control your home with voice or text commands</div>', unsafe_allow_html=True)

# ── Microphone + text input ───────────────────────────────────────────────────
st.markdown('<div class="section-heading">🎙️ Voice Command</div>', unsafe_allow_html=True)

mic_col, gap_col = st.columns([1, 2])

with mic_col:
    # Try to import audio recorder
    try:
        from audio_recorder_streamlit import audio_recorder  # type: ignore
        st.markdown('<div class="mic-wrapper"><div class="mic-label">Hold to record</div></div>',
                    unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="🎙️ Speak",
            recording_color="#58a6ff",
            neutral_color="#bc8cff",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=2.0,
            sample_rate=16000,
        )
        if audio_bytes:
            with st.spinner("Transcribing…"):
                transcribed = asr.transcribe_bytes(audio_bytes)
            if transcribed:
                st.success(f"Heard: **{transcribed}**")
                result = pipeline.handle(transcribed)
                st.session_state.last_result = result
            else:
                st.warning("⚠️ Could not transcribe. Whisper may not be installed — use text input below.")
    except ImportError:
        st.info("📦 Install `audio-recorder-streamlit` to enable live mic capture.")

# Text input fallback
with st.form("cmd_form", clear_on_submit=True):
    text_col, btn_col = st.columns([4, 1])
    with text_col:
        command = st.text_input(
            "Type a command",
            placeholder="e.g. Turn on bedroom light / Set AC to 22 degrees",
            label_visibility="collapsed",
        )
    with btn_col:
        submitted = st.form_submit_button("Send ➤")

if submitted and command:
    result = pipeline.handle(command)
    st.session_state.last_result = result

# ── Result card ───────────────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result
    success_html = (
        '<span class="success-yes">✔ Success</span>'
        if r.success else
        '<span class="success-no">✘ Failed</span>'
    )
    changes_html = ""
    if r.state_changes:
        items = "".join(f"<li>{c}</li>" for c in r.state_changes)
        changes_html = f"<ul style='margin:0.4rem 0 0 1rem;color:#8b949e;font-size:0.85rem'>{items}</ul>"

    st.markdown(f"""
    <div class="response-card">
        <div class="response-text">💬 {r.response}</div>
        <span class="intent-badge">intent: {r.intent}</span>
        <span class="conf-badge">conf: {r.confidence:.0%}</span>
        {success_html}
        {changes_html}
    </div>
    """, unsafe_allow_html=True)

# ── Device dashboard ──────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">📡 Device Dashboard</div>', unsafe_allow_html=True)

ICONS = {
    "light":   "💡",
    "ac":      "❄️",
    "fan":     "🌀",
    "tv":      "📺",
    "lock":    "🔒",
    "curtain": "🪟",
    "garage":  "🚗",
    "heater":  "🔥",
    "sensor":  "🌡️",
}

snapshot = pipeline.store.snapshot()
devices_meta = {d["name"]: d for d in pipeline.store._devices.values()}

cards_html = '<div class="device-grid">'
for dev_name, state in snapshot.items():
    meta = devices_meta.get(dev_name, {})
    dev_type = meta.get("type", "sensor")
    room = meta.get("room", "").title()
    icon = ICONS.get(dev_type, "📡")
    power = state.get("power", None)

    if power is not None:
        badge = (
            '<span class="badge-on">ON</span>'
            if power == "on"
            else '<span class="badge-off">OFF</span>'
        )
    else:
        badge = '<span class="badge-off">READ-ONLY</span>'

    value_html = ""
    if "value" in state:
        unit = meta.get("value", {}).get("unit", "")
        value_html = f'<div class="device-value">⚡ {state["value"]} {unit}</div>'

    cards_html += f"""
    <div class="device-card type-{dev_type}">
        <div class="device-icon">{icon}</div>
        <div class="device-name">{dev_name.title()}</div>
        <div class="device-room">📍 {room}</div>
        {badge}
        {value_html}
    </div>
    """

cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#30363d;font-size:0.75rem;margin-top:3rem;padding-bottom:1rem;">
    Voice Smart Home Simulator · Powered by Whisper ASR + Streamlit
</div>
""", unsafe_allow_html=True)
