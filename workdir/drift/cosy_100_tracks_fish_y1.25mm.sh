#!/bin/bash
cd $(dirname $0)

temp=$(mktemp)

## options for track generator as env variables
export outfile=$temp
export number=100
export z_length=0.016 # m - track length in z
export displacement_x=0.0 # displacement of tracks in x 
export displacement_y=0.00125 # displacement of tracks in y
export width_x=0.001  # m - simulate uniform track distribution between +-width_x
export width_y=0.000 # m - simulate uniform track distribution between +-width_y

## boundary box for tracks
export x_min=-0.0035
export x_max=+0.0035
export y_min=-0.0035
export y_max=+0.0035
export z_min=-0.0035
export z_max=+0.0085


## call track generator
root -l 'gen_cosy_tracks_fish.C()' -q > /dev/null

## print result and delete temp file
cat $temp
rm $temp
