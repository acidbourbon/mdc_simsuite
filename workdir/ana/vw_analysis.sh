#!/bin/bash

cd $(dirname $0) # go to THIS directory


export t1_noise=0
# export fish_z_max=300
export t1_noise_method=random
# export t1_noise_method=conv

root -l "vw_analysis.C(\"../drift_data.root\")"