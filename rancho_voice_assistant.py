import speech_recognition as sr
import asyncio
import edge_tts
import os
import pygame
from multilingual_rancho import query_rancho_multilingual, detect_language

class RanchoVoice:
    def __init__(self):
        pygame.mixer.init()
        # Dictionary of voice options for different languages
        self.voices = {
            "en": "en-IN-PrabhatNeural",    # English (India) - Male
            "hi": "hi-IN-MadhurNeural",     # Hindi - Male
            "es": "es-MX-JorgeNeural",      # Spanish - Male
            "fr": "fr-FR-HenriNeural",      # French - Male
            "de": "de-DE-ConradNeural",     # German - Male
            "zh": "zh-CN-YunxiNeural",      # Chinese - Male
            "ja": "ja-JP-KeitaNeural",      # Japanese - Male
            "ru": "ru-RU-DmitryNeural",     # Russian - Male
            # Add more languages as needed
        }
        self.default_voice = "en-IN-PrabhatNeural"  # Default to Indian English male
        print(f"Rancho's voice system is ready!")
    
    async def _speak_async(self, text, language_code="en"):
        # Select appropriate voice for the language
        voice = self.voices.get(language_code, self.default_voice)
        print(f"Using voice: {voice} for language: {language_code}")
        
        try:
            communicate = edge_tts.Communicate(text, voice)
            output_file = "rancho_response.mp3"
            await communicate.save(output_file)
            
            # Play the audio
            print(f"Rancho says: {text}")
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload()
            os.remove(output_file)
        except Exception as e:
            print(f"Error with voice {voice}: {str(e)}")
            # Fall back to default voice if specific language voice fails
            if voice != self.default_voice:
                print(f"Falling back to default voice")
                communicate = edge_tts.Communicate(text, self.default_voice)
                output_file = "rancho_response.mp3"
                await communicate.save(output_file)
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.unload()
                os.remove(output_file)
    
    def speak(self, text, language_code="en"):
        """Convert text to speech with appropriate voice for the language"""
        try:
            asyncio.run(self._speak_async(text, language_code))
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
    
    def test_voices(self):
        """Test different language voices"""
        for lang_code, voice in self.voices.items():
            print(f"Testing {lang_code} voice...")
            test_text = "Hello! This is a test of Rancho's voice."
            if lang_code == "hi":
                test_text = "नमस्ते! यह रंचो की आवाज़ का परीक्षण है।"
            self.speak(test_text, lang_code)

# Speech recognition with language detection
class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
    
    def listen(self):
        """Listen for user input and detect language"""
        with sr.Microphone() as source:
            print("\nListening for your question...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing speech...")
                
                # Try to recognize with Google (supports multiple languages)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"You said: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Sorry, I didn't understand that.")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return None
            except Exception as e:
                print(f"Error during listening: {e}")
                return None

# Main application
def main():
    print("Starting Rancho Multilingual Voice Assistant...")
    
    # Initialize components
    voice_listener = VoiceListener()
    rancho_voice = RanchoVoice()
    
    # Test voice
    print("Testing Rancho's voice...")
    rancho_voice.speak("Aal izz well! Main Rancho nahi hoon, main Phunsukh Wangdu hoon!")
    
    print("\nRancho AI Voice Assistant is ready! Speak something...")
    
    while True:
        # Listen for user question
        user_question = voice_listener.listen()
        
        if user_question:
            # Check for exit commands in common languages
            exit_commands = ["exit", "quit", "bye", "goodbye", "adiós", "adios", "salir", 
                           "अलविदा", "बाय", "निकास", "निकलें", "au revoir", "sortie"]
            
            if any(cmd in user_question.lower() for cmd in exit_commands):
                # Detect language for appropriate goodbye
                lang = detect_language(user_question)
                if lang == "hi":
                    rancho_voice.speak("अलविदा दोस्त! ऑल इज़ वेल!", lang)
                elif lang == "es":
                    rancho_voice.speak("¡Adiós amigo! ¡Todo está bien!", lang)
                else:
                    rancho_voice.speak("Aal izz well! Goodbye friend!", lang)
                break
            
            # Detect language
            language_code = detect_language(user_question)
            print(f"Detected language: {language_code}")
            
            # Process with Rancho AI (multilingual)
            rancho_response = query_rancho_multilingual(user_question)
            
            # Speak the response with appropriate voice
            rancho_voice.speak(rancho_response, language_code)

if __name__ == "__main__":
    main()