
def read_custom_prompt(file_path):    
    try:
        # Attempt to open the file for reading
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()  # Read content and remove trailing whitespace
            return content
    except FileNotFoundError:
        # If the file doesn't exist, create a new one and ask for input
        print(f"File '{file_path}' not found")
        return "Not Found"
    except IOError as e:
        print(f"Error: Unable to read the file '{file_path}': {e}")
        return "Read Error"
