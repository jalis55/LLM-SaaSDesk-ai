
import numpy as np

from app.embeddings.model import get_embedding_model


embeddings = get_embedding_model()

sentences = [
    "How much does FlowDesk Pro cost?",
    "What is the price of the Pro subscription?",
    "How do I reset my password?",
]

vectors = embeddings.embed_documents(sentences)

query_vector = np.array(vectors[0])

for sentence, vector in zip(sentences[1:], vectors[1:]):
    similarity = np.dot(query_vector, np.array(vector))

    print(f"\nSentence: {sentence}")
    print(f"Cosine similarity: {similarity:.4f}")
