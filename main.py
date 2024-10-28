# Load model and tokenizer
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

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

# Test with a target term
target_term = "hypertension"
term_list = ["high blood pressure", "diabetes", "asthma"]

most_similar_term, similarity_score = find_most_similar(target_term, term_list)
print(f"Most similar term to '{target_term}': {most_similar_term} (Similarity: {similarity_score:.4f})")


