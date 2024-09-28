import base64
import json
import os
import random
import json
import logging
import pymongo
import boto3
from anthropic import AnthropicVertex
MODEL = "claude-3-5-sonnet@20240620"



logger = logging.getLogger(__name__)
from db_config import db_connection_string

mongo_client = pymongo.MongoClient(db_connection_string)
db = mongo_client["vehicle_damage"]
collection = db["vehicle_damage"]  
PROJECT_ID="pierre-petersson"
MODEL="claude-3-5-sonnet@20240620"
LOCATION="europe-west1"
client = AnthropicVertex(region=LOCATION, project_id=PROJECT_ID)
    
def process_image(client, base64_image_data):
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image_data,
                        },
                    },
                    {"type": "text", "text": "Can you describe the damage to the vehicle, including a title and the severity (categorized as low, medium or high)? Please return json instead of text. The json structure should use the headings 'title', 'description', and 'severity'."},
                ],
            }
        ],
        model=MODEL,
    )
    try:
        response=(message.model_dump_json(indent=2))      
        # Assuming response is a JSON string
        result = json.loads(response)
        
        # Check if content exists and is a list
        if "content" in result and isinstance(result["content"], list):
            resp_text = result["content"][0]["text"]
            resp_json = json.loads(resp_text.replace("\n", "").replace("`", ""))
            resp_json["severity"] = resp_json["severity"].lower()
            print(resp_json)
            return resp_json;
        else:
            print("Content not found or is not in the expected format.")

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
    except Exception as e:
        print("An error occurred:", e)




def encode_image(image_path):
    """Encode the image as a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def estimate_cost(severity):
    """Estimate the cost of the damage based on the severity."""
    if severity == "low":
        return random.randint(300, 1500)
    elif severity == "medium":
        return random.randint(1000, 5000)
    else:
        return random.randint(3000, 20000)


def image_exists(image_path):
    """Check if the image already exists in the database."""
    doc = collection.find_one({"image_path": image_path})
    return bool(doc)


def main():
    """Main function to process the images and store the data in the database."""
    
    images = os.listdir("./dataset")
    for image_path in images:
        if image_exists(image_path):
            print(f"Image {image_path} already exists in the database")
        else:
            relative_path = os.path.join("./dataset", image_path)
            base64_image = encode_image(relative_path)
            image_data = process_image(client, base64_image)
            image_data["image_path"] = image_path
            image_data["image_base64"] = base64_image
            image_data["cost_estimate"] = estimate_cost(image_data["severity"])
            collection.insert_one(image_data)
            print(image_data)


if __name__ == "__main__":
    main()
