# camera.py

import cv2
import numpy as np
from threading import Thread
import time
import os, sys
import subprocess
import signal
import json

show_face_captions = False
show_obj_captions = False
show_gest_captions = False
show_camera = False
show_camera_1m = False
show_style_transfer = False

recognition_dict = {}
module_FPS = {}



if os.path.exists("/tmp/center_display") is True:
	os.remove("/tmp/center_display")

out = cv2.VideoWriter ('appsrc ! shmsink socket-path=/tmp/center_display sync=true wait-for-connection=false shm-size=100000000',0, 30, (1080,1920), True)



out.write(np.zeros((1920,1080,3), np.uint8))
out.write(np.zeros((1920,1080,3), np.uint8))

def to_node(type, message):
	# convert to json and print (node helper will read from stdout)
	try:
		print(json.dumps({type: message}))
	except Exception:
		pass
	# stdout has to be flushed manually to prevent delays in the node helper communication
	sys.stdout.flush()

to_node("status", 'Buffer initalized.. starting')

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def check_stdin():
	global show_face_captions
	global show_obj_captions
	global show_gest_captions
	global show_camera
	global show_camera_1m
	global show_style_transfer
	global recognition_dict
	global module_FPS
	
	while True:
		lines = sys.stdin.readline()
		
		data = json.loads(lines)
		if 'SET' in data:
			setting = data['SET']
			to_node("status", "Changing: " + setting)
			if setting == 'TOGGLE':
				show_camera = not show_camera
				show_style_transfer = False
			elif setting == 'DISTANCE':
				show_camera_1m = not show_camera_1m
			elif setting == 'FACE':
				show_face_captions = not show_face_captions
			elif setting == 'OBJECT':
				show_obj_captions = not show_obj_captions
			elif setting == 'GESTURE':
				show_gest_captions = not show_gest_captions
			elif setting == 'STYLE_TRANSFERE':
				show_obj_captions = False
				show_face_captions = False
				show_gest_captions = False
				show_camera = False
				show_camera_1m = False
				show_style_transfer = not show_style_transfer
			elif setting == 'HIDEALL':
				show_obj_captions = False
				show_face_captions = False
				show_gest_captions = False
				show_camera = False
				show_camera_1m = False
				show_style_transfer = False
			elif setting == 'SHOWALL':
				show_obj_captions = True
				show_face_captions = True
				show_gest_captions = True
				show_camera = True
				show_camera_1m = False
				show_style_transfer = False
		elif 'DETECTED_FACES' in data:
			recognition_dict['DETECTED_FACES'] = data['DETECTED_FACES']
		elif 'DETECTED_GESTURES' in data:
			recognition_dict['DETECTED_GESTURES'] = data['DETECTED_GESTURES']
		elif 'DETECTED_OBJECTS' in data:
			recognition_dict['DETECTED_OBJECTS'] = data['DETECTED_OBJECTS']
		elif 'GESTURE_DET_FPS' in data:
			module_FPS['GESTURE_DET_FPS'] = data['GESTURE_DET_FPS']
		elif 'OBJECT_DET_FPS' in data:
			module_FPS['OBJECT_DET_FPS'] = data['OBJECT_DET_FPS']
		elif 'FACE_DET_FPS' in data:
			module_FPS['FACE_DET_FPS'] = data['FACE_DET_FPS']

			

t = Thread(target=check_stdin)
t.start()

#cv2.namedWindow("center image", cv2.WINDOW_NORMAL)

#print("Calling subprocess to open gst_rtsp_server")
#BASE_DIR = os.path.dirname(__file__) + '/'
BASE_DIR = os.path.dirname(__file__) + '/'
os.chdir(BASE_DIR)
#p = subprocess.Popen(['python', BASE_DIR + 'gst_rtsp_server.py'])
pp = subprocess.Popen(['python', 'webstream.py'])

time.sleep(2)


def shutdown(self, signum):
	to_node("status", 'Shutdown: Cleaning up camera...')
	os.remove("/tmp/center_display")
	pp.kill()
	video.release()
	video_1m.release()
	video_style_transfer.release()
	out.release()

	to_node("status", 'Shutdown: Done.')
	exit()

signal.signal(signal.SIGINT, shutdown)

image_gestures = {}
image_gestures["flat_right"] = cv2.imread('icons/flat_right.jpg')
image_gestures["flat_left"] = cv2.imread('icons/flat_left.jpg')
image_gestures["okay_right"] = cv2.imread('icons/okay_right.jpg')
image_gestures["okay_left"] = cv2.imread('icons/okay_left.jpg')
image_gestures["thumbs_up_right"] = cv2.imread('icons/thumbs_up_right.jpg')
image_gestures["thumbs_up_left"] = cv2.imread('icons/thumbs_up_left.jpg')
image_gestures["thumbs_down_right"] = cv2.imread('icons/thumbs_down_right.jpg')
image_gestures["thumbs_down_left"] = cv2.imread('icons/thumbs_down_left.jpg')

time.sleep(5)
 
