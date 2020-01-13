#!/bin/bash



docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
--name mdc_simsuite_prebuilt -v $(pwd)/workdir:/workdir \
-p 8888:8888 \
--rm -it --user $(id -u) acidbourbon/mdc_simsuite
