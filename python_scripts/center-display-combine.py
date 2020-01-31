# camera.py

import cv2
import numpy as np
from threading import Thread
import time
import os, sys
import subprocess
import signal
import json

def to_node(type, message):
	# convert to json and print (node helper will read from stdout)
	try:
		print(json.dumps({type: message}))
	except Exception:
		pass
	# stdout has to be flushed manually to prevent delays in the node helper communication
	sys.stdout.flush()

BASE_DIR = os.path.dirname(__file__) + '/'
os.chdir(BASE_DIR)

#Full HD image as default
IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920
global AI_ART_MIRROR
AI_ART_MIRROR = False

try:
	to_node("status", "starting with config: " + sys.argv[1])
	config = json.loads(sys.argv[1])
	if 'image_height' in config:
		IMAGE_HEIGHT = int(config['image_height'])
	if 'image_width' in config:
		IMAGE_WIDTH = int(config['image_width'])
	if 'ai_art_mirror' in config:
		AI_ART_MIRROR = bool(config['ai_art_mirror'])

except:
	to_node("status", "starting without config as it was not readable/existent")


global global_show_face_captions 
global global_show_obj_captions 
global global_show_gest_captions 
global global_show_person_captions 
global global_show_camera 
global global_show_camera_1m 
global global_show_style_transfer

global recognition_dict
global module_FPS

global_show_face_captions = False
global_show_obj_captions = False
global_show_gest_captions = False
global_show_person_captions = True
global_show_camera = True
global_show_camera_1m = False
global_show_style_transfer = False

recognition_dict = {}
module_FPS = {}

if os.path.exists("/dev/shm/center_display") is True:
	os.remove("/dev/shm/center_display")

out = cv2.VideoWriter ('appsrc ! shmsink socket-path=/dev/shm/center_display sync=true wait-for-connection=false shm-size=100000000',0, 30, (IMAGE_WIDTH, IMAGE_HEIGHT), True)

out.write(np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8))
out.write(np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8))
out.write(np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8))
out.write(np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8))

to_node('status','starting sub process')

pp = subprocess.Popen(['python3', 'webstream.py', str(IMAGE_HEIGHT), str(IMAGE_WIDTH) ])


def check_stdin():
	global global_show_face_captions
	global global_show_obj_captions
	global global_show_gest_captions
	global global_show_person_captions
	global global_show_camera
	global global_show_camera_1m
	global global_show_style_transfer
	global recognition_dict
	global module_FPS
	global AI_ART_MIRROR
	
	while True:
		lines = sys.stdin.readline()
		try:
			data = json.loads(lines)
			if 'SET' in data:
				setting = data['SET']
				to_node('status', "Changing: " + setting)
				if setting == 'TOGGLE':
					global_show_camera = not global_show_camera
					global_show_style_transfer = False
				elif setting == 'DISTANCE':
					global_show_camera_1m = not global_show_camera_1m
				elif setting == 'FACE':
					global_show_face_captions = not global_show_face_captions
				elif setting == 'OBJECT':
					global_show_obj_captions = not global_show_obj_captions
				elif setting == 'GESTURE':
					global_show_gest_captions = not global_show_gest_captions
				elif setting == 'PERSON':
					global_show_person_captions = not global_show_person_captions
				elif setting == 'STYLE_TRANSFERE' and AI_ART_MIRROR:
					global_show_obj_captions = False
					global_show_face_captions = False
					global_show_gest_captions = False
					global_show_person_captions = False
					global_show_camera = False
					global_show_camera_1m = False
					global_show_style_transfer = not global_show_style_transfer
				elif setting == 'HIDEALL':
					global_show_obj_captions = False
					global_show_face_captions = False
					global_show_gest_captions = False
					global_show_person_captions = False
					global_show_camera = False
					global_show_camera_1m = False
					global_show_style_transfer = False
				elif setting == 'SHOWALL':
					global_show_obj_captions = True
					global_show_face_captions = True
					global_show_gest_captions = True
					global_show_camera = True
					global_show_camera_1m = False
					global_show_style_transfer = False
			elif 'DETECTED_FACES' in data:
				recognition_dict['DETECTED_FACES'] = data['DETECTED_FACES']
				#to_node('status',recognition_dict['DETECTED_FACES'])
			elif 'DETECTED_GESTURES' in data:
				recognition_dict['DETECTED_GESTURES'] = data['DETECTED_GESTURES']
				#to_node('status',recognition_dict['DETECTED_GESTURES'])
			elif 'DETECTED_OBJECTS' in data:
				recognition_dict['DETECTED_OBJECTS'] = data['DETECTED_OBJECTS']
				#to_node('status',recognition_dict['DETECTED_OBJECTS'])
			elif 'RECOGNIZED_PERSONS' in data:
				recognition_dict['RECOGNIZED_PERSONS'] = data['RECOGNIZED_PERSONS']
				#to_node('status',data)
			elif 'GESTURE_DET_FPS' in data:
				module_FPS['GESTURE_DET_FPS'] = data['GESTURE_DET_FPS']
			elif 'OBJECT_DET_FPS' in data:
				module_FPS['OBJECT_DET_FPS'] = data['OBJECT_DET_FPS']
			elif 'FACE_DET_FPS' in data:
				module_FPS['FACE_DET_FPS'] = data['FACE_DET_FPS']
		except:
			to_node("error","check_std_in error")


