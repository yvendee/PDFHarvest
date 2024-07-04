import os 

def save_csv(filename, header, data):

    # Replace spaces with underscores in headers
    header = [column.replace(' ', '_') for column in header]

    # Check if the file exists
    file_exists = os.path.exists(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        # If the file doesn't exist, write the header
        if not file_exists:
            csvfile.write('"' + '","'.join(header) + '"\n')

        # Write the data
        csvfile.write('"' + '","'.join(data) + '"\n')