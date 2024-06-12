from flask import Flask, request, Blueprint, render_template, jsonify, session, redirect, url_for, send_file
import os
import time
from threading import Thread
import zipfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

apps = Blueprint('apps', __name__, template_folder='templates', static_folder='static')

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

progress = {}

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

    zip_filename = f"{session_id}_files.zip"
    zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename != zip_filename:  # Exclude the zip file itself
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                zipf.write(file_path, filename)

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
