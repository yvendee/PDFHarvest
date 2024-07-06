from functools import wraps
from flask import Flask, request, Blueprint, render_template, jsonify, session, redirect, url_for, send_file

import os
import time
from threading import Thread
import zipfile
import shutil
import re

# import os
import io
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from flask_cors import CORS
from openai_api.utils.utils import ( get_summary_from_image, get_summary_from_text )
from custom_prompt.utils.utils import read_custom_prompt
from csv_functions.utils.utils import save_csv
from log_functions.utils.utils import save_log

# Build app
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = 'your_secret_key'  # Needed for session management

# Hardcoded username and password (for demo purposes)
USERNAME = "searchmaid"
PASSWORD = "maidasia"

# Global variable to store current OCR setting
current_ocr = "tesseractOCR"

# Define a decorator function to check if the user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Function to check if user is authenticated
def check_authenticated():
    if 'username' in session:
        return session['username'] == USERNAME
    return False

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
EXTRACTED_PROFILE_PICTURE_FOLDER = 'extracted_images'
EXTRACTED_PAGE_IMAGES_FOLDER = 'output_pdf2images'
GENERATE_CSV_FOLDER = 'output_csv'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_PROFILE_PICTURE_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_PAGE_IMAGES_FOLDER, exist_ok=True)
os.makedirs(GENERATE_CSV_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXTRACTED_PROFILE_PICTURE_FOLDER'] = EXTRACTED_PROFILE_PICTURE_FOLDER
app.config['EXTRACTED_PAGE_IMAGES_FOLDER'] = EXTRACTED_PAGE_IMAGES_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

progress = {}

####### PDF to Images Extraction ################
def pdf_to_jpg(pdf_file, output_folder, zoom=2):
    # Get the base name of the PDF file to create a subfolder
    base_name = os.path.splitext(os.path.basename(pdf_file))[0]
    base_name = base_name.replace(" ","_")
    subfolder = os.path.join(output_folder, base_name)
    
    # Ensure the output subfolder exists
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_file)


    save_log(os.path.join(output_folder, "logs.txt"),f"Opening pdf file: {pdf_file}")
    
    # List to store the filenames of the images for each page
    page_images = []

    # String to store the summary for each page
    total_summary = ""
    test_summary = ""
    
    # Iterate through each page of the PDF
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)
        
        # Set the zoom factor for higher resolution
        mat = fitz.Matrix(zoom, zoom)
        
        # Convert page to image
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save image as JPEG
        image_filename = os.path.join(subfolder, f"page_{page_num + 1}.jpg")
        img.save(image_filename, "JPEG")
        page_images.append(image_filename)
        # print(f"Page {page_num + 1} of {pdf_file} saved as {image_filename}")
        print(image_filename)

        save_log(os.path.join(output_folder, "logs.txt"),f"Page {page_num + 1} of {pdf_file} extracted")

        save_log(os.path.join(output_folder, "logs.txt"),f"Sending data to OpenAI GPT4o")
        # summary = get_summary_from_image(image_filename) ## summary text from gpt4o OCR
        save_log(os.path.join(output_folder, "logs.txt"),f"Received data from OpenAI GPT4o")

        summary = ""
        total_summary += summary + "\n"  # Add newline between summaries
    
    # Close the PDF file
    pdf_document.close()

    # Call the function to read and print the content of custom_prompt.txt
    custom_prompt = read_custom_prompt("dynamic/txt/custom_prompt.txt")

    pattern = r'\[(.*?)\]'
    matches_list = re.findall(pattern, custom_prompt)
    # print(matches_list)

    # Filter out "y1" and "y2" from matches_list
    matches_list = [match for match in matches_list if match not in ["y1", "y2"]]   

    # Initialize summary_dict based on matches_list
    summary_dict = {match: "" for match in matches_list}
    # print(summary_dict)

    # summary_dict = {
    #     'maid_name': '',
    #     'maid_ref_code': '',
    #     'maid_type_option_id': '',
    #     'maid_agency': '',
    #     'availability_status_id': '',
    #     'nationality_id': '',
    #     'birth_place': '',
    #     'siblings_count': '',
    #     'children_count': '',
    #     'children_ages': '',
    #     'Height': '150 cm',
    #     'Weight': '50 kg',
    #     'rest_day': '',
    #     'religion_id': '',
    #     'marital_status_id': '',
    #     'education_id': '',
    #     'education_info': '',
    #     'maid_current_salary': '',
    #     'maid_current_rest_day_id': '',
    #     'maid_preferred_rest_day_id': '',
    #     'home_address': '',
    #     'home_number': '',
    #     'home_contacts': '',
    #     'repatriate': '',
    #     'maid_passport_number': '',
    #     'maid_passport_expiry': '',
    #     'maid_work_permit_number': '',
    #     'maid_work_permit_expiry': '',
    #     'is_youtube_video': '',
    #     'youtube_link': '',
    #     'Language-English-Experience': '',
    #     'Language-English-stars': '',
    #     'languages_observations': '',
    #     'Expertise-Care for Infant|Children-Experience â€“ Willing?': '',
    #     'Expertise-Care for Infant|Children-Experience': '',
    #     'Expertise-Care for Infant|Children-stars': '',
    #     'Expertise-Care for Elderly-Experience â€“ Willing?': '',
    #     'Expertise-Care for Elderly-Experience': '',
    #     'Expertise-Care for Elderly-stars': '',
    #     'Expertise-Care for Disabled-Experience â€“ Willing?': '',
    #     'Expertise-Care for Disabled-Experience': '',
    #     'Expertise-Care for Disabled-stars': '',
    #     'Expertise-General Housework-Experience â€“ Willing?': '',
    #     'Expertise-General Housework-Experience': '',
    #     'Expertise-General Housework-stars': '',
    #     'Expertise-Cooking-Experience â€“ Willing?': '',
    #     'Expertise-Cooking-Experience': '',
    #     'Expertise-Cooking-stars': '',
    #     'skills_observations': '',
    #     'AdditionalInfo-Able to handle pork?': '',
    #     'AdditionalInfo-Able to eat pork?': '',
    #     'AdditionalInfo-Able to handle beef?': '',
    #     'AdditionalInfo-Able to care dog|cat?': '',
    #     'AdditionalInfo-Able to do gardening work?': '',
    #     'AdditionalInfo-Able to do simple sewing?': '',
    #     'AdditionalInfo-Willing to wash car?': '',
    #     'Experience-Singaporean-Experience': '',
    #     'maid_introduction': '',
    #     'maid_employment_history': '',
    #     'maid_status': '',
    #     'employment_status_id': '',
    #     'Language-Mandarin|Chinese-Dialect-Experience': '',
    #     'Language-Mandarin|Chinese-Dialect-stars': '',
    #     'Experience-Others-Experience': '',
    #     'Experience-Malaysian-Experience': ''
    # }


    if custom_prompt not in ["Not Found", "Read Error"]:

        total_summary += custom_prompt + "\n"

        save_log(os.path.join(output_folder, "logs.txt"),f"Sending data to OpenAI GPT3.5")
        # summary_text = get_summary_from_text(total_summary) ## summary text from gpt3.5
        save_log(os.path.join(output_folder, "logs.txt"),f"Received data from OpenAI GPT3.5")

        summary_text = """
        - [Name]: Tacac Annie Magtortor
        - [Date of Birth]: May 27, 1981
        - [Age]: 42
        - [Place of Birth]: LupaGan Clarin Misam
        - [Weight]: 50 kg
        - [Height]: 150 cm
        - [Nationality]: Filipino
        - [Residential Address in Home Country]: Ilagan Isabela
        - [Repatriation Port/Airport]: Cauayan City
        - [Religion]: Catholic
        - [Education Level]: High School (10-12 years)
        - [Number of Siblings]: 4
        - [Marital Status]: Married
        - [Number of Children]: 1
        """


        # Extracting values and updating summary_dict
        pattern = r'\[(.*?)\]:\s*(.*)'
        matches = re.findall(pattern, summary_text)

        for key, value in matches:
            if key in summary_dict:
                summary_dict[key] = value.strip()

        # Creating values_array based on summary_dict
        values_array = []
        for key in summary_dict:
            if summary_dict[key] == '':
                values_array.append(' ')
            else:
                values_array.append(summary_dict[key])

        # Print the updated summary_dict and values_array
        # print(summary_dict)
        # print(values_array)

        save_log(os.path.join(output_folder, "logs.txt"),f"Appending data to output.csv")
        csv_path = 'output_csv/output.csv'
        save_csv(csv_path, matches_list, values_array)

    # Print the list of page image filenames
    # print(f"List of page images for {pdf_file}: {page_images}")

    ## Write total_summary
    with open(os.path.join(output_folder, "ocr_results_plus_prompt.txt"), "a", encoding="utf-8") as text_file:
        text_file.write(f"[start]{base_name}----------------------------------------------------------")
        text_file.write(total_summary)
        text_file.write(f"\n[end]..{base_name}----------------------------------------------------------\n")

    with open(os.path.join(output_folder, "summary_text_from_gpt35.txt"), "a", encoding="utf-8") as text_file:
        text_file.write(f"[start]{base_name}----------------------------------------------------------")
        text_file.write(summary_text)
        text_file.write(f"\n[end]..{base_name}----------------------------------------------------------\n")
    
    # save_log(os.path.join(output_folder, "logs.txt"),"hello")

    return page_images

