#!/bin/bash

export DOCKER_ID_USER="acidbourbon"
docker login
docker tag mdc_simsuite acidbourbon/mdc_simsuite
docker push acidbourbon/mdc_simsuite
