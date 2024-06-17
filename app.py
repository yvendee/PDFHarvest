from flask import Flask, request, Blueprint, render_template, jsonify, session, redirect, url_for, send_file
import os
import time
from threading import Thread
import zipfile
import shutil

# import os
import io
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

apps = Blueprint('apps', __name__, template_folder='templates', static_folder='static')

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
EXTRACTED_PROFILE_PICTURE_FOLDER = 'extracted_images'
EXTRACTED_PAGE_IMAGES_FOLDER = 'output_pdf2images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_PROFILE_PICTURE_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_PAGE_IMAGES_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXTRACTED_PROFILE_PICTURE_FOLDER'] = EXTRACTED_PROFILE_PICTURE_FOLDER
app.config['EXTRACTED_PAGE_IMAGES_FOLDER'] = EXTRACTED_PAGE_IMAGES_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

progress = {}

####### PDF to Images Extraction ################
def pdf_to_jpg(pdf_file, output_folder, zoom=2):
    # Get the base name of the PDF file to create a subfolder
    base_name = os.path.splitext(os.path.basename(pdf_file))[0]
    subfolder = os.path.join(output_folder, base_name)
    
    # Ensure the output subfolder exists
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_file)
    
    # List to store the filenames of the images for each page
    page_images = []
    
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
        print(f"Page {page_num + 1} of {pdf_file} saved as {image_filename}")
    
    # Close the PDF file
    pdf_document.close()
    
    # Print the list of page image filenames
    print(f"List of page images for {pdf_file}: {page_images}")
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
    # Create the images folder with the PDF base name inside the main folder
    images_folder = os.path.join(main_folder, f"{pdf_basename}_extracted")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

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
            # Save the image in the images folder with a fixed name "image.jpg"
            image_pil.save(os.path.join(images_folder, "image.jpg"), "JPEG")
            extracted_images.append(image_pil)
            break  # Stop processing further images on the first page once a face is found

    pdf_document.close()

    return extracted_images


# Load the pre-trained face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to process a specific PDF file in the "uploads" folder
def process_pdf_extract_image(filename):
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(pdf_path) and pdf_path.endswith(".pdf"):
        extracted_images = extract_images_with_faces(pdf_path)
        print(f"Processed {pdf_path}: {len(extracted_images)} images extracted with faces")
    else:
        print(f"File '{filename}' not found or is not a PDF.")


@app.route('/')
@app.route('/home')
def home_page():
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

        return render_template('home/home-page.html')
    else:
        return render_template('home/home-page.html')  # Or redirect to another page if the folder doesn't exist


@app.route('/upload', methods=['POST'])
def upload_files():
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
def process_files(session_id):
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

    if session_id not in progress:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    # Start the mock processing in a separate thread
    thread = Thread(target=mock_processing)
    thread.start()
    
    return jsonify({'message': 'Processing started'}), 200

@app.route('/status')
def status_page():
    return render_template('status/status-page.html')

@app.route('/progress/<session_id>')
def progress_status(session_id):
    if session_id in progress:
        return jsonify(progress[session_id]), 200
    else:
        return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/download/<session_id>')
def download_files(session_id):
    if session_id not in progress or progress[session_id]['current'] < progress[session_id]['total']:
        return jsonify({'error': 'Files are still being processed or invalid session ID'}), 400

    # zip_filename = f"{session_id}_files.zip"
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

# @app.before_request
# def log_request_info():
#     print(f'Request URL: {request.url}')
#     print(f'Request Method: {request.method}')
#     print(f'Request Headers: {request.headers}')
#     print(f'Request Body: {request.get_data()}')


@app.route('/sendData', methods=['POST'])
def log_post_request():
    data = request.get_json()
    print(data)
    with open('log.txt', 'a') as f:
        f.write(str(data) + '\n')
    return 'Received and logged the POST request successfully!', 200

if __name__ == '__main__':
    app.register_blueprint(apps)
    app.run(debug=True)
