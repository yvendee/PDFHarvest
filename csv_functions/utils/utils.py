import os
import re

# Define accepted characters as a regular expression pattern
accepted_chars_pattern = r'[ &_$a-zA-Z0-9\(\)\-\~\/\\\<\>=\.\@:;+|]'

def filter_accepted_chars(item):
    # Use regular expression to filter out unwanted characters
    return ''.join(re.findall(accepted_chars_pattern, item))

def save_csv(filename, header, data):
    # Replace spaces with underscores in headers
    header = [column.replace(' ', '_') for column in header]

    # character cleansing in the list "header"
    header = [filter_accepted_chars(item) for item in header]

    # Modify specific header value if found
    for i in range(len(header)):
        if header[i] == 'language_english_experience':
            header[i] = 'Language–English–Experience'
        if header[i] == 'language_english_stars':
            header[i] = 'Language–English–stars'
        if header[i] == 'expertise_care_for_infant|children_experience__willing':
            header[i] = 'Expertise–Care for Infant/Children–Experience – Willing?'
        if header[i] == 'expertise_care_for_infant|children_experience_willing':
            header[i] = 'Expertise–Care for Infant/Children–Experience – Willing?'
        if header[i] == 'expertise_care_for_infant|children_experience':
            header[i] = 'Expertise–Care for Infant/Children–Experience'

        if header[i] == 'expertise_care_for_infant|children_stars':
            header[i] = 'Expertise–Care for Infant/Children–stars'
        if header[i] == 'expertise_care_for_elderly_experience__willing':
            header[i] = 'Expertise–Care for Elderly–Experience – Willing?'

        if header[i] == 'expertise_care_for_elderly_experience':
            header[i] = 'Expertise–Care for Elderly–Experience'

        if header[i] == 'expertise_care_for_elderly_stars':
            header[i] = 'Expertise–Care for Elderly–stars'
        if header[i] == 'expertise_care_for_disabled_experience__willing':
            header[i] = 'Expertise–Care for Disabled–Experience – Willing?'
        if header[i] == 'expertise_care_for_disabled_experience_willing':
            header[i] = 'Expertise–Care for Disabled–Experience – Willing?'
        
        if header[i] == 'expertise_care_for_disabled_experience':
            header[i] = 'Expertise–Care for Disabled–Experience'
        if header[i] == 'expertise_care_for_disabled_stars':
            header[i] = 'Expertise–Care for Disabled–stars'
        if header[i] == 'expertise_general_housework_experience__willing':
            header[i] = 'Expertise–General Housework–Experience – Willing?'
        if header[i] == 'expertise_general_housework_experience_willing':
            header[i] = 'Expertise–General Housework–Experience – Willing?'
        if header[i] == 'expertise_general_housework_experience_willing':
            header[i] = 'Expertise–General Housework–Experience – Willing?'

        if header[i] == 'expertise_general_housework_experience':
            header[i] = 'Expertise–General Housework–Experience'
        if header[i] == 'expertise_general_housework_stars':
            header[i] = 'Expertise–General Housework–stars'
        if header[i] == 'expertise_cooking_experience__willing':
            header[i] = 'Expertise–Cooking–Experience – Willing?'
        if header[i] == 'expertise_cooking_experience_willing':
            header[i] = 'Expertise–Cooking–Experience – Willing?'

        if header[i] == 'expertise_cooking_experience':
            header[i] = 'Expertise–Cooking–Experience'
        if header[i] == 'expertise_cooking_stars':
            header[i] = 'Expertise–Cooking–stars'

        if header[i] == 'additional_info_able_to_handle_pork':
            header[i] = 'AdditionalInfo–Able to handle pork?'
        if header[i] == 'additional_info_able_to_eat_pork':
            header[i] = 'AdditionalInfo–Able to eat pork?'
        if header[i] == 'additional_info_able_to_handle_beef':
            header[i] = 'AdditionalInfo–Able to handle beef?'
        if header[i] == 'additional_info_able_to_care_dog|cat':
            header[i] = 'AdditionalInfo–Able to care dog/cat?'

        if header[i] == 'additional_info_able_to_do_gardening_work':
            header[i] = 'AdditionalInfo–Able to do gardening work?'

        if header[i] == 'additional_info_able_to_do_simple_sewing':
            header[i] = 'AdditionalInfo–Able to do simple sewing?'
        if header[i] == 'additional_info_willing_to_wash_car':
            header[i] = 'AdditionalInfo–Willing to wash car?'
        if header[i] == 'experience_singaporean_experience':
            header[i] = 'Experience–Singaporean–Experience'

        if header[i] == 'language_mandarin|chinese_dialect_experience':
            header[i] = 'Language–Mandarin/Chinese–Dialect–Experience'
        if header[i] == 'language_mandarin|chinese_dialect_stars':
            header[i] = 'Language–Mandarin/Chinese–Dialect–stars'
        if header[i] == 'experience_others_experience':
            header[i] = 'Experience–Others–Experience'

    # Check if the file exists
    file_exists = os.path.exists(filename)

    # Function to process each data item
    def process_data_item(item):
        unwanted_values = ["not provided", "n/a", "n.a","null", "not found", "not-found", "not specified", "not applicable", "none", "not mentioned", "not-mentioned", "not evaluated"]
        item_lower = item.strip().lower()
        
        # Check for unwanted values
        for unwanted in unwanted_values:
            if item_lower == unwanted:
                return ""
                
        # Check if any unwanted value is in item_lower
        # Therefore, if item_lower is " language english experience null, ", the process_data_item function will return ""

        if len(item_lower) <= 17: ## to make sure that it will not affect a item's value has long content like "maid employment history" or others
            # Execute the block only if item_lower is 17 characters or shorter
            for unwanted in unwanted_values:
                if unwanted in item_lower:
                    return ""  # Return empty string if unwanted value is found

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
