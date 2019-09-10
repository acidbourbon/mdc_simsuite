#!/usr/bin/env python3

import numpy as np

from sigproc_kit import *
from avalanche_current import *
from apply_network import apply_network

import sys
import json
import os


def get_file_json(name):
  if os.path.isfile(name) :
    fh = open(name,"r")
    obj= json.load(fh)
    fh.close()
    return obj
  raise NameError("file {:s} does not exist".format(name))

def write_file_json(name,obj):
  fh = open(name,"w")
  json.dump(obj,fh,indent=2,sort_keys=True)
  fh.close()


def write_csv(filename,data_x,data_y):
  with open(filename,"w") as f:
    for i in range(0,len(data_x)):
      f.write("{:E}\t{:E}\n".format(data_x[i],data_y[i]))
    f.close()

def gauss(x, **kwargs):
  mu = kwargs.get("mu",0)
  sigma = kwargs.get("sigma",1)
  A = kwargs.get("A",1./(sigma*(2.*np.pi)**0.5)) ## default amplitude generates bell curve with area = 1
  return A*np.exp(-(x-mu)**2/(2.*sigma**2))







def calc_sig(**kwargs):
  
  
  garfield_root_file = kwargs.get("garfield_root_file","../drift_data.root")

  ### define main working time base

  sample_width = kwargs.get("sample_width",2e-6)
  delta_t = kwargs.get("delta_t", 0.1e-9)
  
  samples = int(sample_width/delta_t)

  time = np.linspace(0,sample_width,samples)
  
  hit_wire = kwargs.get("hit_wire",1)

  cell_spice_conf = kwargs.get("cell_spice_conf","none")
  
  cell_spice_conf_json = get_file_json(cell_spice_conf)
  
  configuration = cell_spice_conf_json["configuration"]
  model         = cell_spice_conf_json["model"]
  
  ## approximate delta pulse with narrow gaussian at t=10ns
  #delta_pulse = gauss(time,mu=10e-9,sigma=2*delta_t)
  
  
  
  ##################################################
  ##           call SPICE, generate IR            ##
  ##################################################
  
  ### only process short time sample with SPICE
  
  spice_delta_t = kwargs.get("spice_delta_t", delta_t)
  spice_sample_width = kwargs.get("spice_sample_width", 400e-9)
  spice_samples = int(spice_sample_width/delta_t)
  spice_time = np.linspace(0,spice_sample_width,spice_samples)
  spice_delta_pulse = gauss(spice_time,mu=10e-9,sigma=2*delta_t)
  
  dummy, v_cell_ir = apply_network(
        model,
        spice_time,spice_delta_pulse,
        params=configuration
        )
  
  dummy, v_cell_ir = resample(time,spice_time,v_cell_ir) ## resample from spice time (short sample) to global time (long sample)




  ### generate avalanche current response model ###
  i_avalanche = avalanche_current(time, **configuration) # pass dict configuration as kwargs
  
  
  
  
  #### load garfield signal ###
  #garfield_x, garfield_y = load_and_resample("00_garfield_signal/Fe55_kernel.csv",time)
  #garfield_y = normalize_dt(garfield_x,garfield_y) # normalize as if we had one charge

  #### load cell impulse response ###
  #dummy, i_cell = load_and_resample("02_cell_response_function/ir_current.csv", time)

  ### load a measurement ###
  dummy, v_meas = load_and_resample("meas08_resampled.txt", time, x_offset=-299e-9+40e-9)

  ava_c_cell_fft = fft_convolve(time,[i_avalanche,v_cell_ir])
  dummy, ava_c_cell_fft = shift_time(time, ava_c_cell_fft, 25e-9)

  #ava_c_cell_c_gar_fft = fft_convolve(time,[i_avalanche,i_cell,garfield_y])
  #dummy, ava_c_cell_c_gar_fft = shift_time(time, ava_c_cell_c_gar_fft, -32.5e-9+40e-9)


  if True:
    import matplotlib.pyplot as plt
    
    time_ns = time /1e-9
    
    plt.plot(time_ns,v_meas, label="v(meas08)")
    plt.plot(time_ns,218.5*ava_c_cell_fft, label="v(218.5*avalanche conv cell)")
    
    plt.xlabel("time (ns)")
    plt.ylabel("voltage (V)")
    
    plt.legend() # order a legend.
    plt.show()
    
    
  
  

if __name__=='__main__':
    calc_sig( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
