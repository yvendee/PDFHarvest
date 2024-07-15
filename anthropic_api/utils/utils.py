import anthropic
import base64
import json
import cv2
import numpy as np
import re
import os
from log_functions.utils.utils import save_log

# Fetch API key from environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")

LOGPATH = 'output_pdf2images'

def get_summary_from_image_using_claude(image_path):
  global api_key

  try:  
    with open(image_path, 'rb') as f:
        image_data = f.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

    # Decode base64 string to bytes
    image_data = base64.b64decode(base64_image)

    # Convert bytes to numpy array
    np_arr = np.frombuffer(image_data, np.uint8)

    # Decode numpy array to image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    # # Display grayscale image
    # cv2.imshow('Grayscale Image', gray_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # Resize image to a smaller size
    scale_percent = 50  # percent of original size
    width = int(gray_img.shape[1] * scale_percent / 100)
    height = int(gray_img.shape[0] * scale_percent / 100)
    small_gray_img = cv2.resize(gray_img, (width, height), interpolation=cv2.INTER_AREA)

    # # Display resized grayscale image
    # cv2.imshow('Small Grayscale Image', small_gray_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Encode grayscale image to base64
    _, buffer = cv2.imencode('.jpg', small_gray_img)
    base64_gray_image = base64.b64encode(buffer).decode('utf-8')

    print("Sending image and text to Anthropic...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"Sending image and text to Anthropic...")

    # Initialize the anthropic client
    client = anthropic.Anthropic(
        api_key=api_key
    )

    # Create a message with the uploaded image
    message = client.messages.create(
        # model="claude-3-opus-20240229",
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        # system="Please analyze the image  and extract relevant information such as objects, text, and any notable features",
        system="Please analyze the image and extract relevant information such as objects, text, and any notable features. For any tables detected, extract text word by word.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Do a summary for the image with paired values\n"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_gray_image  # Replace with your base64 encoded image
                        }
                    }
                ]
            }
        ]
    )

    print("[Success] Sending image and text to Anthropic...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from Anthropic Claude Haiku...")

    rtn_list = message.content
    rtn_str = str(rtn_list)
    return rtn_str

  except Exception as e:
    print(f"Error generating summary: {e}")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary: {e}")
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending image and text to Anthropic Claude Haiku...")
    return f"Error generating summary: {e}"
