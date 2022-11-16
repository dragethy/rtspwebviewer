#!/bin/zsh

source $USER/.zshrc

# Run the CMD specified by the user
sh -c "$(echo $@)"
