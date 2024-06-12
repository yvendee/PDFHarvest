from flask import Flask, request, Blueprint, render_template, jsonify
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
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400
    
    uploaded_files = []
    for file in files:
        if file and file.filename:
            filename = file.filename
            fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullpath)
            # uploaded_files.append(filename)
            uploaded_files.append(fullpath)
    print(uploaded_files)


    
    response = {
        'message': 'Files successfully uploaded'
        # 'files': uploaded_files
    }
    return jsonify(response), 200


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
