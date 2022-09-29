Description
-----------

Web server that displays an RTSP video stream.

Install with pip
----------------

```bash
$ pip install rtspwebviewer --user
```

Install from source
-------------------

```bash
$ python3 setup.py install
```

Run 
---

* Syntax:
  ```bash
  $ python rtspwebviewer.run -u <rtsp_address> -a <listening_ip_address> -p <port> -t <web_title>
  ```

* Example:
  ```bash
  $ python rtspwebviewer.run -u 'rtsp://user:pass@127.0.0.1:8669/unicast' -a 0.0.0.0 -p 7654 -t 'RTSP Web Viewer'
  ```
  In this case, you would connect to [http://127.0.0.1:7654](http://127.0.0.1:7654) and you would see a website with the video stream. The IP address `0.0.0.0` means that the web server will listen in all your network interfaces.
  
 
Run Docker container
---------------------
1. Build Docker image:
```bash
$ docker build -t rtspwebviewer docker
```

2. Deploy container:
```bash
$ docker run --name rtspwebviewer rtspwebviewer:latest /bin/zsh -c "source $HOME/.zshrc && python -m rtspwebviewer.run -u <rtsp_address> -a <listening_ip_address> -p <port> -t <web_title>"
```
