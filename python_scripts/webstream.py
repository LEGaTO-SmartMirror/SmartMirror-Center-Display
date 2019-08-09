# camera.py

import cv2

IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920


try:
	IMAGE_HEIGHT = int(sys.argv[1][0])
	IMAGE_WIDTH = int(sys.argv[1][1])
except:
	print("using default image size")


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture("shmsrc socket-path=/dev/shm/center_display ! video/x-raw, format=BGR ,height=" + str(IMAGE_HEIGHT) + ", width=" + str(IMAGE_WIDTH) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        #rescaled_image = image
        #rescaled_image = cv2.resize(image,(IMAGE_WIDTH,IMAGE_HEIGHT))
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
# main.py

from flask import Flask, render_template, Response
#from camera import VideoCamera

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5003, debug=False)
