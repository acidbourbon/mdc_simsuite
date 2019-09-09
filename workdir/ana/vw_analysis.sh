#!/bin/bash

cd $(dirname $0) # go to THIS directory
root -l "vw_analysis.C(\"../drift_data.root\")"
