# app.py
import streamlit as st
from utils import corpus_api, storage, ai_modules
from PIL import Image
import base64
import io
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title=st.secrets.get("app_name","Telangana Tourist Guide"), layout="wide")
st.title(st.secrets.get("app_name","Telangana Tourist Guide"))

# session state for auth
if "auth" not in st.session_state:
    st.session_state.auth = {"token": st.secrets.get("corpus",{}).get("access_token","") or None, "user": None, "contact": None}

# Sidebar auth / OTP
st.sidebar.header("Authentication")
if not st.session_state.auth.get("token"):
    st.sidebar.write("Sign in with registered phone or email (OTP)")
    with st.sidebar.form("send_otp"):
        contact = st.text_input("Phone or Email")
        send = st.form_submit_button("Send OTP")
        if send:
            try:
                resp = corpus_api.send_otp(contact)
                st.session_state.auth["contact"] = contact
                st.sidebar.success("OTP sent — check your SMS/email.")
            except Exception as e:
                st.sidebar.error(f"Send OTP failed: {e}")

    with st.sidebar.form("verify_otp"):
        otp = st.text_input("Enter OTP")
        verify = st.form_submit_button("Verify & Login")
        if verify:
            try:
                resp = corpus_api.verify_otp(st.session_state.auth.get("contact"), otp)
                # Expect access_token in response; stores into session_state
                token = resp.get("access_token") or resp.get("token") or resp.get("token_value")
                if token:
                    st.session_state.auth["token"] = token
                    st.session_state.auth["user"] = resp
                    st.sidebar.success("Logged in.")
                else:
                    st.sidebar.error("Login response did not contain access_token.")
            except Exception as e:
                st.sidebar.error(f"Verify failed: {e}")
else:
    st.sidebar.success("Signed in")
    if st.sidebar.button("Sign out"):
        st.session_state.auth = {"token": None, "user": None, "contact": None}

token = st.session_state.auth.get("token")

# main menu
menu = ["Explore Places", "Add Place", "Plan My Trip", "Image Finder", "Feedback", "Map"]
choice = st.sidebar.selectbox("Menu", menu)

# Explore Places
if choice == "Explore Places":
    st.header("Explore Places")
    places = storage.load_places(token)
    # normalize response form: handle dict wrappers
    if isinstance(places, dict):
        # try common places: "data", "items", or list inside
        if "data" in places and isinstance(places["data"], list):
            places = places["data"]
        elif "items" in places and isinstance(places["items"], list):
            places = places["items"]
        elif "results" in places and isinstance(places["results"], list):
            places = places["results"]
        else:
            # unknown wrapper, attempt to convert to list
            try:
                places = list(places)
            except Exception:
                places = []
    if not places:
        st.info("No places available.")
    else:
        # display as cards in 3 columns
        cols = st.columns(3)
        for i, p in enumerate(places):
            col = cols[i % 3]
            with col:
                if p.get("image_url"):
                    st.image(p.get("image_url"), use_column_width=True)
                st.subheader(p.get("name","Unnamed"))
                st.caption(f"{p.get('district','')} • {p.get('category','')}")
                st.write(p.get("description",""))
                if st.button("More Info", key=f"info_{i}"):
                    st.json(p)
                if st.button("Add to Trip", key=f"add_{i}"):
                    st.success(f"Added {p.get('name')} to your trip (client-side placeholder)")

# Add Place
elif choice == "Add Place":
    st.header("Add Place")
    with st.form("add_place"):
        name = st.text_input("Name")
        district = st.text_input("District")
        category = st.selectbox("Category", ["Heritage","Nature","Religious","Adventure","Wildlife","Other"])
        season = st.selectbox("Best Season", ["Summer","Monsoon","Winter","All"])
        description = st.text_area("Description")
        lat = st.text_input("Latitude")
        lon = st.text_input("Longitude")
        image_file = st.file_uploader("Image (optional)", type=["png","jpg","jpeg"])
        submit = st.form_submit_button("Save")
        if submit:
            place = {
                "name": name,
                "district": district,
                "category": category,
                "season": season,
                "description": description,
                "lat": float(lat) if lat else None,
                "lon": float(lon) if lon else None
            }
            if image_file:
                b = image_file.read()
                b64 = "data:" + image_file.type + ";base64," + base64.b64encode(b).decode()
                place["image_url"] = b64
            res = storage.save_place(place, token)
            st.success("Place saved.")
            st.write(res)

