from openai import OpenAI
import base64
import json
import re
from log_functions.utils.utils import save_log

LOGPATH = 'output_pdf2images'

def get_summary_from_text(summarized_string):
  global LOGPATH


  print("Sending text to OpenAI...")
  save_log(os.path.join(LOGPATH, "logs.txt"),"Sending text to OpenAI...")
  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Please analyze the summarized text and extract relevant information."},
        {"role": "user", "content": summarized_string}
    ],
    temperature=0.7,
    max_tokens=2030,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )

  print("[Success] Sending text to OpenAI")
  save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending text to OpenAI")


  try:
    summary = response.choices[0].message.content
    # print(summary)
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI")
    return summary


  except Exception as e:
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending text to OpenAI...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."
  

def get_summary_from_image(image_path):

  # Read the image file and encode it to base64
  with open(image_path, 'rb') as f:
      image_data = f.read()
      base64_image = base64.b64encode(image_data).decode('utf-8')

  # Construct the image URL payload
  image_url_payload = {
      "type": "image_url",
      "image_url": {
          "url": f"data:image/jpeg;base64,{base64_image}"  
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
            "text": "Please analyze the image and extract relevant information such as objects, text, and any notable features"
          }
        ]
      },
      {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Do a summary for the image\n"
            },
            image_url_payload
        ]
      }
    ],
    temperature=1,
    max_tokens=2030,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )

  save_log(os.path.join(LOGPATH, "logs.txt"),"[Success] Sending image and text to OpenAI...")

  try:
    summary = response.choices[0].message.content
    print("[Success] Sending image and text to OpenAI...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"Received data from OpenAI...")
    # print(summary)
    return summary


  except Exception as e:
    print("[Failed] Sending image and text to OpenAI...")
    save_log(os.path.join(LOGPATH, "logs.txt"),"[Failed] Sending image and text to OpenAI...")
    save_log(os.path.join(LOGPATH, "logs.txt"),f"Error generating summary: {e}")
    return f"Error generating summary: {e}"
    # return "Summary could not be generated due to an error."

