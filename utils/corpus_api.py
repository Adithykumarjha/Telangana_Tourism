# utils/corpus_api.py
import streamlit as st
import requests
from typing import Optional

def _conf():
    c = st.secrets.get("corpus", {})
    return {
        "base_url": c.get("base_url", "https://api.corpus.swecha.org/api/v1").rstrip("/"),
        "send_otp_ep": c.get("send_otp_endpoint", "auth/send-otp"),
        "verify_otp_ep": c.get("verify_otp_endpoint", "auth/verify-otp"),
        "places_ep": c.get("places_endpoint", "collections/places"),
        "feedback_ep": c.get("feedback_endpoint", "collections/feedback"),
        "itineraries_ep": c.get("itineraries_endpoint", "collections/itineraries"),
    }

def send_otp(contact: str) -> dict:
    """
    contact: phone number (string) or email
    returns JSON response from server
    """
    cfg = _conf()
    url = f"{cfg['base_url']}/{cfg['send_otp_ep'].lstrip('/')}"
    payload = {"phone": contact} if "@" not in contact else {"email": contact}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

def verify_otp(contact: str, otp: str) -> dict:
    cfg = _conf()
    url = f"{cfg['base_url']}/{cfg['verify_otp_ep'].lstrip('/')}"
    payload = {"phone": contact, "otp": otp} if "@" not in contact else {"email": contact, "otp": otp}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

def api_get(endpoint: str, token: Optional[str] = None, params: dict = None) -> dict:
    cfg = _conf()
    url = f"{cfg['base_url']}/{endpoint.lstrip('/')}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def api_post(endpoint: str, data: dict, token: Optional[str] = None) -> dict:
    cfg = _conf()
    url = f"{cfg['base_url']}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(url, json=data, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()
