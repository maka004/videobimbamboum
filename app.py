# app.py
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file
import requests
from werkzeug.utils import secure_filename
import os
import ffmpeg


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

from moviepy.video.fx.all import blackwhite

@app.route('/black_and_white', methods=['POST'])
def black_and_white():
    video_url = request.get_json()['url']
    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to download file'}), 400

    filename = secure_filename(video_url.split('/')[-1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    video = VideoFileClip(file_path)
    bw_video = blackwhite(video)
    bw_filename = 'bw_' + filename
    bw_file_path = os.path.join(app.config['UPLOAD_FOLDER'], bw_filename)
    bw_video.write_videofile(bw_file_path)

    bw_url = request.url_root + '/uploads/' + bw_filename

    return jsonify({'bw_video_url': bw_url})

@app.route('/remove_first_5_seconds', methods=['POST'])
def remove_first_5_seconds():
    video_url = request.get_json()['url']
    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to download file'}), 400

    filename = secure_filename(video_url.split('/')[-1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    video = VideoFileClip(file_path)
    if video.duration < 5.0:
        return jsonify({'error': 'Video is less than 5 seconds long'}), 400

    modified_video = video.subclip(5, None)  # Start at 5 seconds, end at original end
    modified_filename = 'modified_' + filename
    modified_file_path = os.path.join(app.config['UPLOAD_FOLDER'], modified_filename)
    modified_video.write_videofile(modified_file_path)

    modified_url = request.url_root + app.config['UPLOAD_FOLDER'] + modified_filename

    return jsonify({'modified_video_url': modified_url})

