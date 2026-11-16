# Cartesia Voice Studio

A small Streamlit app that turns text into speech with the Cartesia Sonic API.

- Pick a voice from your Cartesia account (loaded live from the API)
- Choose language (English, Bengali, Hindi and more) and model (Sonic 3.5 / 3.6 / 3)
- Adjust speed, generate, listen in the browser and download the MP3

## API key

The app reads `CARTESIA_API_KEY` from Streamlit Secrets when present.
Without it, paste your Cartesia API key in the sidebar — it is kept in the
browser session only and never stored.
