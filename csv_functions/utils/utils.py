import os 

def save_csv(filename, header, data):
    # Replace spaces with underscores in headers
    header = [column.replace(' ', '_') for column in header]

    # Check if the file exists
    file_exists = os.path.exists(filename)

    # Function to process each data item
    def process_data_item(item):
        unwanted_values = ["not provided", "n/a", "null", "not found", "not-found", "not specified", "not applicable"]
        item_lower = item.strip().lower()
        for unwanted in unwanted_values:
            if item_lower == unwanted:
                return ""
        return item.strip()

    # Process each item in data list
    processed_data = [process_data_item(item) for item in data]

    # Function to process each data item
    def process_data_item2(item):
        words = item.split()
        processed_words = []
        for word in words:
            processed_words.append(word.lower().capitalize())
        return ' '.join(processed_words)

    # Process each item in data list
    processed_data2 = [process_data_item2(item) for item in processed_data]

    # Special Case: Uppercase All
    # Uppercase the value of the second index (header) (maid_ref_code) in processed_data2
    if len(processed_data2) > 1:
        item = processed_data2[1]  # Assuming you want to access the second item in processed_data2
        processed_data2[1] = item.upper()  # Uppercase the second index

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        # If the file doesn't exist, write the header
        if not file_exists:
            csvfile.write('"' + '","'.join(header) + '"\n')

        # Write the data
        csvfile.write('"' + '","'.join(processed_data2) + '"\n')