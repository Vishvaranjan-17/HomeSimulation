# Voice-Based Smart Home Simulator - Project Report

> Slide outline. Export to PDF with any Markdown-to-PDF tool, e.g.
> `pandoc docs/report.md -o report.pdf` or VS Code "Markdown PDF".

---

## Slide 1 - Title

**Voice-Based Smart Home Simulator**

A mini Alexa/Google Home assistant built with an AI pipeline.

Author: <your name> | Course: <course> | Date: <date>

---

## Slide 2 - Objective

Build a voice-controlled smart home simulator where a spoken command is:

1. Converted to text (ASR)
2. Understood by AI (intent + slots)
3. Executed on simulated devices
4. Confirmed back through speech (TTS)

---

## Slide 3 - Architecture

```
User Speech
  -> Whisper ASR
  -> Intent Classifier
  -> Slot Extractor
  -> Ambiguity Handler (+ context memory)
  -> Device State Store
  -> Response Generator (TTS)
```

Every stage is a pluggable adapter: a working fallback runs anywhere; real
models plug in without code changes.

---

## Slide 4 - Core Components

| Component | File | Fallback | Real model |
|-----------|------|----------|-----------|
| ASR | `asr.py` | MockASR | Whisper Medium |
| Intent | `intent.py` | rule/keyword | Nemotron Nano |
| Slots | `slots.py` | regex | Nemotron Super |
| Ambiguity | `ambiguity.py` | context + clarify | - |
| State store | `devices.py` | JSON registry | - |
| Response | `response.py` | templates | Mistral Large |
| TTS | `response.py` | MockTTS | gTTS |

---

## Slide 5 - Device Registry

12 simulated devices: lights (bedroom/living/kitchen), ceiling fan, AC, TV,
door lock, curtains, garage door, heater, temperature sensor, motion sensor.

Each device declares supported actions, value range, unit, and initial state.

---

## Slide 6 - Intents & Slot Schema

**Intents:** turn_on, turn_off, set_value, query_state, execute_routine, clarify.

**Slots:** device, value, unit (optional), relative/absolute flag (+ direction).

---

## Slide 7 - Ambiguity & Context

- Single exact device match -> use it.
- No device named -> use most recent device from context (e.g. "turn it off").
- Otherwise -> ask the user to clarify.
- Context expires after a configurable TTL (`CONTEXT_TTL_SECONDS`).

---

## Slide 8 - Routines (Macros)

- **Goodnight** -> lights off, door locked, AC to 24.
- **Good morning** -> bedroom light on, curtains open, door unlocked.
- **Movie time** -> living light off, TV on, curtains closed.

---

## Slide 9 - Indian-accent / Hindi support

Classifier and slot extractor recognise Hinglish/Hindi keywords:
`band karo`, `jalao`, `chalu`, `kya hai`, `set karo`, `badha`, `kam`.

Examples: "bedroom light band karo", "AC ka temperature kya hai".

---

## Slide 10 - Results & Accuracy

- 31 test commands across all categories.
- Intent accuracy reported in `notebook/demo.ipynb`.
- Automated pytest suite verifies intents, slots, state changes, ambiguity,
  context, routines, relative values, and a Hindi case.

---

## Slide 11 - Industry Practices

Confidence thresholds, context expiration, routines as macros, value-range
validation, graceful clarification on unknown/ambiguous input.

---

## Slide 12 - Demo

Live demo via Streamlit UI and the notebook. See `DEMO_SCRIPT.md`.

---

## Slide 13 - Deliverables

Notebook, device registry JSON, test commands, pytest suite, Streamlit UI,
accuracy analysis, README, this report, demo script.

---

## Slide 14 - Future Work

Real Whisper streaming, noise-robust ASR, LLM-based slot filling, multi-device
commands, persistent state, and richer Hindi/regional language coverage.
