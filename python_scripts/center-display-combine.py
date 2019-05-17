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

image_face_cap = np.zeros((1920,1080,3), np.uint8)
image_obj_cap = np.zeros((1920,1080,3), np.uint8)
image_gest_cap = np.zeros((1920,1080,3), np.uint8)
image_gest_ind = np.zeros((1920,1080,3), np.uint8)


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


def check_stdin():
	global show_face_captions
	global show_obj_captions
	global show_gest_captions
	global show_camera
	global show_camera_1m
	global show_style_transfer
	while True:
		lines = sys.stdin.readline()
		to_node("status", "Changing: " + lines)
		data = json.loads(lines)
		setting = data['SET']
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

t = Thread(target=check_stdin)
t.start()


#cv2.namedWindow("center image", cv2.WINDOW_NORMAL)

#print("Calling subprocess to open gst_rtsp_server")
BASE_DIR = os.path.dirname(__file__) + '/'
#p = subprocess.Popen(['python', BASE_DIR + 'gst_rtsp_server.py'])
pp = subprocess.Popen(['python', BASE_DIR + 'webstream.py'])

time.sleep(2)


def shutdown(self, signum):
	to_node("status", 'Shutdown: Cleaning up camera...')
	os.remove("/tmp/center_display")
	pp.kill()
	video.release()
	video_face_cap.release()
	video_obj_cap.release()
	video_gest_cap.release()
	video_gest_ind.release()
	video_1m.release()
	video_style_transfer.release()
	out.release()

	to_node("status", 'Shutdown: Done.')
	exit()

signal.signal(signal.SIGINT, shutdown)


time.sleep(5)

video = cv2.VideoCapture("shmsrc socket-path=/tmp/camera_image ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_1m = cv2.VideoCapture("shmsrc socket-path=/tmp/camera_1m ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_face_cap = cv2.VideoCapture("shmsrc socket-path=/tmp/face_recognition_captions ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_obj_cap = cv2.VideoCapture("shmsrc socket-path=/tmp/object_detection_captions ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_gest_cap = cv2.VideoCapture("shmsrc socket-path=/tmp/gesture_recognition_captions ! video/x-raw, format=BGR, height=1920,width=1080, framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_gest_ind = cv2.VideoCapture("shmsrc socket-path=/tmp/gesture_indicator ! video/x-raw, format=BGR, height=1920,width=1080, framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true", cv2.CAP_GSTREAMER)
video_style_transfer = cv2.VideoCapture("shmsrc socket-path=/tmp/style_transfer is-live=true ! queue ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! queue ! appsink wait-on-eos=false drop=true", cv2.CAP_GSTREAMER)



def get_face_caps():
	global image_face_cap
	global show_face_captions
	global video_face_cap
	while True:
		if show_face_captions is True:
			success_cap, image_face_cap_tmp = video_face_cap.read()
			if success_cap is True:
				image_face_cap = np.copy(image_face_cap_tmp)
		else:
			time.sleep(1)
		


def get_obj_caps():
	global image_obj_cap
	global show_obj_captions
	global video_obj_cap
	while True:
		if show_obj_captions is True:
			success_cap, image_obj_cap_tmp = video_obj_cap.read()
			if success_cap is True:
				image_obj_cap = np.copy(image_obj_cap_tmp)
		else:
			time.sleep(1)

def get_gest_caps():
	global image_gest_cap
	global show_gest_captions
	global video_gest_cap
	while True:
		if show_gest_captions is True:
			success_cap, image_gest_cap_tmp = video_gest_cap.read()
			if success_cap is True:
				image_gest_cap = np.copy(image_gest_cap_tmp)
		else:
			time.sleep(1)

def get_gest_inds():
	global image_gest_ind
	global video_gest_ind
	while True:
		success_cap, image_gest_ind_tmp = video_gest_ind.read()
		if success_cap is True:
			image_gest_ind = np.copy(image_gest_ind_tmp)
		else:
			time.sleep(1)


face_thread = Thread(target=get_face_caps, args= ())
face_thread.start()

obj_thread = Thread(target=get_obj_caps, args= ())
obj_thread.start()

gest_thread = Thread(target=get_gest_caps, args= ())
gest_thread.start()

gest_ind_thread = Thread(target=get_gest_inds, args= ())
gest_ind_thread.start()


while video.isOpened() is False:
	to_node("status", 'video is not open')
	time.sleep(5)


while True:

	#if show_style_transfer is False and video_style_transfer.isOpened() is True:
	#	video_style_transfer.release()
	#	#del video_style_transfer
	#	#video_style_transfer = cv2.VideoCapture()
	#	to_node("status", 'closing smo: /tmp/style_transfer')


	if show_camera is True:
		if show_camera_1m is True:
			ret, image = video_1m.read()
		else:
			ret, image = video.read()
	elif show_style_transfer is True:
	#	if video_style_transfer.isOpened() is False:			
	#		video_style_transfer.open("shmsrc socket-path=/tmp/style_transfer is-live=true wait-on-eos=false drop=true ! video/x-raw, format=BGR ,height=1920,width=1080,framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink", cv2.CAP_GSTREAMER)
	#		to_node("status", 'opening smo: /tmp/style_transfer')
		try:		
			ret, frame = video_style_transfer.read()
			if ret is True:
				image = frame.copy()
		except:
			to_node("status", 'error')
	else:
		
		ret = False
		
	if ret is False:


		image = np.zeros((1920,1080,3), np.uint8)
		image = np.where(image_gest_ind > 0 , image_gest_ind , image)

		out.write(image)
		#cv2.imshow("center image", image)
		#cv2.waitKey(1)
		continue
	
	if show_face_captions is True:
		image = np.where(image_face_cap > 0 , image_face_cap , image)

	if show_obj_captions is True:
		image = np.where(image_obj_cap > 0 , image_obj_cap , image)

	if show_gest_captions is True:
		image = np.where(image_gest_cap > 0 , image_gest_cap , image)

	

	out.write(image)


	#cv2.imshow("center image", image_face_cap)
	#cv2.waitKey(1)


