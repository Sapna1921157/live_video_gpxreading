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

# Stream live video
def gen():
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
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Simulate GPX data processing from the live video (replace with actual logic)
@app.route('/gpx_data', methods=['GET'])
def gpx_data():
    # Example logic to generate GPX data (replace with actual processing code)
    gpx_data = {
        'latitude': round(random.uniform(-90, 90), 5),
        'longitude': round(random.uniform(-180, 180), 5),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    return jsonify(gpx_data)

if __name__ == '__main__':
    app.run(debug=True)
