#!/bin/bash

cd $(dirname $0) # go to THIS directory
root -l "plot_drift_data.C(\"../drift_data.root\")"
