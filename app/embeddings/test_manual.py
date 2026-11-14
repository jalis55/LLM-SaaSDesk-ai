
from app.embeddings.model import get_embedding_model


embeddings = get_embedding_model()

text = "FlowDesk offers project management tools."

vector = embeddings.embed_query(text)

print("Text:", text)
print("Vector dimensions:", len(vector))
print("First 10 values:", vector[:10])
print("Vector type:", type(vector))
