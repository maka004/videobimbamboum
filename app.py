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
import requests
import polyline
from geopy.distance import geodesic

def get_directions(api_key, origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def decode_polyline(polyline_str):
    return polyline.decode(polyline_str)

def get_waypoints(route_points, interval_km=0.5):
    waypoints = []
    accumulated_distance = 0.0
    waypoints.append(route_points[0])  # Start point
    
    for i in range(1, len(route_points)):
        start_point = route_points[i - 1]
        end_point = route_points[i]
        segment_distance = geodesic(start_point, end_point).km
        
        while accumulated_distance + segment_distance >= interval_km:
            fraction = (interval_km - accumulated_distance) / segment_distance
            waypoint_lat = start_point[0] + fraction * (end_point[0] - start_point[0])
            waypoint_lng = start_point[1] + fraction * (end_point[1] - start_point[1])
            waypoints.append((waypoint_lat, waypoint_lng))
            accumulated_distance = 0.0
            start_point = (waypoint_lat, waypoint_lng)
            segment_distance = geodesic(start_point, end_point).km
            
        accumulated_distance += segment_distance
    
    return waypoints

def main():
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"
    origin = "origin_latitude,origin_longitude"
    destination = "destination_latitude,destination_longitude"
    
    directions_data = get_directions(api_key, origin, destination)
    if directions_data and directions_data['status'] == 'OK':
        route = directions_data['routes'][0]
        polyline_str = route['overview_polyline']['points']
        route_points = decode_polyline(polyline_str)
        waypoints = get_waypoints(route_points)
        print("Waypoints at 0.5 km intervals:")
        for waypoint in waypoints:
            print(waypoint)
    else:
        print("Error fetching directions")

if __name__ == "__main__":
    main()
