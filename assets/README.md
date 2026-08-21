# SceneMedic — Fallback Assets

Pre-baked assets so the live demo NEVER hangs on stage. Every hero moment
in the pitch has a fallback file here that the UI serves if the live
generation call is slow, rate-limited, or blocked.

## Required files (pre-render before H55)

| File | How to generate | Used by |
|---|---|---|
| `fallback_ecg.png` | `tools/imagen3.py` — prompt: "photograph of a Philips IntelliVue monitor screen showing narrow-complex tachycardia at 180 bpm, HR 182, BP 88/54, SpO₂ 91%, dim ER lighting" | Prop gallery, ECG panel |
| `fallback_monitor.png` | Imagen 3 — bedside monitor prop for the corrected scene | Prop gallery, monitor panel |
| `fallback_cxr.png` | Imagen 3 — post-ROSC chest X-ray, ETT tip 4 cm above carina | Prop gallery, CXR panel |
| `fallback_icu.wav` | `tools/lyria3.py` mood=`icu_quiet`, 30 s | Audio bench |
| `fallback_read.wav` | `tools/gemini_tts.py` — the 3 corrected lines with 4 voices | Audio bench |

## Pre-render command

```bash
python -m scripts.prebake  # writes all 5 files
```

(Script lives at `scripts/prebake.py` — build it at H50.)

## Ground rule

If the live network call has not returned within **8 seconds**, the UI
must swap to the fallback file silently. Never let a hung tool call
stall the pitch.
