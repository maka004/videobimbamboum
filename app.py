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

from pydub import AudioSegment, silence
from moviepy.editor import concatenate_videoclips

@app.route('/remove_silence', methods=['POST'])
def remove_silence():
    video_url = request.get_json()['url']
    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to download file'}), 400

    filename = secure_filename(video_url.split('/')[-1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    video = VideoFileClip(file_path)
    audio_filename = str(uuid.uuid4()) + '.wav'  
    audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
    video.audio.write_audiofile(audio_file_path)

    sound = AudioSegment.from_file(audio_file_path, format="wav")
    non_silence_intervals = silence.detect_nonsilent(sound, min_silence_len=1000, silence_thresh=-32)
    
    # Convert milliseconds to seconds for subclip
    video_parts = [video.subclip(max(0, start/1000.0), min(len(sound)/1000.0, end/1000.0)) for start, end in non_silence_intervals]
    final_clip = concatenate_videoclips(video_parts)

    final_filename = 'ns_' + filename
    final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
    final_clip.write_videofile(final_file_path)

    final_video_url = request.url_root + app.config['UPLOAD_FOLDER'] + final_filename

    return jsonify({'ns_video_url': final_video_url})

