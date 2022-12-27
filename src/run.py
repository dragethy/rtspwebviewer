#!/usr/bin/env python3
"""
@brief    Software to launch a web server that displays an RTSP stream.
@details  Code inspired by: https://towardsdatascience.com/video-streaming-in-web-browsers-
                            with-opencv-flask-93a38846fe00

@author Luis C. Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
@date   10 Sep 2022.
"""

import argparse
import cv2
import threading
import time
import imutils
import gevent.pywsgi
import flask
import os
import ffmpeg
import numpy as np


# Initialize a flask object
app = flask.Flask(__name__)

# Initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
output_frame = None
lock = threading.Lock()

# Initialise video stream object so that it is accessible from the Flask functions
vs = None


def help(short_option):
    """
    @returns The string with the help information for each command 
             line option.
    """
    help_msg = {
        '-t': 'Web title (required: True)',
        '-u': 'RTSP URL (required: True)',
        '-a': 'The HTTP server will listen in this address (required: True)',
        '-p': 'The HTTP server will listen in this TCP port (required: True)',
        '-w': 'URL-based password (required: True)',
    }
    return help_msg[short_option]


def parse_cmdline_params():
    """@returns The argparse args object."""

    # Create command line parser
    parser = argparse.ArgumentParser(description='PyTorch segmenter.')
    parser.add_argument('-u', '--url', required=True, type=str, 
                        help=help('-u'))
    parser.add_argument('-a', '--address', required=True, type=str, 
                        help=help('-a'))
    parser.add_argument('-p', '--port', required=True, type=int,
                        help=help('-p'))
    parser.add_argument('-t', '--title', required=True, type=str,
                        help=help('-t'))
    parser.add_argument('-w', '--password', required=False, default='', type=str,
                        help=help('-w'))

    # Read parameters
    args = parser.parse_args()
    
    return args

# Get command line arguments
args = parse_cmdline_params()


class RTSPVideoStream:
    def __init__(self, url=None, reopen_interval=2):
        """
        @param[in]  url  RTSP URL, e.g.: rtsp://<user>:<password>@<ip>:<port>/unicast
        """
        # Initialise attributes
        self.url = url
        self.reopen_interval = reopen_interval
        self.stopped = False
        self.frame = None
        
        # Initialise video capture
        #self.stream = cv2.VideoCapture(self.url)

    def start(self):
        """@brief Call this method to launch the capture thread."""
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """brief Keep looping infinitely until the thread is stopped."""
        # Get stream dimensions
        cap = cv2.VideoCapture(self.url)
        grabbed = False
        frame = None
        while not grabbed:
            grabbed, frame = cap.read()
        width = frame.shape[1]
        height = frame.shape[0]
        cap.release()

        # Launch ffmpeg capture process
        print('[INFO] Launching ffmpeg ...')
        ffmpeg_args = {
            "hwaccel": "cuda",
            "rtsp_transport": "tcp",
            "fflags": "nobuffer",
            "flags": "low_delay",
        }
        ffmpeg_process = (
        ffmpeg
        .input(self.url, **ffmpeg_args)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24', vsync=2)
        .overwrite_output()
        .run_async(pipe_stdout=True)
        )
        print('[INFO] ffmpeg is now running.')

        while True:
            if self.stopped:
                return
            in_bytes = ffmpeg_process.stdout.read(width * height * 3)
            if in_bytes:
                self.frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])[...,::-1].copy()

    def read(self):
        """@returns the frame most recently read."""
        return self.frame

    def stop(self):
        """@brief Indicate that the thread should be stopped."""
        self.stopped = True


def display_frame():
    """
    @brief Display the most recent frame on the website.
    @returns the last frame encoded as HTTP payload.
    """
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            # Encode the frame in JPEG
            (success, encoded_im) = cv2.imencode('.jpg', output_frame)
            if not success:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' \
            + bytearray(encoded_im) + b'\r\n')


def preprocess_frame():
    """ 
    @brief Function to preprocess the frames before displaying them.
           At the moment it does not do anything.
    @returns nothing.
    """
    #global vs, output_frame, lock, window_width
    global vs, output_frame, lock
    
    while True:
        frame = vs.read()
        if frame is not None:
            # NOTE: Preprocess frame here if you wish
            with lock:
                output_frame = frame


@app.route('/' + args.password)
def index():
    """@returns the rendered template."""
    global args, window_width, window_height
    return flask.render_template('index.html', title=args.title)


@app.route('/' + args.password + '/video_feed')
def video_feed():
    """@returns the response generated along with the specific media type (mime type)."""
    return flask.Response(display_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    global app, vs, args
    
    # Initialise the video stream and allow the camera sensor to warmup
    vs = RTSPVideoStream(url=args.url).start()
    #warmup_time_s = 2
    #time.sleep(warmup_time_s)

    # Launch frame preprocessor
    t = threading.Thread(target=preprocess_frame, args=())
    t.daemon = True
    t.start() 

    # Launch web server
    http_server = gevent.pywsgi.WSGIServer((args.address, args.port), app)
    http_server.serve_forever()

    # Stop the input video stream
    vs.stop()


if __name__ == '__main__':
    main()