t = Thread(target=check_stdin)
t.start()


#cv2.namedWindow("center image", cv2.WINDOW_NORMAL)

to_node('status', "check_stdin started")

def convertBack(x, y, w, h):
	x = x * IMAGE_WIDTH
	y = y * IMAGE_HEIGHT
	w = w * IMAGE_WIDTH
	h = h * IMAGE_HEIGHT
	xmin = int(round(x - (w / 2)))
	xmax = int(round(x + (w / 2)))
	ymin = int(round(y - (h / 2)))
	ymax = int(round(y + (h / 2)))
	return (xmin, ymin),(xmax, ymax)

def shutdown(self, signum):
	to_node('status', 'Shutdown: Cleaning up camera...')
	os.remove("/dev/shm/center_display")
	pp.kill()
	video.release()
	video_1m.release()
	video_style_transfer.release()
	out.release()

	to_node('status', 'Shutdown: Done.')
	exit()

signal.signal(signal.SIGINT, shutdown)

to_node('status', "loading hand images")

image_gestures = {}
image_gestures["flat_right"] = cv2.imread('icons/flat_right.jpg')
image_gestures["flat_left"] = cv2.imread('icons/flat_left.jpg')
image_gestures["okay_right"] = cv2.imread('icons/okay_right.jpg')
image_gestures["okay_left"] = cv2.imread('icons/okay_left.jpg')
image_gestures["thumbs_up_right"] = cv2.imread('icons/thumbs_up_right.jpg')
image_gestures["thumbs_up_left"] = cv2.imread('icons/thumbs_up_left.jpg')
image_gestures["thumbs_down_right"] = cv2.imread('icons/thumbs_down_right.jpg')
image_gestures["thumbs_down_left"] = cv2.imread('icons/thumbs_down_left.jpg')
image_gestures["two_left"] = cv2.imread('icons/two_left.jpg')
image_gestures["two_right"] = cv2.imread('icons/two_right.jpg')
image_gestures["one_left"] = cv2.imread('icons/one_left.jpg')
image_gestures["one_right"] = cv2.imread('icons/one_right.jpg')

#time.sleep(5)
 
video = cv2.VideoCapture()
video_1m = cv2.VideoCapture()
video_style_transfer = cv2.VideoCapture()

