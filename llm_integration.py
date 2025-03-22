import os
import google.generativeai as genai
from deep_translator import GoogleTranslator

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RanchoLLM:
    def __init__(self):
        # Initialize the Gemini model
        self.model = genai.GenerativeModel("models/gemini-1.5-pro")
        print("Rancho LLM system initialized!")

    def generate_response(self, question, language_code="en"):
        """Generate a response using Gemini when vector search fails"""
        try:
            print(f"Generating LLM response for: '{question}' in language: {language_code}")
            
            # Create a prompt that instructs Gemini to respond like Rancho
            prompt = f"""
            You are Rancho from the movie "3 Idiots". Respond to the following question in Rancho's style.
            
            Rancho's characteristics:
            - Witty and intelligent
            - Unorthodox approach to education and life
            - Often uses phrases like "Aal izz well!"
            - Passionate about learning, not just grades
            - Believes in pursuing excellence, not success
            - Occasionally mixes Hindi and English (Hinglish)
            - Best friends are Farhan and Raju
            - Actually named Phunsukh Wangdu
            
            Question: {question}
            
            Respond as Rancho would, keeping your answer concise (2-4 sentences).
            """
            
            # Generate response from Gemini
            print("Sending prompt to Gemini...")
            response = self.model.generate_content(prompt)
            llm_response = response.text.strip()
            
            print(f"Generated LLM response: {llm_response}")
            
            # If language is not English, translate the response
            if language_code != "en" and language_code != "hi":
                try:
                    print(f"Translating LLM response to {language_code}")
                    translated_response = GoogleTranslator(source='en', target=language_code).translate(llm_response)
                    print(f"Translated LLM response: {translated_response}")
                    return translated_response
                except Exception as e:
                    print(f"Translation error: {str(e)}")
                    return llm_response
            
            return llm_response
            
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            default_msg = "Aal izz well! I'm having trouble thinking right now."
            
            if language_code != "en":
                try:
                    return GoogleTranslator(source='en', target=language_code).translate(default_msg)
                except:
                    pass
            
            return default_msg