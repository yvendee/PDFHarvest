from flask import Flask, request, Blueprint, render_template, redirect, url_for
import os

app = Flask(__name__)
apps = Blueprint('apps', __name__, template_folder='templates', static_folder='static')

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

@app.route('/')
def calendar():
    return render_template('home/home-page.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No files part in the request', 400
    files = request.files.getlist('files')
    if not files:
        return 'No files selected for uploading', 400
    for file in files:
        if file and file.filename:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return 'Files successfully uploaded', 200

@app.before_request
def log_request_info():
    print(f'Request URL: {request.url}')
    print(f'Request Method: {request.method}')
    print(f'Request Headers: {request.headers}')
    print(f'Request Body: {request.get_data()}')

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
