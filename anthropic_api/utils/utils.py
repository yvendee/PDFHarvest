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


    # # # Display grayscale image
    # # cv2.imshow('Grayscale Image', gray_img)
    # # cv2.waitKey(0)
    # # cv2.destroyAllWindows()

    # Resize image to a smaller size
    scale_percent = 100  # percent of original size
    width = int(gray_img.shape[1] * scale_percent / 100)
    height = int(gray_img.shape[0] * scale_percent / 100)
    small_gray_img = cv2.resize(gray_img, (width, height), interpolation=cv2.INTER_AREA)

    # # # Display resized grayscale image
    # # cv2.imshow('Small Grayscale Image', small_gray_img)
    # # cv2.waitKey(0)
    # # cv2.destroyAllWindows()

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
        # model="claude-3-sonnet-20240229",
        max_tokens=4096,
        temperature=1,
        system="You are an OCR tool. Your task is to extract and transcribe text, checkboxes, and tables exactly as they appear in the images provided, without summarizing or altering any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract and transcribe the content from the provided image exactly as it appears. This includes text, checkboxes, and tables. Do not summarize or alter any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately.
                            - For checkboxes, use "[ ]" for unchecked and "[x]" for checked.
                            - For tables, preserve the structure with rows and columns as seen in the image."""
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

    rtn_str = rtn_str.replace("[TextBlock(text='","").replace("', type='text')]","\n")
    rtn_str = rtn_str.replace('[TextBlock(text="',"").replace(", type='text')]","\n")

    return rtn_str

  except Exception as e:
    print(f"Error generating summary: {e}")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary: {e}")
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending image and text to Anthropic Claude Haiku...")
    return f"Error generating summary: {e}"
