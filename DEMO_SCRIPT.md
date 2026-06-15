# Demo Script - Voice-Based Smart Home Simulator

Use this to record a 3-5 minute demo video. Each step lists what to say and what
to show on screen.

## 0. Setup (before recording)

```bash
pip install -r requirements.txt
pytest -q                      # show the suite passing
streamlit run app/streamlit_app.py
```

## 1. Intro (20s)

> "This is a Voice-Based Smart Home Simulator - a mini Alexa built from an AI
> pipeline: speech to text, intent, slots, ambiguity handling, device state, and
> a spoken response."

Show the architecture diagram from the README.

## 2. Basic commands (40s)

In the Streamlit UI, type each and show the result + device state table:

- `Turn on bedroom light` -> light turns on.
- `Set AC to 24 degrees` -> AC value updates.
- `What's the AC temperature?` -> spoken query answer.

## 3. Context memory (30s)

- `Turn on the TV`
- `Turn it off`  -> note it resolves "it" to the TV from context.

## 4. Relative command (20s)

- `Set AC to 24 degrees`
- `Increase AC by 2 degrees` -> AC becomes 26 (relative handling).

## 5. Ambiguity (20s)

Reload the app, then:

- `Turn it off` -> assistant asks "Which device did you mean?"

## 6. Routine (20s)

- `Goodnight` -> lights off, door locked, AC to 24 (one command, many actions).

## 7. Hindi / Hinglish (30s)

- `bedroom light band karo` -> turns the light off.
- `AC ka temperature kya hai` -> answers the query.

## 8. Accuracy analysis (20s)

Open `notebook/demo.ipynb`, run the last cell, and show the printed intent
accuracy over the 31-command test set.

## 9. Wrap-up (15s)

> "All components are pluggable - the same code runs with real Whisper and gTTS
> by installing the optional dependencies. Thanks for watching."
