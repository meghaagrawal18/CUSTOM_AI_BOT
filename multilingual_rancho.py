import os
import google.generativeai as genai
from pinecone import Pinecone
from googletrans import Translator

# Load API Keys
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create instances for services
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
translator = Translator()

# Connect to the existing index
index_name = "rancho-ai"
index = pc.Index(index_name)

# Function to convert text to embeddings using the selected model
def get_embedding(text):
    try:
        embedding = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return embedding["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise

def detect_language(text):
    """Detect the language of the input text"""
    try:
        detection = translator.detect(text)
        return detection.lang
    except Exception as e:
        print(f"Error detecting language: {str(e)}")
        return "en"  # Default to English if detection fails

def translate_text(text, src_lang, dest_lang):
    """Translate text from source language to destination language"""
    if src_lang == dest_lang:
        return text
    
    try:
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return text  # Return original text if translation fails

def query_rancho_multilingual(user_question, top_k=3, similarity_threshold=0.85):
    """
    Multilingual version of query_rancho that handles different languages
    """
    # Detect the language of the user's question
    input_language = detect_language(user_question)
    print(f"Detected language: {input_language}")
    
    # If not English, translate to English for processing
    english_question = user_question
    if input_language != "en":
        english_question = translate_text(user_question, input_language, "en")
        print(f"Translated question: {english_question}")
    
    # Generate embedding for the English version of the question
    question_embedding = get_embedding(english_question)
    
    # Query Pinecone
    results = index.query(
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Check if we have a good match
    if results.matches and results.matches[0].score >= similarity_threshold:
        # Get the top match
        top_match = results.matches[0]
        rancho_response = top_match.metadata.get("text", "")
        similarity = top_match.score
        category = top_match.metadata.get("category", "Unknown")
        
        print(f"\nUsing top match (score: {similarity:.4f}, category: {category})")
        
        # If the user's question was not in English, translate the response back
        if input_language != "en":
            # First, decide which parts to translate and which to keep
            # For Rancho's character, we might want to keep Hindi phrases untranslated
            # This is a simplified approach - you might want more sophisticated handling
            
            # For now, translate the entire response
            translated_response = translate_text(rancho_response, "en", input_language)
            print(f"Translated response to {input_language}")
            return translated_response
        else:
            return rancho_response
    else:
        # No good match, return default response
        default_response = "Aal izz not well! I don't have an answer for that right now."
        
        # Translate the default response if needed
        if input_language != "en":
            return translate_text(default_response, "en", input_language)
        return default_response