####### PDF to profile Picture Extraction #######
# Function to extract images with faces from a specific PDF file
def extract_images_with_faces(pdf_path):
    # Get the base name of the PDF file
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    # Create the main folder if it doesn't exist
    main_folder = "extracted_images"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    extracted_images = []

    pdf_document = fitz.open(pdf_path)

    # Extract images from the first page only
    page_number = 0
    page = pdf_document[page_number]
    image_list = page.get_images(full=True)
    face_found = False  # Flag to track if a face has been found on the first page
    for image_index, img in enumerate(image_list):
        xref = img[0]
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]
        image_pil = Image.open(io.BytesIO(image_bytes))
        image_cv2 = cv2.cvtColor(cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(image_cv2, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) > 0 and not face_found:
            # If a face is detected and no face has been found yet on the first page
            face_found = True
            # Save the image in the main folder with the PDF base name as the image name
            image_filename = f"{pdf_basename}_{image_index + 1}.jpg"  # Naming based on image index
            image_pil.save(os.path.join(main_folder, image_filename), "JPEG")
            extracted_images.append(image_pil)
            break  # Stop processing further images on the first page once a face is found

    pdf_document.close()

    return extracted_images


# Load the pre-trained face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to process a specific PDF file in the "uploads" folder
def process_pdf_extract_image(filename):
    global EXTRACTED_PAGE_IMAGES_FOLDER

    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(pdf_path) and pdf_path.endswith(".pdf"):
        extracted_images = extract_images_with_faces(pdf_path)
        print(f"Processed {pdf_path}: {len(extracted_images)} images extracted with faces")
        save_log(os.path.join(EXTRACTED_PAGE_IMAGES_FOLDER, "logs.txt"),f"Processed {pdf_path}: {len(extracted_images)} images extracted with faces")

    else:
        print(f"File '{filename}' not found or is not a PDF.")
        save_log(os.path.join(EXTRACTED_PAGE_IMAGES_FOLDER, "logs.txt"),f"File '{filename}' not found or is not a PDF.")
     


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            return redirect(url_for('home_page'))
        else:
            return render_template('login/login.html', error='Invalid credentials')
    return render_template('login/login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Home route (secured)
@app.route('/')
@app.route('/home')
@login_required
def home_page():
    if not check_authenticated():
        return redirect(url_for('login'))
    # Check if the 'uploads' folder exists before attempting to delete files
    if os.path.exists(UPLOAD_FOLDER):
        # Delete all files inside the 'uploads' folder
        for file_name in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Delete all files inside the 'extracted_images' folder
        for file_name in os.listdir(EXTRACTED_PROFILE_PICTURE_FOLDER):
            file_path = os.path.join(EXTRACTED_PROFILE_PICTURE_FOLDER, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Delete all files inside the 'output_pdf2images' folder
        for file_name in os.listdir(EXTRACTED_PAGE_IMAGES_FOLDER):
            file_path = os.path.join(EXTRACTED_PAGE_IMAGES_FOLDER, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Delete output.csv file if it exists
        output_csv_path = os.path.join(GENERATE_CSV_FOLDER, 'output.csv')
        if os.path.exists(output_csv_path):
            os.remove(output_csv_path)

        return render_template('home/home-page.html')
    else:
        return render_template('home/home-page.html')  # Or redirect to another page if the folder doesn't exist

# Secure routes
@app.route('/upload', methods=['POST'])
@login_required
def upload_files():
    if not check_authenticated():
        return jsonify({'error': 'Unauthorized access'}), 401
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400
    
    uploaded_files = []
    session_id = str(os.urandom(16).hex())
    progress[session_id] = {'current': 0, 'total': len(files)}  # Initialize progress

    for file in files:
        if file and file.filename:
            filename = file.filename
            fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullpath)
            uploaded_files.append(filename)
    
    response = {
        'message': 'Files successfully uploaded',
        'files': uploaded_files,
        'session_id': session_id
    }
    return jsonify(response), 200


@app.route('/process/<session_id>', methods=['POST'])
@login_required
def process_files(session_id):
    if not check_authenticated():
        return jsonify({'error': 'Unauthorized access'}), 401
    def mock_processing():
        uploaded_files = os.listdir(UPLOAD_FOLDER)
        total_files = len(uploaded_files)
        progress[session_id]['total'] = total_files

        for index, filename in enumerate(uploaded_files):
            # Simulate processing of each file
            time.sleep(3)  # Simulate processing delay
            process_pdf_extract_image(filename)
            pdf_path = os.path.join(UPLOAD_FOLDER, filename)
            pdf_to_jpg(pdf_path, EXTRACTED_PAGE_IMAGES_FOLDER, zoom=2)
            progress[session_id]['current'] = index + 1

        save_log(os.path.join(EXTRACTED_PAGE_IMAGES_FOLDER, "logs.txt"),f"Processed Completed. Ready to download!")

    if session_id not in progress:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    # Start the mock processing in a separate thread
    thread = Thread(target=mock_processing)
    thread.start()
    
    return jsonify({'message': 'Processing started'}), 200

@app.route('/status')
@login_required
def status_page():
    if not check_authenticated():
        return redirect(url_for('login'))
    return render_template('status/status-page.html')

processing_threads = {}  # Initialize an empty dictionary to keep track of processing threads

@app.route('/progress/<session_id>')
def progress_status(session_id):
    if not check_authenticated():
        return jsonify({'error': 'Unauthorized access'}), 401
    if session_id in progress:
        return jsonify(progress[session_id]), 200
    else:
        return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/cancel/<session_id>', methods=['POST'])
@login_required
def cancel_processing(session_id):
    if session_id in processing_threads:
        del processing_threads[session_id]  # Stop the processing
        # Additional cleanup if necessary
        return jsonify({'message': 'Processing cancelled'})
    return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/download/<session_id>')
@login_required
def download_files(session_id):
    if not check_authenticated():
        return jsonify({'error': 'Unauthorized access'}), 401
    if session_id not in progress or progress[session_id]['current'] < progress[session_id]['total']:
        return jsonify({'error': 'Files are still being processed or invalid session ID'}), 400

    zip_filename = f"profile_pictures_{session_id}.zip"
    zip_filepath = os.path.join(app.config['EXTRACTED_PROFILE_PICTURE_FOLDER'], zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(app.config['EXTRACTED_PROFILE_PICTURE_FOLDER']):
            for file in files:
                file_path = os.path.join(root, file)
                # Exclude the zip file itself from being added
                if file_path != zip_filepath:
                    arcname = os.path.relpath(file_path, app.config['EXTRACTED_PROFILE_PICTURE_FOLDER'])
                    zipf.write(file_path, arcname)

    return send_file(zip_filepath, as_attachment=True)

@app.route('/download-csv/<session_id>')
@login_required
def download_csv(session_id):
    if not check_authenticated():
        return jsonify({'error': 'Unauthorized access'}), 401
    csv_filepath = 'output_csv/output.csv'

    if os.path.exists(csv_filepath):
        return send_file(csv_filepath, as_attachment=True)
    else:
        return jsonify({'error': 'output.csv not found'}), 404


@app.route('/custom-prompt', methods=['GET', 'POST'])
@login_required
def text_editor():
    if request.method == 'POST':
        # Handle form submission if needed
        pass

    custom_prompt_file = 'dynamic/txt/custom_prompt.txt'
    default_content = ''
    
    # Read the content of custom_prompt.txt if it exists
    if os.path.exists(custom_prompt_file):
        with open(custom_prompt_file, 'r', encoding='utf-8') as f:
            default_content = f.read()
    
    return render_template('custom/custom-prompt-page.html', default_content=default_content)


@app.route('/save-content', methods=['POST'])
@login_required
def save_content():
    content = request.form.get('content')

    if content.strip():  # Check if content is not empty or whitespace
        custom_prompt_file = 'dynamic/txt/custom_prompt.txt'
        with open(custom_prompt_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'Saved Successfully'}), 200
    else:
        return jsonify({'error': 'Content is empty'}), 400

@app.route('/download-template')
@login_required
def download_template():
    template_file = 'static/txt/custom_prompt_template.txt'
    return send_file(template_file, as_attachment=True)


@app.route('/settings')
@login_required  # Ensure only authenticated users can access settings
def settings_page():
    if not check_authenticated():
        return redirect(url_for('login'))
    return render_template('settings/settings-page.html')


# Endpoint to handle toggle OCR settings
@app.route('/toggle-ocr/<setting>', methods=['POST'])
@login_required
def toggle_ocr_setting(setting):
    global current_ocr  # Access the global variable
    
    if setting in ['gpt4o', 'tesseract', 'keras']:
        # Set the current OCR setting based on the URL parameter
        if setting == 'gpt4o':
            current_ocr = "gpt4oOCR"
        elif setting == 'tesseract':
            current_ocr = "tesseractOCR"
        elif setting == 'keras':
            current_ocr = "kerasOCR"
        
        # Print the current value of current_ocr
        print(f"Current OCR setting: {current_ocr}")

        return jsonify({'message': f'Successfully set {setting} OCR setting'}), 200
    else:
        return jsonify({'error': 'Invalid OCR setting'}), 400

# Route to retrieve current OCR setting
@app.route('/current-ocr', methods=['GET'])
def get_current_ocr():
    global current_ocr
    return jsonify({'current_ocr': current_ocr})


@app.route('/download-gpt/<session_id>')
def download_gpt(session_id):
    # Replace with actual path to summary_text_from_gpt35.txt
    filepath = 'output_pdf2images/summary_text_from_gpt35.txt'
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'})

@app.route('/download-ocr/<session_id>')
def download_ocr(session_id):
    # Replace with actual path to ocr_results_plus_prompt.txt
    filepath = 'output_pdf2images/ocr_results_plus_prompt.txt'
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'})

# Route to fetch logs content
@app.route('/fetch-logs/<session_id>')
def fetch_logs(session_id):
    # Logic to read and return logs.txt content
    try:
        with open('output_pdf2images/logs.txt', 'r') as file:
            logs_content = file.read()
        return logs_content
    except Exception as e:
        return str(e), 500  # Return error message and HTTP status code 500 for server error


@app.route('/save-csv')
@login_required
def save_outputcsv():
    
    save_csv(csv_path,"hello word")
    return "success"


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
