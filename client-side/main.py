from data_man import *
import subprocess as sp
from pure_data import *
from socket import *
import numpy as np
import progressbar
import threading
import datetime
import keyboard
import time
import math
import h5py
import cv2

import global_vars


recording = False
recording_count = 0
is_pressed = False
current_timestamp = ''

batch_size = 200
actions_size = 174
desired_fps = 20

video_buffer = np.zeros(shape=(batch_size,4,240,320))
video_storage = np.empty(shape=(batch_size,4,240,320))
actions_buffer = np.zeros(shape=(batch_size,actions_size))
actions_storage= np.empty(shape=(batch_size,actions_size))

frame_lock = threading.Lock()

global_vars.init()

# Create the progressbar to display the batches of data being stored on RAM
bar = progressbar.ProgressBar(maxval=batch_size, widgets = [progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

def getVideoData():
    global frame_lock
    FFMPEG_BIN = "ffmpeg"
    command = [ FFMPEG_BIN,
                '-loglevel', 'quiet',
                '-srtp_in_suite', 'AES_CM_128_HMAC_SHA1_80',
                '-srtp_in_params', '00108310518720928b30d38f41149351559761969b71d79f8218a39259a7',
                '-i', 'srtp://localhost:1234',
                '-f', 'image2pipe',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'rgb24', '-'
                ]
    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
    while True:
        raw_image = pipe.stdout.read(480*640*4)
        image = np.fromstring(raw_image, dtype='uint8')

        # OpenCV interprets images inverted
        cv_image = image[0:480*640*3].reshape((480,640,3))
        depth_image = image[(480*640*3):].reshape((480,640))
        depth_image = np.flip(depth_image, 1)
        cv_image = np.flip(cv_image, 1)
        cv_image = np.dstack((cv_image, depth_image))
        cv_image = cv2.resize(cv_image, dsize=(320,240), interpolation=cv2.INTER_NEAREST)
        #with frame_lock:
        global_vars.g_current_frame = cv_image.astype(np.uint8).copy()

# Create the video stream thread
try:
    t = threading.Thread(target=getVideoData)
    t.start()
except:
    print("Something went wrong trying to start getVideoData")
# Create the pure data receive thread
try:
    t = threading.Thread(target=pdreceive)
    t.start()
except:
    print("Something went wrong trying to start pdreceive")

start_time = time.time()
while(True):
    if keyboard.is_pressed('space'):
        is_pressed = True
    else:
        if is_pressed:
            recording = not recording
            if recording:
                current_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
                recording_count = 0
                print("Recording on dataset " + str(current_timestamp))
                bar.start()
            is_pressed = False
        
    #with frame_lock:
    show_image = global_vars.g_current_frame.astype(np.uint8).copy()

    cv2.imshow('ImprovAI', show_image)
    if(recording):
        video_buffer[recording_count] = np.moveaxis(global_vars.g_current_frame, -1, 0)
        actions_buffer[recording_count] = np.array(global_vars.g_current_state)[:174]
        bar.update(recording_count + 1)
        if recording_count >= 199: #reached the end of the buffer, execute store callback and reset counter
            video_storage = np.copy(video_buffer)
            actions_storage = np.copy(actions_buffer)
            try:
                t = threading.Thread(target=store_raw, args=(current_timestamp,video_storage,actions_storage))
                t.start()
            except:
                print("Could not create storage thread!!!!")
            recording_count = 0
            bar.finish()
            bar.start()
        recording_count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # measure time
    end_time = time.time()
    elapsed = end_time - start_time
    desired_elapsed = 1/desired_fps
    if (elapsed > desired_elapsed):
        print("Process is running slower than desired! Check your fps limit and lower it.")
    else:
        time.sleep(desired_elapsed - elapsed) #Sleep enough time to make each loop take the desired time
    end_time = time.time()
    fps = 1/(end_time - start_time)
    print("fps: " + str(fps))
    start_time = time.time()
