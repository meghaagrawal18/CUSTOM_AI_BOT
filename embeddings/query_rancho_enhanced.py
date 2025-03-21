import os
import google.generativeai as genai
from pinecone import Pinecone

# Load API Keys
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create an instance of the Pinecone class
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Connect to the existing index
index_name = "rancho-ai"
index = pc.Index(index_name)

# Function to convert text to embeddings
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

# Configure the Gemini generative model
generation_model = genai.GenerativeModel("models/gemini-1.5-pro")

def query_rancho(user_question, top_k=3, similarity_threshold=0.92):
    """
    Query the Rancho AI to get a response to a user question.
    Falls back to LLM generation if no good matches are found.
    
    Args:
        user_question (str): The question asked by the user
        top_k (int): Number of similar questions to retrieve
        similarity_threshold (float): Minimum similarity score to consider a good match
        
    Returns:
        str: Rancho's response to the user's question
    """
    # Generate embedding for user question
    print(f"Generating embedding for: '{user_question}'")
    question_embedding = get_embedding(user_question)
    
    # Query Pinecone
    print(f"Querying Pinecone index: {index_name}")
    results = index.query(
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Get the top match
    if results.matches and results.matches[0].score >= similarity_threshold:
        # Print all matches for debugging
        print("\nMatches found:")
        for i, match in enumerate(results.matches):
            print(f"Match {i+1}:")
            print(f"  Score: {match.score:.4f}")
            print(f"  Category: {match.metadata.get('category', 'Unknown')}")
            print(f"  Response: {match.metadata.get('text', 'No response')[:50]}...")
        
        # Return the top match
        top_match = results.matches[0]
        rancho_response = top_match.metadata.get("text", "Koi response nahi mila!")
        similarity = top_match.score
        category = top_match.metadata.get("category", "Unknown")
        
        print(f"\nUsing top match (score: {similarity:.4f}, category: {category}):")
        print(f"Rancho: {rancho_response}")
        
        return rancho_response
    else:
        print("\nNo good matches found. Generating response with LLM...")
        
        # Get all existing questions and responses for context
        try:
            # Fetch some examples from our dataset to provide context
            collection_query = index.query(
                vector=[0.0] * 768,  # Dummy vector
                top_k=5,
                include_metadata=True
            )
            examples = ""
            for item in collection_query.matches:
                if "text" in item.metadata:
                    examples += f"Q: {user_question}\nA: {item.metadata['text']}\n\n"
        except:
            examples = ""  # If we can't get examples, proceed without them
        
        # Prepare the prompt for the LLM
        prompt = f"""
        You are Rancho from the movie "3 Idiots". Respond to the following question in Rancho's style.
        Use Rancho's personality traits: witty, intelligent, unorthodox, passionate about learning.
        Mix Hindi and English in your response like Rancho does.
        Sometimes use phrases like "Aal izz well" or mention "Farhan" and "Raju".

        Here are some examples of how Rancho responds:
        {examples}
        
        Question: {user_question}
        
        Rancho's response:
        """
        
        # Generate response using Gemini
        try:
            response = generation_model.generate_content(prompt)
            llm_response = response.text.strip()
            print(f"Generated LLM response:\n{llm_response}")
            return llm_response
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            return "Aal izz not well! I'm having trouble thinking right now. Ask me something else, yaar!"

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("\nAsk Rancho a question (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Rancho: Bye! All izz well!")
            break
        
        response = query_rancho(user_input)
        print(f"Rancho says: {response}")