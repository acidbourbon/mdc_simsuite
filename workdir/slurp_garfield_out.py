#!/usr/bin/env python3



### this script is designed to direcly parse garfield stdout from a pipe
### all units are converted to SI units before writing to the root tree,
### i.e. meters and seconds
### note that internally garfield uses cm and us as base units

import sys
import re


from ROOT import TFile, TTree, TH1, TH1F
from array import array
import numpy as np



root_file = TFile("drift_data.root","RECREATE")
data_tree = TTree("data_tree","data_tree") 


# f for float, i for integer
data = {
  "track_start_x":'f',
  "track_start_y":'f',
  "track_start_z":'f',
  "track_end_x":'f',
  "track_end_y":'f',
  "track_end_z":'f',
  "e_start_x":'f',
  "e_start_y":'f',
  "e_start_z":'f',
  "e_drift_t":'f',
  "hit_wire":'i',
  "evt":'i'
  }


for key in data:
  val_type = data[key]
  data[key] = array(val_type,[0]) # replace type definition with array placeholder
  data_tree.Branch(key,data[key],"{:s}/{:s}".format(key,val_type.upper()))
  
  # set value of data object like this: data[key][0] = 3.14
  # yes: always element 0. the array is just a placeholder
  # data_tree.Fill()




# track geometry information

# example output to match:
#  The particle begins at (     0.100,     0.100,    -0.400)
#  and goes towards       (     0.100,     0.100,     0.400)

# marks also the beginning of a new event

track_start_pattern = re.compile(
  "The particle begins at \(\s+([0-9E+\-.]+),\s+([0-9E+\-.]+),\s+([0-9E+\-.]+)\)"
  )
track_end_pattern = re.compile(
  "and goes towards       \(\s+([0-9E+\-.]+),\s+([0-9E+\-.]+),\s+([0-9E+\-.]+)\)"
  )



# electron drft information

# example output to match:
#   0.100E+00   0.100E+00   0.225E+00   0.391E-01 unavailable unavailable unavailable  Hit S solid 1 
# 
# values to extract:
#   x-start     y-start     z-start   Drift time

hit_pattern = re.compile(
  "([0-9E+\-.]+)\s+([0-9E+\-.]+)\s+([0-9E+\-.]+)\s+([0-9E+\-.]+)\s+unavailable unavailable unavailable  Hit [ST] solid (\d+)"
  )




data["evt"][0] = -1

electrons = 0

for line in sys.stdin:
  
  ### find track geometry information
  
  match = re.search(track_start_pattern, line)
  if match:
    data["evt"][0] = data["evt"][0]+1
    print("\nnew track, event no {:d}".format(data["evt"][0]))
    electrons = 0
    #print(match.groups())
    # convert from cm to m
    data["track_start_x"][0] = 1e-2*float(match.groups()[0])
    data["track_start_y"][0] = 1e-2*float(match.groups()[1])
    data["track_start_z"][0] = 1e-2*float(match.groups()[2])
    
    
  match = re.search(track_end_pattern, line)
  if match:
    #print("track end")
    #print(match.groups())
    # convert from cm to m
    data["track_end_x"][0] = 1e-2*float(match.groups()[0])
    data["track_end_y"][0] = 1e-2*float(match.groups()[1])
    data["track_end_z"][0] = 1e-2*float(match.groups()[2])

  
    
  ### match electron drift information
  match = re.search(hit_pattern, line)
  if match:
    #print("electron")
    #print(match.groups())
    # convert from cm to m
    data["e_start_x"][0] = 1e-2*float(match.groups()[0])
    data["e_start_y"][0] = 1e-2*float(match.groups()[1])
    data["e_start_z"][0] = 1e-2*float(match.groups()[2])
    # convert form us to s
    data["e_drift_t"][0] = 1e-6*float(match.groups()[3])
    data["hit_wire"][0]  =   int(match.groups()[4])
    #print("hit wire: {:d}".format(data["hit_wire"][0]))
    electrons += 1
    print("got {:d} electrons".format(electrons)+" "*20+"\r", end=" ")
    
    data_tree.Fill()

data_tree.Write()    

root_file.Close()    
