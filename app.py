import requests
import streamlit as st

API_BASE = "https://api.cartesia.ai"
API_VERSION = "2026-08-14"

LANGUAGES = {
    "English": "en",
    "Bengali (বাংলা)": "bn",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Italian": "it",
    "Dutch": "nl",
    "Polish": "pl",
    "Russian": "ru",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Thai": "th",
    "Indonesian": "id",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Punjabi": "pa",
}

MODELS = ["sonic-3.5", "sonic-3.6", "sonic-3"]

st.set_page_config(page_title="Cartesia Voice Studio", page_icon="🎙️")
st.title("🎙️ Cartesia Voice Studio")
st.caption("Text to speech with Cartesia Sonic — for Shorts voiceovers, narration and voice tests.")


def get_api_key():
    try:
        key = st.secrets.get("CARTESIA_API_KEY", "")
    except Exception:
        key = ""
    if key:
        return key
    return st.session_state.get("api_key_input", "")


with st.sidebar:
    st.header("Settings")
    try:
        has_secret = bool(st.secrets.get("CARTESIA_API_KEY", ""))
    except Exception:
        has_secret = False
    if has_secret:
        st.success("API key loaded from Secrets.")
    else:
        st.text_input(
            "Cartesia API key",
            type="password",
            key="api_key_input",
            help="Paste your Cartesia API key. It stays in this session only. "
            "For permanent use, add CARTESIA_API_KEY in the app's Streamlit Secrets.",
        )
    model = st.selectbox("Model", MODELS, index=0)
    language_name = st.selectbox("Language", list(LANGUAGES.keys()), index=0)
    speed = st.slider("Speed", 0.6, 1.5, 1.0, 0.05)

api_key = get_api_key()
headers = {"X-API-Key": api_key, "Cartesia-Version": API_VERSION}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_voices(key):
    r = requests.get(
        f"{API_BASE}/voices",
        headers={"X-API-Key": key, "Cartesia-Version": API_VERSION},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    voices = payload.get("data", payload) if isinstance(payload, dict) else payload
    return voices


voice_options = {}
if api_key:
    try:
        for v in fetch_voices(api_key):
            label = v.get("name", "Voice")
            desc = (v.get("description") or "").strip()
            if desc:
                label = f"{label} — {desc[:60]}"
            voice_options[label] = v.get("id")
    except Exception as e:
        st.warning(f"Could not load the voice list ({e}). You can still paste a voice ID below.")
else:
    st.info("Add your Cartesia API key in the sidebar to load voices and generate speech.")

voice_label = None
voice_id = ""
if voice_options:
    voice_label = st.selectbox("Voice", list(voice_options.keys()))
    voice_id = voice_options[voice_label]
else:
    voice_id = st.text_input("Voice ID", value="db6b0ed5-d5d3-463d-ae85-518a07d3c2b4")

text = st.text_area("Text to speak", height=160, placeholder="Type or paste your script here…")
st.caption(f"{len(text)} characters")

if st.button("🔊 Generate voice", type="primary", disabled=not (api_key and text.strip() and voice_id)):
    body = {
        "model_id": model,
        "transcript": text.strip(),
        "voice": {"mode": "id", "id": voice_id},
        "output_format": {"container": "mp3", "bit_rate": 128000, "sample_rate": 44100},
        "language": LANGUAGES[language_name],
    }
    if speed != 1.0:
        body["generation_config"] = {"speed": speed}
    with st.spinner("Generating audio…"):
        try:
            r = requests.post(f"{API_BASE}/tts/bytes", headers=headers, json=body, timeout=120)
            r.raise_for_status()
            st.session_state["audio"] = r.content
        except Exception as e:
            st.error(f"Generation failed: {e}")

if st.session_state.get("audio"):
    st.audio(st.session_state["audio"], format="audio/mp3")
    st.download_button(
        "⬇ Download MP3",
        data=st.session_state["audio"],
        file_name="cartesia-voice.mp3",
        mime="audio/mpeg",
    )
