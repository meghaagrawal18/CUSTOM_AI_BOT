import os
import google.generativeai as genai
import pandas as pd
from pinecone import Pinecone, ServerlessSpec

# Load API Keys
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create an instance of the Pinecone class
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define index name
index_name = "rancho-ai"

# Check if index exists and delete it if it does
if index_name in pc.list_indexes().names():
    print(f"Deleting existing index: {index_name}")
    pc.delete_index(index_name)

# Create Pinecone index with the CORRECT dimension for Gemini embeddings
print(f"Creating new index with dimension 768")
pc.create_index(
    name=index_name,
    dimension=768,  # This matches the embedding dimension from Gemini
    metric="cosine",
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'  # Adjust the region as needed
    )
)

# Connect to the index
index = pc.Index(index_name)

# Load dataset
print("Loading dataset...")
df = pd.read_csv("data/Rancho_AI_Dataset1.csv")
print(f"Loaded dataset successfully with {len(df)} rows")

# Explicitly rename the columns to avoid any character issues
df = df.rename(columns={
    'Category': 'category',
    'User_Input (Question)': 'question',
    df.columns[2]: 'response'  # Use position instead of name for the problematic column
})

print("Renamed columns:", df.columns.tolist())

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

# Store embeddings in Pinecone with the renamed columns
print("\nStarting to process rows...")
for i, row in df.iterrows():
    try:
        # Access data from renamed columns
        question = row['question']
        response = row['response']
        category = row['category']
        
        # Print what we're working with
        print(f"\nProcessing row {i}:")
        print(f"Question: {question}")
        
        # Get embedding
        print("Generating embedding...")
        embedding = get_embedding(question)
        print(f"Embedding dimension: {len(embedding)}")
        
        # Upsert to Pinecone
        print("Upserting to Pinecone...")
        index.upsert(
            vectors=[(f"dialogue_{i}", embedding, {"text": response, "category": category})]
        )
        
        print(f"Row {i} processed successfully")
        
    except Exception as e:
        print(f"Error processing row {i}: {str(e)}")

print("\n✅ Process completed!")