to_node('status', "getting video stream")
while video.isOpened() is False:
	video.open("shmsrc socket-path=/dev/shm/camera_image ! video/x-raw, format=BGR, height=" + str(IMAGE_HEIGHT) + ", width=" + str(IMAGE_WIDTH) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
	
to_node('status', 'getting video_1m stream')
while video_1m.isOpened() is False:
	video_1m.open("shmsrc socket-path=/dev/shm/camera_1m ! video/x-raw, format=BGR, height=" + str(IMAGE_HEIGHT) + ", width=" + str(IMAGE_WIDTH) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
#video_style_transfer = cv2.VideoCapture("shmsrc socket-path=/tmp/style_transfer is-live=true ! queue ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! queue ! appsink wait-on-eos=false drop=true", cv2.CAP_GSTREAMER)


if AI_ART_MIRROR is True:
	to_node('status', "getting video_style_transfer stream")
	while video_style_transfer.isOpened() is False:
		video_style_transfer.open("shmsrc socket-path=/dev/shm/style_transfer ! video/x-raw, format=BGR, height=" + str(IMAGE_HEIGHT) + ", width=" + str(IMAGE_WIDTH) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
else:
	to_node('status', "starting without video_style_transfer")


achieved_FPS_counter = 0.0
achieved_FPS = 0.0

to_node('status', 'starting while loop')
while True:

	start_time = time.time();

	show_face_captions = global_show_face_captions
	show_obj_captions = global_show_obj_captions
	show_gest_captions = global_show_gest_captions
	show_person_captions = global_show_person_captions
	show_camera = global_show_camera
	show_camera_1m = global_show_camera_1m
	show_style_transfer = global_show_style_transfer


	if show_camera is True:
		if show_camera_1m is True:
			ret, image = video_1m.read()
		else:
			ret, image = video.read()

	elif show_style_transfer is True:
			ret, image = video_style_transfer.read()
	else:
		image = np.zeros((IMAGE_HEIGHT,IMAGE_WIDTH,3), np.uint8)
		ret = True

	if ret is False:
		to_node('status', "ret was false.. no image captured")
		image = np.zeros((IMAGE_HEIGHT,IMAGE_WIDTH,3), np.uint8)

	
	
	imgUMat = cv2.UMat(image)	


	if show_face_captions is True:	
		if 'DETECTED_FACES' in recognition_dict:
			for element in recognition_dict['DETECTED_FACES']:
				pt1, pt2 = convertBack(element["center"][0], element["center"][1], element["w_h"][0], element["w_h"][1])
				cv2.rectangle(imgUMat, pt1, pt2, color=(255,55,55), thickness=2)
				cv2.putText(imgUMat, element["name"]+ "/ID:" + str(element["TrackID"]) , (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,55,55), thickness=3)
				cv2.putText(imgUMat,"confidence: " + str(element["confidence"]) , (int(pt1[0]), int(pt2[1] + 20)), cv2.FONT_HERSHEY_DUPLEX, fontScale=0.5, color=(255,55,55), thickness=2)
			

	if show_gest_captions is True:
		if 'DETECTED_GESTURES' in recognition_dict:
			for element in recognition_dict['DETECTED_GESTURES']:
				pt1,pt2 = convertBack(element["center"][0], element["center"][1], element["w_h"][0], element["w_h"][1])
				cv2.rectangle(imgUMat, pt1, pt2, color=(55,55,255), thickness=2)
				cv2.putText(imgUMat, element["name"] + "/ID:" + str(element["TrackID"]), (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,55,255), thickness=3)


	if show_person_captions is True:
		try:
			if 'RECOGNIZED_PERSONS' in recognition_dict:
				persons = recognition_dict['RECOGNIZED_PERSONS'].copy()
				for key in persons.keys():
					element = persons[key]
					pt1, pt2 = convertBack(element["center"][0], element["center"][1], element["w_h"][0], element["w_h"][1])
					cv2.rectangle(imgUMat, pt1, pt2, color=(255,255,255), thickness=2)
					cv2.putText(imgUMat, "TrackID:" + str(element["TrackID"]), (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,255,255), thickness=3)
					if "face" in element:
						cv2.putText(imgUMat, element["face"]["name"] , (int(pt1[0] + 5), int(pt1[1] + 60)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,255,255), thickness=3)
						cv2.putText(imgUMat,"with id: " + str(element["face"]["id"]) , (int(pt1[0] + 5), int(pt1[1] + 80)), cv2.FONT_HERSHEY_DUPLEX, fontScale=0.5, color=(255,255,255), thickness=2)
						cv2.putText(imgUMat,"and confidence: " + str(element["face"]["confidence"]) , (int(pt1[0] + 5), int(pt1[1] + 100)), cv2.FONT_HERSHEY_DUPLEX, fontScale=0.5, color=(255,255,255), thickness=2)
						if "center" in element["face"]:
							pt1, pt2 = convertBack(element["face"]["center"][0], element["face"]["center"][1], element["face"]["w_h"][0], element["face"]["w_h"][1])
							cv2.rectangle(imgUMat, pt1, pt2, color=(255,255,255), thickness=2)

					if "gestures" in element:
						for gesture in element["gestures"]:
							pt1, pt2 = convertBack(gesture["center"][0], gesture["center"][1], gesture["w_h"][0], gesture["w_h"][1])
							cv2.rectangle(imgUMat, pt1, pt2, color=(255,255,255), thickness=2)
							cv2.putText(imgUMat, gesture["name"] , (int(pt1[0] + 5), int(pt1[1] + 60)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,255,255), thickness=3)
							


		except:
			to_node("error","drawing person reg error")
			to_node("error", json.dumps(element))

	

	if show_obj_captions is True:
		if 'DETECTED_OBJECTS' in recognition_dict:
				for element in recognition_dict['DETECTED_OBJECTS']:
					pt1, pt2 = convertBack(element["center"][0], element["center"][1], element["w_h"][0], element["w_h"][1] )
					cv2.rectangle(imgUMat, pt1, pt2, color=(55,255,55), thickness=2)
					cv2.putText(imgUMat, element["name"] + "/ID:" + str(element["TrackID"]) , (int(pt1[0] + 5), int(pt1[1] + 30)), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(55,255,55), thickness=3)

	image = cv2.UMat.get(imgUMat)

	if show_gest_captions is False and show_obj_captions is False and show_camera is False:
		if 'DETECTED_GESTURES' in recognition_dict:
			for element in recognition_dict['DETECTED_GESTURES']:
				name = element["name"]
				if name in image_gestures:
					cpX = int(element["center"][0]*IMAGE_WIDTH)
					cpY = int(element["center"][1]*IMAGE_HEIGHT)
				
					if(cpX + image_gestures[name].shape[1] > IMAGE_WIDTH):
						cpX = IMAGE_WIDTH - image_gestures[name].shape[1]
					if(cpY + image_gestures[name].shape[0] > IMAGE_HEIGHT):
						cpY = IMAGE_HEIGHT - image_gestures[name].shape[0]

					area = image [cpY:cpY + image_gestures[name].shape[0] , cpX:cpX + image_gestures[name].shape[1]]
					image [cpY:cpY + image_gestures[name].shape[0] , cpX:cpX + image_gestures[name].shape[1]] =  np.where(image_gestures[name] > 100 ,image_gestures[name], area)
					
				
		
	out.write(image)

	achieved_FPS_counter += 1.0
	
	achieved_FPS +=  (time.time() - start_time)

	if achieved_FPS_counter > 30:
		to_node("CENTER_DISPLAY_FPS", float("{0:.2f}".format(1 / (achieved_FPS / achieved_FPS_counter))))
		achieved_FPS_counter = 0.0
		achieved_FPS = 0.0

	#cv2.imshow("center image", image)
	#cv2.waitKey(1)


