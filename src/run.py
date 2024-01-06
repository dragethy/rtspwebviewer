#!/usr/bin/env python3
"""
@brief    Software to launch a web server that displays an RTSP stream.
@details  Code inspired by: 
              
              https://towardsdatascience.com/video-streaming-in-web-browsers-
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
import numpy as np


# Initialize a flask object
app = flask.Flask(__name__)

# Initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
output_frames = []
locks = []

# Initialise video stream object so that it is accessible from the Flask functions
streams = []


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
    parser.add_argument('-u', '--url', required=True, nargs='+', default=[],
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
    """
    @class RTSPVideoStream is a reader of RTSP video frames that runs on a
           different thread.
    """

    def __init__(self, url=None, reopen_interval=2):
        """
        @param[in]  url              RTSP URL.
        @param[in]  reopen_interval  When a read() error is detected by the
                                     video capture object, the video capture
                                     is restarted. After the restart we sleep
                                     for 'reopen_interval' seconds before
                                     reading new frames.
        """
        # Initialise attributes
        self.url = url
        self.reopen_interval = reopen_interval
        self.stopped = False
        self.frame = None
        
    def start(self):
        """@brief Call this method to launch the capture thread."""
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """brief Keep looping infinitely until the thread is stopped."""
        # Initialise video capture
        cap = cv2.VideoCapture(self.url)

        # Read from the RTSP stream forever
        while True:
            if self.stopped:
                return
            (grabbed, frame) = cap.read()
            if grabbed:
                self.frame = frame
            else:
                print('[ERROR] Reading stream. Re-opening videoc capture.')
                cap = cv2.VideoCapture(self.url)
                time.sleep(self.reopen_interval)

    def read(self):
        """@returns the frame most recently read."""
        return self.frame

    def stop(self):
        """@brief Indicate that the thread should be stopped."""
        self.stopped = True


def display_frame(idx: int):
    """
    @brief Display the most recent frame on the website.

    @param[in]  idx  RTSP stream index. The command line option --url supports
                     a list of RTSP streams (up to 4). This index refers to 
                     that list.

    @returns the last frame encoded as HTTP payload.
    """
    global output_frames, locks
    while True:
        with locks[idx]:
            if output_frames[idx] is None:
                continue
            # Encode the frame in JPEG
            (success, encoded_im) = cv2.imencode('.jpg', output_frames[idx])
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
    global streams, output_frames, locks
    
    while True:
        for i, vs in enumerate(streams):
            frame = vs.read()
            if frame is not None:
                # NOTE: Preprocess frame here if you wish
                with locks[i]:
                    output_frames[i] = frame


@app.route('/' + args.password)
def index():
    """@returns the rendered template."""
    global args, window_width, window_height
    return flask.render_template('index.html', title=args.title)


@app.route('/' + args.password + '/camera_1x1')
def camera_1x1():
    """
    @returns the response generated along with the specific media type 
             (mime type).
    """
    mimetype = 'multipart/x-mixed-replace; boundary=frame'
    return flask.Response(display_frame(0), mimetype=mimetype)

def main():
    global args, app, streams, locks, output_frames 

    # Initialise as many input video stream readers as the user wants
    locks = [ threading.Lock() for _ in args.url ]
    output_frames = [ None for _ in args.url ]
    streams = [ RTSPVideoStream(url=u).start() for u in args.url ]

    # Launch frame preprocessor
    t = threading.Thread(target=preprocess_frame, args=())
    t.daemon = True
    t.start() 

    # Launch web server
    http_server = gevent.pywsgi.WSGIServer((args.address, args.port), app)
    http_server.serve_forever()

    # Stop the input video streams
    for stream in streams:
        stream.stop()


if __name__ == '__main__':
    main()
