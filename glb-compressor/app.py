import os
import subprocess
from flask import Flask, request, redirect, url_for, send_from_directory, render_template

app = Flask(__name__)

# Folders for uploads and compressed files
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.glb'):
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"compressed_{file.filename}")
        file.save(input_path)

        # Compress using gltf-pipeline
        try:
            subprocess.run(
                ['gltf-pipeline', '-i', input_path, '-o', output_path, '--draco.compressMeshes'],
                check=True
            )
        except subprocess.CalledProcessError:
            return "Compression failed. Ensure gltf-pipeline is installed.", 500

        # Ensure compressed file size is under 50MB
        if os.path.getsize(output_path) > 50 * 1024 * 1024:
            return "Compressed file size exceeds 50MB. Try optimizing the input further.", 400

        return redirect(url_for('download_file', filename=f"compressed_{file.filename}"))
    else:
        return "Invalid file type. Please upload a .glb file.", 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
