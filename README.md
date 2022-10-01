Description
-----------

Web server that displays an RTSP video stream. 

It is not a very efficient solution in terms of video transmission, but you will be able to see the video stream from all devices (Windows, Linux, Mac, iPhone, Android). 

Audio is not supported.

Use case
--------

You have a security camera that streams in [RTSP](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol) (e.g. [Foscam](https://www.amazon.co.uk/Foscam-Wireless-Indoor-Security-Camera/dp/B07WHY74F1)) and want to make the video accessible via web.

Install with pip
----------------

```bash
$ pip install rtspwebviewer --user
```

Install from source
-------------------

```bash
$ git clone https://github.com/luiscarlosgph/rtspwebviewer.git
$ cd rtspwebviewer
$ python3 setup.py install
```

Run 
---

* Syntax:
  ```bash
  $ python rtspwebviewer.run -u <rtsp_address> -a <listening_ip_address> -p <port> -t <web_title> -w <password>
  ```

* Example:
  ```bash
  $ python rtspwebviewer.run -u 'rtsp://user:pass@127.0.0.1:8669/unicast' -a 0.0.0.0 -p 7654 -t 'RTSP Web Viewer' -w fancypassword
  ```
  In this case, you should access [http://127.0.0.1:7654/fancypassword](http://127.0.0.1:7654/fancypassword) to see the website displaying the video stream. 
  
  The IP address `0.0.0.0` means that the web server will listen in all your network interfaces. 

  The password parameter is optional, if you do not specify one, you should access [http://127.0.0.1:7654](http://127.0.0.1:7654) to see the video.
  
 
Run Docker container
---------------------
If you do not have Docker installed, you have an install guide [here](https://github.com/luiscarlosgph/how-to/tree/main/docker).

1. Build Docker image:
   ```bash
   $ git clone https://github.com/luiscarlosgph/rtspwebviewer.git
   $ cd rtspwebviewer
   $ docker build -t rtspwebviewer docker
   ```

2. Deploy container:
   ```bash
   $ docker run --name rtspwebviewer --net=host rtspwebviewer:latest python -m rtspwebviewer.run -u <rtsp_address> -a <listening_ip_address> -p <port> -t <web_title>
   ```
<!-- You will be able to access the camera view in `http://127.0.0.1:<port>`. -->
