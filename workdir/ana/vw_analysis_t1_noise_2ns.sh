#!/bin/bash

cd $(dirname $0) # go to THIS directory


export t1_noise=2.0 # ns
# export fish_z_max=300

root -l "vw_analysis.C(\"../drift_data.root\")"
