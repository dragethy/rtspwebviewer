#!/bin/bash

# Launch rtspwebviewer web server
sudo -u $USER /bin/zsh -c "source $HOME/.zshrc && python -m rtspwebviewer.run -u $RWV_RTSP_ADDRESS -a $RWV_LISTENING_IP -p $RWV_PORT -t $RWV_TITLE"

# Run the CMD specified by the user
sh -c "$(echo $@)"
