from typing import List, Optional
import pymongo
from db_config import db_connection_string
from typing import List, Optional
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
mongo_client = pymongo.MongoClient(db_connection_string)
db = mongo_client["vehicle_damage2"]
collection = db["vehicle_damage2"]


def get_embedding(
    texts: list = None,
    task: str = "RETRIEVAL_DOCUMENT",
    dimensionality: Optional[int] = 256,
) -> List[List[float]]:
    """Embeds texts with a pre-trained, foundational model.
    Args:
        texts (List[str]): A list of texts to be embedded.
        task (str): The task type for embedding. Check the available tasks in the model's documentation.
        dimensionality (Optional[int]): The dimensionality of the output embeddings.
    Returns:
        List[List[float]]: A list of lists containing the embedding vectors for each input text
    """
    if texts is None:
        texts = ["banana muffins? ", "banana bread? banana muffins?"]
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    # Example response:
    # [[0.006135190837085247, -0.01462465338408947, 0.004978656303137541, ...],
    return [embedding.values for embedding in embeddings]


def main():
    """Generate embeddings for the damage descriptions."""
    for document in collection.find():
        embedding = document.get("embedding")
        if not embedding:
            damage_description = document["description"]
            embedding = get_embedding([damage_description])
            collection.update_one({"_id": document["_id"]}, {"$set": {"embedding": embedding}})
            print(embedding)
        print(f"Embedding for {document['image_path']} already exists. Skipping.")


if __name__ == "__main__":
    main()