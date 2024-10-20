from flask import Flask, render_template, Response, jsonify
import cv2
import time
import random
import json

app = Flask(__name__)

# Placeholder for live video or camera feed
camera = None  # Initialize camera as None

# File to store GPX data
gpx_data_file = 'gpx_data.json'

# Function to save GPX data to a JSON file
def save_gpx_data(gpx_data):
    with open(gpx_data_file, 'w') as f:
        json.dump(gpx_data, f, indent=4)

# Function to generate random GPX data
def generate_gpx_data():
    gpx_data = {
        'latitude': round(random.uniform(-90, 90), 5),
        'longitude': round(random.uniform(-180, 180), 5),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    save_gpx_data(gpx_data)  # Save GPX data to a file
    return gpx_data

@app.route('/')
def index():
    return render_template('index.html')

def init_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)

# Stream live video (first panel)
def gen_original_video():
    init_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_original_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Stream live video with bounding box and GPX data (second panel)
def gen_video_with_bounding_box():
    init_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gpx_data = generate_gpx_data()
            latitude = gpx_data['latitude']
            longitude = gpx_data['longitude']
            timestamp = gpx_data['timestamp']

            start_point = (50, 50)
            end_point = (400, 200)
            color = (0, 255, 0)
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_color = (255, 255, 255)
            line_type = 2

            cv2.putText(frame, f'Lat: {latitude}', (60, 80), font, font_scale, font_color, line_type)
            cv2.putText(frame, f'Lon: {longitude}', (60, 110), font, font_scale, font_color, line_type)
            cv2.putText(frame, f'Time: {timestamp}', (60, 140), font, font_scale, font_color, line_type)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed_with_box')
def video_feed_with_box():
    return Response(gen_video_with_bounding_box(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/gpx_data', methods=['GET'])
def gpx_data():
    try:
        with open(gpx_data_file, 'r') as f:
            gpx_data = json.load(f)
    except FileNotFoundError:
        gpx_data = {}
    return jsonify(gpx_data)

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera
    if camera is not None:
        camera.release()  # Close the camera
        camera = None  # Reset camera variable
    return jsonify({"message": "Camera stopped."})

if __name__ == '__main__':
    app.run(debug=True)