video = cv2.VideoCapture("shmsrc socket-path=/tmp/camera_image ! video/x-raw, format=BGR ,height=1920,width=1080, framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_1m = cv2.VideoCapture("shmsrc socket-path=/tmp/camera_1m ! video/x-raw, format=BGR ,height=1920,width=1080, framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
#video_style_transfer = cv2.VideoCapture("shmsrc socket-path=/tmp/style_transfer is-live=true ! queue ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! queue ! appsink wait-on-eos=false drop=true", cv2.CAP_GSTREAMER)
video_style_transfer = cv2.VideoCapture("shmsrc socket-path=/tmp/style_transfer ! video/x-raw, format=BGR ,height=1920,width=1080, framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)


while video.isOpened() is False:
	to_node("status", 'video is not open')
	time.sleep(5)


while True:

	if show_camera is True:
		if show_camera_1m is True:
			ret, image = video_1m.read()
		else:
			ret, image = video.read()

	elif show_style_transfer is True:
			ret, image = video_style_transfer.read()
	else:
		image = np.zeros((1920,1080,3), np.uint8)

	
	imgUMat = cv2.UMat(image)

	if show_face_captions is True:
		if 'FACE_DET_FPS' in module_FPS:
			cv2.putText(imgUMat, str(module_FPS['FACE_DET_FPS']) + " FPS", (50, 50), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,55,55), thickness=3) 
		if 'DETECTED_FACES' in recognition_dict:
			for element in recognition_dict['DETECTED_FACES']:
				xmin, ymin, xmax, ymax = convertBack(float(element["center"][0] * 1080), float(element["center"][1] * 1920), float(element["w_h"][0] * 1080), float(element["w_h"][1] * 1920))
				pt1 = (xmin, ymin)
				pt2 = (xmax, ymax)
				cv2.rectangle(imgUMat, pt1, pt2, color=(255,55,55), thickness=2)
				cv2.putText(imgUMat, element["name"], (int(pt1[0] + 5), int(pt1[1] + 60)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,55,55), thickness=3)
				cv2.putText(imgUMat, "ID:" + str(element["TrackID"]), (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,55,55), thickness=3)

	if show_gest_captions is True:
		if 'GESTURE_DET_FPS' in module_FPS:
			cv2.putText(imgUMat, str(module_FPS['GESTURE_DET_FPS']) + " FPS", (50, 100), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,55,255), thickness=3) 
		if 'DETECTED_GESTURES' in recognition_dict:
			for element in recognition_dict['DETECTED_GESTURES']:
				xmin, ymin, xmax, ymax = convertBack(float(element["center"][0] * 1080), float(element["center"][1] * 1920), float(element["w_h"][0] * 1080), float(element["w_h"][1] * 1920))
				pt1 = (xmin, ymin)
				pt2 = (xmax, ymax)
				cv2.rectangle(imgUMat, pt1, pt2, color=(55,55,255), thickness=2)
				cv2.putText(imgUMat, element["name"], (int(pt1[0] + 5), int(pt1[1] + 60)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,55,255), thickness=3)
				cv2.putText(imgUMat, "ID:" + str(element["TrackID"]), (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,55,255), thickness=3)

	if show_obj_captions is True:
		if 'OBJECT_DET_FPS' in module_FPS:
			cv2.putText(imgUMat, str(module_FPS['OBJECT_DET_FPS']) + " FPS", (50, 150), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,255,55), thickness=3)
		if 'DETECTED_OBJECTS' in recognition_dict:
			for element in recognition_dict['DETECTED_OBJECTS']:
				xmin, ymin, xmax, ymax = convertBack(float(element["center"][0] * 1080), float(element["center"][1] * 1920), float(element["w_h"][0] * 1080), float(element["w_h"][1] * 1920))
				pt1 = (xmin, ymin)
				pt2 = (xmax, ymax)
				cv2.rectangle(imgUMat, pt1, pt2, color=(55,255,55), thickness=2)
				cv2.putText(imgUMat, element["name"], (int(pt1[0] + 5), int(pt1[1] + 60)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,255,55), thickness=3)
				cv2.putText(imgUMat, "ID:" + str(element["TrackID"]), (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,255,55), thickness=3)


	image = cv2.UMat.get(imgUMat)

	if show_gest_captions is False and show_obj_captions is False and  show_camera is False:
		if 'DETECTED_GESTURES' in recognition_dict:
			for element in recognition_dict['DETECTED_GESTURES']:
				name = element["name"]
				if name in image_gestures:
					cpX = int(element["center"][0]*1080)
					cpY = int(element["center"][1]*1920)
				
					if(cpX + image_gestures[name].shape[1] > 1080):
						cpX = 1080 - image_gestures[name].shape[1]
					if(cpY + image_gestures[name].shape[0] > 1920):
						cpY = 1920 - image_gestures[name].shape[0]

					image [cpY:cpY + image_gestures[name].shape[0] , cpX:cpX + image_gestures[name].shape[1]] =  image_gestures[name]
					
				
		
	out.write(image)

	#cv2.imshow("center image", image)
	#cv2.waitKey(1)


