import os 

def save_csv(filename, header, data):

    # Replace spaces with underscores in headers
    header = [column.replace(' ', '_') for column in header]

    # Check if the file exists
    file_exists = os.path.exists(filename)


    # Function to process each data item
    def process_data_item(item):
        if item.strip() in ["Not Provided", "Not provided", "Null", "Not found", "Not Found", "Not-found", "Not-Found","Not Specified", "Not specified", "Not Applicable", "Not applicable"]:
            return ""
        else:
            return item.strip()

    # Process each item in data list
    processed_data = [process_data_item(item) for item in data]


    # Function to process each data item
    def process_data_item2(item):
        # Split the item into words, lowercase each word, capitalize the first letter
        words = item.split()
        processed_words = [word.lower().capitalize() for word in words]
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