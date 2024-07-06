import os 

def save_log(filepath, data):
    with open(filepath, "a", encoding="utf-8") as text_file:
        text_file.write(f"{data}\n")
