#!/bin/bash

name=$(basename $(pwd))

docker build -t $name . || exit

docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
--name $name -v $(pwd)/workdir:/workdir \
-p 8888:8888 \
--device /dev/ttyACM0:/dev/ttyACM0 \
--rm -it --user $(id -u) $name 
