from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import blackwhite
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = '/app/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def homepage():
    return "Homepage"

@app.route('/video_length', methods=['POST'])
def video_length():
    try:
        data = request.get_json()
        if 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        video_url = data['url']
        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to download file'}), 400

        filename = secure_filename(video_url.split('/')[-1])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        video = VideoFileClip(file_path)
        duration = video.duration
        video.close()
        os.remove(file_path)

        return jsonify({'video_length': duration})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trim_video', methods=['POST'])
def trim_video():
    try:
        data = request.get_json()
        if 'url' not in data or 'start_time' not in data or 'end_time' not in data:
            return jsonify({'error': 'Missing parameters'}), 400

        video_url = data['url']
        start_time = data['start_time']
        end_time = data['end_time']

        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to download file'}), 400

        filename = secure_filename(video_url.split('/')[-1])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        video = VideoFileClip(file_path)
        trimmed_video = video.subclip(start_time, end_time)
        trimmed_filename = 'trimmed_' + filename
        trimmed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], trimmed_filename)
        trimmed_video.write_videofile(trimmed_file_path)

        trimmed_url = request.url_root + 'uploads/' + trimmed_filename

        video.close()
        os.remove(file_path)

        return jsonify({'trimmed_video_url': trimmed_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/black_and_white', methods=['POST'])
def black_and_white():
    try:
        data = request.get_json()
        if 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        video_url = data['url']
        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to download file'}), 400

        filename = secure_filename(video_url.split('/')[-1])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        video = VideoFileClip(file_path)
        bw_video = blackwhite(video)
        bw_filename = 'bw_' + filename
        bw_file_path = os.path.join(app.config['UPLOAD_FOLDER'], bw_filename)
        bw_video.write_videofile(bw_file_path)

        bw_url = request.url_root + 'uploads/' + bw_filename

        video.close()
        os.remove(file_path)

        return jsonify({'bw_video_url': bw_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
