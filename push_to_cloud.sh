#!/bin/bash

export DOCKER_ID_USER="acidbourbon"
docker login
docker tag mdc_3d_garfield_ubuntu acidbourbon/mdc_3d_garfield
docker push acidbourbon/mdc_3d_garfield
