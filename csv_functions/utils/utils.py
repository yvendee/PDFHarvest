import os
import re

# Define accepted characters as a regular expression pattern
accepted_chars_pattern = r'[ &_$a-zA-Z0-9\(\)\-\~\/\\\<\>=\.\@\":;+|]'

def filter_accepted_chars(item):
    # Use regular expression to filter out unwanted characters
    return ''.join(re.findall(accepted_chars_pattern, item))

def save_csv(filename, header, data):
    # Replace spaces with underscores in headers
    header = [column.replace(' ', '_') for column in header]
    header = [filter_accepted_chars(item) for item in header]

    # Check if the file exists
    file_exists = os.path.exists(filename)

    # Function to process each data item
    def process_data_item(item):
        unwanted_values = ["not provided", "n/a", "null", "not found", "not-found", "not specified", "not applicable", "none", "not mentioned", "not-mentioned", "not evaluated"]
        item_lower = item.strip().lower()
        
        # Check for unwanted values
        for unwanted in unwanted_values:
            if item_lower == unwanted:
                return ""
        
        # Filter accepted characters
        filtered_item = filter_accepted_chars(item)
        
        return filtered_item.strip()

    # Process each item in data list
    processed_data = [process_data_item(item) for item in data]

    # Function to process each data item and capitalize words
    def process_data_item2(item):
        words = item.split()
        processed_words = []
        for word in words:
            processed_words.append(word.lower().capitalize())
        return ' '.join(processed_words)

    # Process each item in data list
    processed_data2 = [process_data_item2(item) for item in processed_data]

    try:
        # Special Case: Uppercase the second index in processed_data2
        if len(processed_data2) > 1:
            processed_data2[1] = processed_data2[1].upper()

        # Convert "Yrs" or "Years" to "yrs" or "years" in processed_data2[2]
        if len(processed_data2) > 2:
            processed_data2[16] = processed_data2[16].replace("Yrs", "yrs").replace("Years", "years").replace("Level", "level")
    except Exception as e:
        print(e)

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        # If the file doesn't exist, write the header
        if not file_exists:
            csvfile.write('"' + '","'.join(header) + '"\n')

        # Write the data
        csvfile.write('"' + '","'.join(processed_data2) + '"\n')

# # # Example usage:
# filename = 'example.csv'
# header = ['Column 1', 'Column 2', 'Column 3']
# data = ['$456â‰0%abA', "hello", 'Secondary level (8~9 Yrs)', 'null']

# save_csv(filename, header, data)