# Plan My Trip
elif choice == "Plan My Trip":
    st.header("Plan My Trip")
    with st.form("plan"):
        start = st.selectbox("Starting city", ["Hyderabad","Warangal","Nizamabad"])
        days = st.slider("Days",1,7,3)
        interests = st.multiselect("Interests", ["Heritage","Nature","Adventure","Religious"])
        budget = st.selectbox("Budget", ["Low","Medium","High"])
        submit = st.form_submit_button("Generate")
        if submit:
            plan_text = ai_modules.generate_itinerary(start, days, interests, budget, "Winter")
            st.markdown("### Suggested Itinerary")
            st.write(plan_text)
            if st.button("Save Itinerary"):
                it = {"start":start,"days":days,"interests":interests,"budget":budget,"plan":plan_text}
                storage.save_itinerary(it, token)
                st.success("Itinerary saved.")

# Image Finder
elif choice == "Image Finder":
    st.header("Image-based place finder")
    uploaded = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Uploaded")
        # Try embedding model (heavy) via ai_modules
        try:
            model = ai_modules  # we will use functions inside
            embed_model = ai_modules.get_image_embedding_model() if hasattr(ai_modules, "get_image_embedding_model") else None
        except Exception:
            embed_model = None
        if embed_model:
            st.info("Computing similarity (this may take time)...")
            emb = embed_model.encode(img, convert_to_tensor=True)
            places = storage.load_places(token)
            if isinstance(places, dict):
                places = places.get("data") or places.get("items") or []
            texts = [( (p.get("name","")+" "+p.get("description","")), p) for p in (places or [])]
            corpus_embs = [ embed_model.encode(t[0], convert_to_tensor=True) for t in texts ]
            sims = [ float((emb @ e).cpu().numpy()) if hasattr(emb,'cpu') else float(util.pytorch_cos_sim(emb,e).item()) for e in corpus_embs ]
            ranked = sorted(zip(sims, texts), key=lambda x: -x[0])[:3]
            st.markdown("**Top matches**")
            for score, (txt, p) in ranked:
                st.write(f"{p.get('name')} — score {score:.3f}")
        else:
            st.info("No local embedding available. Use textual fallback.")
            q = st.text_input("Describe the image (fallback):")
            if q:
                places = storage.load_places(token)
                matches = [p for p in (places or []) if q.lower() in (p.get("description","")+" "+p.get("name","")).lower()]
                for p in matches:
                    st.write(p.get("name"))

# Feedback
elif choice == "Feedback":
    st.header("Feedback")
    places = storage.load_places(token)
    place_names = [p.get("name") for p in (places or [])]
    selected = st.selectbox("Place", options=place_names if place_names else ["None"])
    fb = st.text_area("Your feedback")
    if st.button("Submit Feedback"):
        lowered = fb.lower()
        sentiment = "Neutral"
        if any(w in lowered for w in ["good","great","amazing","excellent","love","best"]):
            sentiment = "Positive"
        elif any(w in lowered for w in ["bad","worst","awful","hate","terrible"]):
            sentiment = "Negative"
        payload = {"place": selected, "feedback": fb, "sentiment": sentiment}
        storage.save_feedback(payload, token)
        st.success("Feedback saved")

# Map
elif choice == "Map":
    st.header("Map")
    places = storage.load_places(token)
    if isinstance(places, dict):
        places = places.get("data") or places.get("items") or places
    m = folium.Map(location=[17.385,78.4867], zoom_start=7)
    for p in (places or []):
        lat = p.get("lat"); lon = p.get("lon")
        if lat and lon:
            folium.Marker([lat, lon], popup=p.get("name")).add_to(m)
    st_folium(m, width=900)
