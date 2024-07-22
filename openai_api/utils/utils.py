from openai import OpenAI
import base64
import json
import cv2
import numpy as np
import re
import os
from log_functions.utils.utils import save_log

LOGPATH = 'output_pdf2images'


def get_summary_from_text_test(summarized_string):
  global LOGPATH
  try:

    summary = """
        # - [Name]: Tacac Annie Magtortor
        # - [Date of Birth]: May 27, 1981
        # - [Age]: 42
        # - [Place of Birth]: LupaGan Clarin Misam
        # - [Weight]: 50 kg
        # - [Height]: 150 cm
        # - [Nationality]: Filipino
        # - [Residential Address in Home Country]: Ilagan Isabela
        # - [Repatriation Port/Airport]: Cauayan City
        # - [Religion]: Catholic
        # - [Education Level]: High School (10-12 years)
        # - [Number of Siblings]: 4
        # - [Marital Status]: Married
        # - [Number of Children]: 1
        # """

    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT3.5")
    return summary


  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending text to OpenAI GPT3.5...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT3.5: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."
  

def get_summary_from_text(summarized_string):
  global LOGPATH


  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an assistant that generates structured text output in a specific format. Always follow the structure and instructions provided without omitting any elements."},
        {"role": "user", "content": summarized_string}
    ],
    temperature=0.3,
    max_tokens=4096,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1
  )



  print("[Success] Sending text to OpenAI GPT3.5")
  save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending text to OpenAI GPT3.5")


  try:
    summary = response.choices[0].message.content
    # print(summary)
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT3.5")
    return summary


  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending text to OpenAI GPT3.5...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT3.5: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."
  

def get_summary_from_text_gpt4omini(summarized_string):
  global LOGPATH


  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an assistant that generates structured text output in a specific format. Always follow the structure and instructions provided without omitting any elements."},
        {"role": "user", "content": summarized_string}
    ],
    temperature=0.3,
    # max_tokens=4096,
    max_tokens=16383,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1
  )



  print("[Success] Sending text to OpenAI GPT4omini")
  save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending text to OpenAI GPT4omini")


  try:
    summary = response.choices[0].message.content
    # print(summary)
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT4omini")
    return summary


  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending text to OpenAI GPT4omini...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4omini: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."
  

def get_summary_from_text_gpt4o(summarized_string):
  global LOGPATH


  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": "You are an assistant that generates structured text output in a specific format. Always follow the structure and instructions provided without omitting any elements."},
        {"role": "user", "content": summarized_string}
    ],
    temperature=0.3,
    max_tokens=4096,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1
  )

  print("[Success] Sending text to OpenAI GPT3.5")
  save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending text to OpenAI GPT4o")


  try:
    summary = response.choices[0].message.content
    # print(summary)
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT4o")
    return summary


  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending text to OpenAI GPT4o...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4o: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."
  

def get_summary_from_image(image_path):

  try: 
    # Read the image file and encode it to base64
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

    # Resize image to a smaller size
    scale_percent = 50  # percent of original size
    width = int(gray_img.shape[1] * scale_percent / 100)
    height = int(gray_img.shape[0] * scale_percent / 100)
    small_gray_img = cv2.resize(gray_img, (width, height), interpolation=cv2.INTER_AREA)

    # Encode grayscale image to base64
    _, buffer = cv2.imencode('.jpg', small_gray_img)
    base64_gray_image = base64.b64encode(buffer).decode('utf-8')

    # Construct the image URL payload
    image_url_payload = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_gray_image}"  
        }
    }
    
    print("Sending image and text to OpenAI...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"Sending image and text to OpenAI...")

    client = OpenAI()

    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You are an OCR tool. Your task is to extract and transcribe text, checkboxes, and tables exactly as they appear in the images provided, without summarizing or altering any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately."
            }
          ]
        },
        {
          "role": "user",
          "content": [
              {
                  "type": "text",
                  "text": """Extract and transcribe the content from the provided image exactly as it appears. This includes text, checkboxes, and tables. Do not summarize or alter any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately.
                            - For checkboxes, use "[ ]" for unchecked and "[x]" for checked.
                            - For tables, preserve the structure with rows and columns as seen in the image."""
              },
              image_url_payload
          ]
        }
      ],
      temperature=1,
      max_tokens=4095,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending image and text to OpenAI GPT4o...")

    try:
      summary = response.choices[0].message.content
      print("[Success] Sending image and text to OpenAI...")
      save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT4o...")
      # print(summary)
      return summary


    except Exception as e:
      print("[Failed] Sending image and text to OpenAI...")
      save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending image and text to OpenAI GPT4o...")
      save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4o: {e}")
      return f"Error generating summary: {e}"
      # return "Summary could not be generated due to an error."

  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4o: {e}")
    return f"Error generating summary: {e}"


def get_summary_from_image_gpt4omini(image_path):

  try: 
    # Read the image file and encode it to base64
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

    # Resize image to a smaller size
    scale_percent = 100  # percent of original size
    width = int(gray_img.shape[1] * scale_percent / 100)
    height = int(gray_img.shape[0] * scale_percent / 100)
    small_gray_img = cv2.resize(gray_img, (width, height), interpolation=cv2.INTER_AREA)

    # Encode grayscale image to base64
    _, buffer = cv2.imencode('.jpg', small_gray_img)
    base64_gray_image = base64.b64encode(buffer).decode('utf-8')

    # Construct the image URL payload
    image_url_payload = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_gray_image}"  
        }
    }
    
    print("Sending image and text to OpenAI GPT4omini...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"Sending image and text to OpenAI GPT4omini...")

    client = OpenAI()

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You are an OCR tool. Your task is to extract and transcribe text, checkboxes, and tables exactly as they appear in the images provided, without summarizing or altering any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately."
            }
          ]
        },
        {
          "role": "user",
          "content": [
              {
                  "type": "text",
                  "text": """Extract and transcribe the content from the provided image exactly as it appears. This includes text, checkboxes, and tables. Do not summarize or alter any content. Maintain the exact formatting, punctuation, line breaks, and represent checkboxes and tables accurately.
                            - For checkboxes, use "[ ]" for unchecked and "[x]" for checked.
                            - For tables, preserve the structure with rows and columns as seen in the image."""
              },
              image_url_payload
          ]
        }
      ],
      temperature=1,
      # max_tokens=4095,
      max_tokens=16383,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending image and text to OpenAI GPT4omini...")

    try:
      summary = response.choices[0].message.content
      print("[Success] Sending image and text to OpenAI GPT4omini...")
      save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI GPT4omini...")
      # print(summary)
      return summary


    except Exception as e:
      print("[Failed] Sending image and text to OpenAI GPT4omini...")
      save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending image and text to OpenAI GPT4omini...")
      save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4omini: {e}")
      return f"Error generating summary: {e}"
      # return "Summary could not be generated due to an error."

  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary from OpenAI GPT4omini: {e}")
    return f"Error generating summary: {e}"
