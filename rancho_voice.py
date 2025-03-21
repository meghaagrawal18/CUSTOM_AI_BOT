import asyncio
import edge_tts
import os
import pygame

class RanchoVoice:
    def __init__(self):
        pygame.mixer.init()
        self.voice = "en-IN-PrabhatNeural"  # Male Indian voice
        print(f"Rancho's voice is ready (using Edge TTS with {self.voice})!")
    
    async def _speak_async(self, text):
        communicate = edge_tts.Communicate(text, self.voice)
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
    
    def speak(self, text):
        """Convert text to speech with male Indian voice"""
        try:
            asyncio.run(self._speak_async(text))
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
    
    def test_voice(self):
        """Test the voice with a sample Rancho quote"""
        test_text = "Aal izz well! Main Rancho nahi hoon, main Phunsukh Wangdu hoon!"
        self.speak(test_text)