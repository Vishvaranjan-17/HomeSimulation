# Voice-Based Smart Home Simulator

A voice-controlled smart home simulator. A spoken (or typed) command is converted to text, understood by an intent classifier, slot-filled, disambiguated against a device registry, executed on simulated devices, and confirmed back through a natural-language (TTS-ready) response.

## Architecture

```
User Speech
   -> Whisper ASR (asr.py)
   -> Intent Classifier (intent.py)
   -> Slot Extractor (slots.py)
   -> Ambiguity Handler + Context (ambiguity.py)
   -> Device State Store (devices.py)
   -> Response Generator / TTS (response.py)
```

Routines (routines.py) expand a single command (e.g. `Goodnight`) into multiple device actions. The whole flow is orchestrated by `pipeline.py`.

## Pluggable model design

Every AI component ships with a **working fallback** that runs anywhere (no GPU, no API keys) and a clean **adapter interface** where real models plug in:

| Component | Fallback (default) | Real model adapter |
|-----------|--------------------|--------------------|
| ASR | `MockASR` (text passthrough) | `WhisperASR` (Whisper Medium) |
| Intent | rule/keyword classifier | Nemotron Nano |
| Slots | regex/keyword extractor | Nemotron Super |
| Response | template generator | Mistral Large |
| TTS | `MockTTS` (returns text) | gTTS |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Run the test suite:
```bash
pytest -q
```

Run a quick end-to-end demo from the CLI:
```bash
python -m smarthome.pipeline
```

Launch the Streamlit UI:
```bash
streamlit run app/streamlit_app.py
```

Open the notebook:
```bash
jupyter notebook notebook/demo.ipynb
```

## Grading-tier coverage

- **Minimum (8 devices + 4 intents):** registry ships 12 devices; classifier supports 6 intents.
- **Good (30 commands + routines + ambiguity):** `data/test_commands.json` has 30+ cases; `routines.py` implements macros; `ambiguity.py` resolves/clarifies.
- **Excellent (context memory + relative commands + Hindi):** conversation context with expiration, relative value handling (e.g. `increase AC by 2`), and Hindi/Hinglish commands.

## Deliverables

- Python package (`smarthome/`)
- Device registry JSON (`data/device_registry.json`)
- Test command set (`data/test_commands.json`)
- Notebook demo (`notebook/demo.ipynb`)
- Streamlit UI (`app/streamlit_app.py`)
- Test suite (`tests/`)
- This README
