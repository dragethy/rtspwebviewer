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
import flask
import os


# Initialize a flask object
app = flask.Flask(__name__)

# Initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
output_frame = None
lock = threading.Lock()

# Initialise video stream object so that it is accessible from the Flask functions
vs = None

# Initialise command line arguments
args = None


class RTSPVideoStream:
    def __init__(self, url=None, reopen_interval=2):
        """
        @param[in]  url  RTSP URL, e.g.: rtsp://<user>:<password>@<ip>:<port>/unicast
        """
        # Initialise attributes
        self.url = url
        self.reopen_interval = reopen_interval
        self.stopped = False
        self.grabbed = False
        self.frame = None
        
        # Initialise video capture
        self.stream = cv2.VideoCapture(self.url)
        #(self.grabbed, frame) = self.stream.read()

    def start(self):
        """@brief Call this method to launch the capture thread."""
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """brief Keep looping infinitely until the thread is stopped."""
        while True:
            if self.stopped:
                return
            (self.grabbed, frame) = self.stream.read()
            if self.grabbed:
                self.frame = frame
            else:
                print('[ERROR] Reading stream. Re-opening videoc capture.')
                self.stream = cv2.VideoCapture(self.url)
                time.sleep(self.reopen_interval)

    def read(self):
        """@returns the frame most recently read."""
        return self.frame

    def stop(self):
        """@brief Indicate that the thread should be stopped."""
        self.stopped = True


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

    # Read parameters
    args = parser.parse_args()
    
    return args


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
            (success, encoded_im) = cv2.imencode('.jpg', output_frame)
            if not success:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' \
            + bytearray(encoded_im) + b'\r\n')


def preprocess_frame(width: int = 1024):
    """ 
    @brief Function to preprocess the frames before displaying them.
           At the moment it does not do anything.
    @returns nothing.
    """
    global vs, output_frame, lock
    
    while True:
        frame = vs.read()
        if frame is not None:
            #frame = imutils.resize(frame, width=width)
            with lock:
                output_frame = frame.copy()


@app.route('/')
def index():
    """@returns the rendered template."""
    global args
    return flask.render_template('index.html', title=args.title)


@app.route('/video_feed')
def video_feed():
    global output_frame, lock
	# return the response generated along with the specific media
	# type (mime type)
    return flask.Response(display_frame(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    global app, vs, args
    
    # Read command line parameters
    args = parse_cmdline_params()
    
    # Initialise the video stream and allow the camera sensor to warmup
    vs = RTSPVideoStream(url=args.url).start()
    warmup_time_s = 2
    time.sleep(warmup_time_s)

    # Launch frame preprocessor
    t = threading.Thread(target=preprocess_frame, args=())
    t.daemon = True
    t.start() 

    # Start the flask app
    app.run(host=args.address, port=args.port, debug=False, threaded=True, use_reloader=False)

    # Stop the input video stream
    vs.stop()


if __name__ == '__main__':
    main()
