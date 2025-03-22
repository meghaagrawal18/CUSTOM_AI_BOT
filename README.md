# Rancho AI Voice Assistant

## Overview
A multilingual voice assistant based on Rancho from "3 Idiots" that responds to questions in multiple languages using speech recognition, text-to-speech, and LLM technology.

## Features
- Multilingual support (English, Hindi, Kannada, Tamil, Telugu, etc.)
- Speech recognition and text-to-speech capabilities
- Character-accurate responses using Gemini LLM
- Automatic language detection
- Text input fallback when speech recognition fails

## Files
- `rancho_voice_assistant_1.py`: Main interface handling speech recognition and TTS
- `multilingual_rancho_1.py`: Language processing and response generation
- `llm_integration.py`: Gemini API integration
- `text_cleaner.py`: Text preprocessing for speech

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Set environment variables:
   ```
   export GEMINI_API_KEY="your_key"
   export PINECONE_API_KEY="your_key"
   ```

## Usage
Run with: `python rancho_voice_assistant_1.py`

Say or type "exit" to quit the program.

## Optional Web Interface
Run the web version with: `python app.py`
Access at http://127.0.0.1:5000
