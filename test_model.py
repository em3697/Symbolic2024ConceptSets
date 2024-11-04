# Load model and tokenizer
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

tokenizer = AutoTokenizer.from_pretrained("GanjinZero/coder_eng_pp")
model = AutoModel.from_pretrained("GanjinZero/coder_eng_pp")

# Example medical terms
texts = ["hypertension", "high blood pressure"]

# Tokenize and encode the texts
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

# Generate embeddings with `return_dict=True`
with torch.no_grad():
    outputs = model(**inputs, return_dict=True)
    embeddings = outputs.last_hidden_state[:, 0, :].detach()  # CLS token embeddings

print(embeddings.shape)

# Calculate cosine similarity (detached tensors for NumPy)
similarity = cosine_similarity(embeddings[0].unsqueeze(0).numpy(), embeddings[1].unsqueeze(0).numpy())
print(f"Similarity between terms: {similarity[0][0]:.4f}")

# Define a function to find the most similar term
def find_most_similar(term, term_list):
    # Tokenize and encode the terms
    inputs = tokenizer([term] + term_list, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        term_embeddings = model(**inputs, return_dict=True).last_hidden_state[:, 0, :].detach()

    # Calculate cosine similarity with detached tensors
    term_similarities = cosine_similarity(term_embeddings[0].unsqueeze(0).numpy(), term_embeddings[1:].numpy())
    
    most_similar_idx = term_similarities.argmax()
    most_similar_term = term_list[most_similar_idx]
    
    return most_similar_term, term_similarities[0][most_similar_idx].item()

# Updated function to return similarities with terms
def find_similarities(term, term_list):
    """
    Find similarity scores between a term and a list of terms, returning sorted results
    
    Parameters:
        term (str): Target term to compare against
        term_list (list): List of terms to compare with target
        
    Returns:
        list: List of tuples containing (term, similarity_score), sorted by score in descending order
    """
    # Tokenize and encode the terms
    inputs = tokenizer([term] + term_list, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        term_embeddings = model(**inputs, return_dict=True).last_hidden_state[:, 0, :].detach()

    # Calculate cosine similarity with detached tensors
    term_similarities = cosine_similarity(term_embeddings[0].unsqueeze(0).numpy(), term_embeddings[1:].numpy())
    
    # Create list of (term, score) tuples
    similarity_pairs = list(zip(term_list, term_similarities[0].tolist()))
    
    # Sort by similarity score in descending order
    sorted_similarities = sorted(similarity_pairs, key=lambda x: x[1], reverse=True)
    
    return sorted_similarities

# Function to pretty print results
def print_similarity_results(term, results):
    """
    Print similarity results in a formatted way
    
    Parameters:
        term (str): Target term that was compared
        results (list): List of (term, score) tuples from find_similarities
    """
    print(f"\nSimilarity scores for '{term}':")
    print("-" * 50)
    print(f"{'Term':<30} | {'Similarity Score':<15}")
    print("-" * 50)
    for concept, score in results:
        print(f"{concept:<30} | {score:.4f}")

# Test with a target term
target_term = "hypertension"
term_list = ["high blood pressure", "diabetes", "asthma", "elevated blood pressure", 
             "cardiovascular disease", "chronic kidney disease"]

# Get sorted similarity scores
similarity_results = find_similarities(target_term, term_list)

# Print results
print_similarity_results(target_term, similarity_results)

# You can also convert to a pandas DataFrame for additional analysis
df_similarities = pd.DataFrame(similarity_results, columns=['Term', 'Similarity Score'])
print("\nAs DataFrame:")
print(df_similarities)

# Example of filtering for high similarity scores
high_similarity_threshold = 0.8
high_similarity_terms = [(term, score) for term, score in similarity_results if score >= high_similarity_threshold]
if high_similarity_terms:
    print(f"\nTerms with similarity score >= {high_similarity_threshold}:")
    print_similarity_results(target_term, high_similarity_terms)

    
# Get sorted similarities
results = find_similarities("hypertension", ["high blood pressure", "diabetes", "asthma"])

# Access individual results
for term, score in results:
    print(f"{term}: {score:.4f}")

# Get just the highest scoring term
highest_term, highest_score = results[0]

# Convert to DataFrame for more analysis
df = pd.DataFrame(results, columns=['Term', 'Similarity Score'])