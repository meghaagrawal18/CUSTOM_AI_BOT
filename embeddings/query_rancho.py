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

# Function to convert text to embeddings (same as in store_embeddings.py)
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

def query_rancho(user_question, top_k=3):
    """
    Query the Rancho AI to get a response to a user question.
    
    Args:
        user_question (str): The question asked by the user
        top_k (int): Number of similar questions to retrieve
        
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
    if results.matches:
        # Print all matches for debugging
        print("\nAll matches:")
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
        
        print(f"\nTop match (score: {similarity:.4f}, category: {category}):")
        print(f"Rancho: {rancho_response}")
        
        return rancho_response
    else:
        default_response = "Aal izz not well! I don't have an answer for that right now."
        print(f"\nNo matches found. Returning default response.")
        print(f"Rancho: {default_response}")
        return default_response

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("\nAsk Rancho a question (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Rancho: Bye! All izz well!")
            break
        
        response = query_rancho(user_input)
        print(f"Rancho says: {response}")