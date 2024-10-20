from flask import Flask, render_template, Response, jsonify
import cv2
import time
import random

app = Flask(__name__)

# Placeholder for live video or camera feed
camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

# Generate bounding box data (latitude, longitude, timestamp)
def generate_gpx_data():
    # Example logic to generate GPX data (replace with actual processing code)
    return {
        'latitude': round(random.uniform(-90, 90), 5),
        'longitude': round(random.uniform(-180, 180), 5),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

# Stream live video with bounding box and GPX data
def gen():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Get GPX data
            gpx_data = generate_gpx_data()
            latitude = gpx_data['latitude']
            longitude = gpx_data['longitude']
            timestamp = gpx_data['timestamp']

            # Draw a bounding box on the frame
            start_point = (50, 50)
            end_point = (400, 200)
            color = (0, 255, 0)  # Green color in BGR
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness)

            # Display GPX data within the bounding box
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_color = (255, 255, 255)  # White color for text
            line_type = 2

            # Add latitude, longitude, and timestamp text inside the bounding box
            cv2.putText(frame, f'Lat: {latitude}', (60, 80), font, font_scale, font_color, line_type)
            cv2.putText(frame, f'Lon: {longitude}', (60, 110), font, font_scale, font_color, line_type)
            cv2.putText(frame, f'Time: {timestamp}', (60, 140), font, font_scale, font_color, line_type)

            # Encode the frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Simulate GPX data processing from the live video (replace with actual logic)
@app.route('/gpx_data', methods=['GET'])
def gpx_data():
    # Generate GPX data
    gpx_data = generate_gpx_data()
    return jsonify(gpx_data)

if __name__ == '__main__':
    app.run(debug=True)
