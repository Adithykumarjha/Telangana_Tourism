# utils/ai_modules.py
import streamlit as st
import requests

HF_INFERENCE_URL = "https://api-inference.huggingface.co/models"

def _hf_generate(model_name: str, prompt: str):
    key = st.secrets.get("ai", {}).get("hf_api_key", "")
    if not key:
        raise RuntimeError("HF API key missing in secrets.ai.hf_api_key")
    headers = {"Authorization": f"Bearer {key}"}
    payload = {"inputs": prompt}
    r = requests.post(f"{HF_INFERENCE_URL}/{model_name}", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    out = r.json()
    if isinstance(out, list) and out and "generated_text" in out[0]:
        return out[0]["generated_text"]
    return str(out)

def generate_itinerary(city, days, interests, budget, season):
    use_hf = bool(st.secrets.get("ai", {}).get("use_hf_inference", False))
    model = st.secrets.get("ai", {}).get("model_name", "google/flan-t5-small")
    prompt = f"Plan a {days}-day trip from {city} in {season} season with interests: {', '.join(interests) if interests else 'general'}. Budget: {budget}. Provide day-wise schedule."
    if use_hf:
        try:
            return _hf_generate(model, prompt)
        except Exception as e:
            st.warning(f"HuggingFace generation failed: {e}. Using fallback.")
    # fallback simple template
    plan_lines = []
    for d in range(1, days+1):
        plan_lines.append(f"Day {d}: Suggested visits and notes (based on interests: {', '.join(interests) if interests else 'general'})")
    return "\n\n".join(plan_lines)
