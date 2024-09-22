import base64
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GPT_API_KEY')

# Function to compress and encode the image to base64
def encode_image(image_path, max_size=(500, 500), quality=30):
    """
    Compress the image by resizing and reducing quality, then return base64 encoded string.
    
    Args:
        image_path (str): Path to the image file.
        max_size (tuple): Maximum width and height of the image.
        quality (int): Quality of the output image (1-100).

    Returns:
        str: Base64 encoded compressed image.
    """
    try:
        # Open the image and resize it to the max_size, maintaining aspect ratio
        img = Image.open(image_path)
        img.thumbnail(max_size)

        # Compress the image by reducing its quality
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=quality)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

# Function to send API call with base64 encoded images
def send_api_call(prompt, image_paths):
    # Compress and encode each image
    base64_images = [encode_image(image_path) for image_path in image_paths]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Build the messages list with the image URLs
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]
    
    # Add each image to the 'content' list in the messages
    for base64_image in base64_images:
        if base64_image:  # Ensure the image was successfully encoded
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

    # Define the payload
    payload = {
        "model": "gpt-4o-mini",  # Ensure that the model name is correct
        "messages": messages,
        "max_tokens": 300
    }

    # Send the request to OpenAI's API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    res = response.json()['choices'][0]['message']['content'].split(" ")
    return [int(ind) for ind in res]

# Example usage
image_paths = ["./images/image1.jpeg", "./images/image2.jpeg", "./images/image3.jpeg", "./images/image4.jpeg", "./images/image5.jpeg"]
response = send_api_call(
    "You are given several images. Select exactly two that would work best for Instagram. \
    Respond only with the numbers (indices) of the images to keep, like '1 2' for the first and second images I sent. \
    Do not include any other text in your response. Only return the indices.",
    image_paths)

# Print the response
print(response)
