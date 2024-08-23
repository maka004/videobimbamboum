# app.py
import json
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file
import requests
from werkzeug.utils import secure_filename
import os
import ffmpeg
from scipy.spatial import distance


def create_app():
    app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
    app.config['UPLOAD_FOLDER'] = '/app/uploads/'
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    # Other setup code...
    return app


app = create_app()


@app.route('/', methods=['GET'])
def homepage():
    return "Homepage"


@app.route('/hello', methods=['GET'])
def hello():
    return "Hello"

from moviepy.editor import VideoFileClip

@app.route('/video_length', methods=['POST'])
def video_length():
    video_url = request.get_json()['url']
    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to download file'}), 400

    filename = secure_filename(video_url.split('/')[-1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    video = VideoFileClip(file_path)
    duration = video.duration  # Duration in seconds

    return jsonify({'video_length': duration})

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import blackwhite
import os
import requests

app = Flask(__name__)

# Ensure this folder exists and is writable
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/black_and_white', methods=['POST'])
def black_and_white():
    try:
        # Extract URL from request
        data = request.get_json()
        if 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        video_url = data['url']
        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to download file'}), 400

        # Save the file locally
        filename = secure_filename(video_url.split('/')[-1])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Process the video to black and white
        video = VideoFileClip(file_path)
        bw_video = blackwhite(video)
        bw_filename = 'bw_' + filename
        bw_file_path = os.path.join(app.config['UPLOAD_FOLDER'], bw_filename)
        bw_video.write_videofile(bw_file_path)

        # Construct the URL to return
        bw_url = request.url_root + 'uploads/' + bw_filename

        # Clean up original file
        video.close()
        os.remove(file_path)

        return jsonify({'bw_video_url': bw_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to serve the processed video file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)






@app.route('/trim_video', methods=['POST'])
def trim_video():
    data = request.get_json()
    video_url = data['url']
    trim_seconds = int(data['seconds'])

    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to download file'}), 400

    filename = secure_filename(video_url.split('/')[-1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    video = VideoFileClip(file_path)
    trimmed_video = video.subclip(trim_seconds, video.duration)
    trimmed_filename = 'trimmed_' + filename
    trimmed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], trimmed_filename)
    trimmed_video.write_videofile(trimmed_file_path)

    trimmed_url = request.url_root + 'uploads/' + trimmed_filename

    return jsonify({'trimmed_video_url': trimmed_url})

@app.route('/get_similar', methods=['POST'])
def get_similar():
    data = request.json
    query_vector = data['query_vector']
    vector_text_pairs = data['vectors']

    # Extract embeddings and their corresponding texts
    vectors = []
    for pair in vector_text_pairs:
        if isinstance(pair['embedding'], str):
            vectors.append(json.loads(pair['embedding']))
        else:
            vectors.append(pair['embedding'])
    texts = [pair['text'] for pair in vector_text_pairs]

    # Calculate cosine similarity for each vector
    # Return the index of the most similar vector
    most_similar_index = max(range(len(vectors)), key=lambda index: 1 - distance.cosine(query_vector, vectors[index]))

    return jsonify({'most_similar_text': texts[most_similar_index]})
