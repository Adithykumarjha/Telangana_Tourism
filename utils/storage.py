# utils/storage.py
import os
import json
import streamlit as st
from . import corpus_api

DATA_DIR = "data"
PLACES_FILE = os.path.join(DATA_DIR, "places.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
ITINERARIES_FILE = os.path.join(DATA_DIR, "itineraries.json")

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def _use_api() -> bool:
    return bool(st.secrets.get("corpus", {}).get("use_api", False))

def load_places(token: str = None):
    if _use_api():
        endpoint = st.secrets["corpus"].get("places_endpoint", "collections/places")
        try:
            return corpus_api.api_get(endpoint, token)
        except Exception as e:
            st.error(f"Failed to load places from API: {e}")
            return []
    else:
        _ensure_dir()
        if not os.path.exists(PLACES_FILE):
            # seed some sample data
            seed = [
                {"id":"charminar","name":"Charminar","district":"Hyderabad","category":"Heritage","season":"Winter","description":"Iconic 16th-century mosque.","lat":17.3616,"lon":78.4747,"image_url":""},
                {"id":"kuntala","name":"Kuntala Waterfalls","district":"Adilabad","category":"Nature","season":"Monsoon","description":"Telangana’s highest waterfall.","lat":19.1876,"lon":78.5385,"image_url":""}
            ]
            with open(PLACES_FILE,"w",encoding="utf-8") as f:
                json.dump(seed,f,indent=2)
        with open(PLACES_FILE,"r",encoding="utf-8") as f:
            return json.load(f)

def save_place(place: dict, token: str = None):
    if _use_api():
        endpoint = st.secrets["corpus"].get("places_endpoint","collections/places")
        return corpus_api.api_post(endpoint, place, token)
    else:
        _ensure_dir()
        arr = load_places()
        arr.append(place)
        with open(PLACES_FILE,"w",encoding="utf-8") as f:
            json.dump(arr,f,indent=2)
        return place

def load_feedback(token: str = None):
    if _use_api():
        endpoint = st.secrets["corpus"].get("feedback_endpoint","collections/feedback")
        try:
            return corpus_api.api_get(endpoint, token)
        except Exception as e:
            st.error(f"Failed to load feedback from API: {e}")
            return []
    else:
        _ensure_dir()
        if not os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE,"w",encoding="utf-8") as f:
                json.dump([],f)
        with open(FEEDBACK_FILE,"r",encoding="utf-8") as f:
            return json.load(f)

def save_feedback(fb: dict, token: str = None):
    if _use_api():
        endpoint = st.secrets["corpus"].get("feedback_endpoint","collections/feedback")
        return corpus_api.api_post(endpoint, fb, token)
    else:
        _ensure_dir()
        arr = load_feedback()
        arr.append(fb)
        with open(FEEDBACK_FILE,"w",encoding="utf-8") as f:
            json.dump(arr,f,indent=2)
        return fb

def save_itinerary(it: dict, token: str = None):
    if _use_api():
        endpoint = st.secrets["corpus"].get("itineraries_endpoint","collections/itineraries")
        return corpus_api.api_post(endpoint, it, token)
    else:
        _ensure_dir()
        arr = []
        if os.path.exists(ITINERARIES_FILE):
            with open(ITINERARIES_FILE,"r",encoding="utf-8") as f:
                arr = json.load(f)
        arr.append(it)
        with open(ITINERARIES_FILE,"w",encoding="utf-8") as f:
            json.dump(arr,f,indent=2)
        return it
