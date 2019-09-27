#!/usr/bin/env python3

import numpy as np

from sigproc_kit import *
from avalanche_current import *
from apply_network import apply_network

import sys
import json
import os
from ROOT import TFile, TBrowser, TH1F
  
import matplotlib.pyplot as plt

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
  
  plot_n_tracks = int(kwargs.get("plot_n_tracks",10))
  plot_alpha_factor = float(kwargs.get("plot_alpha_factor",2))
  plot_alpha = float(kwargs.get("plot_alpha",plot_alpha_factor*1/plot_n_tracks))
  plot_opt = kwargs.get("plot_opt",'b-')
  
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
  spice_samples = int(spice_sample_width/spice_delta_t)
  spice_time = np.linspace(0,spice_sample_width,spice_samples)
  spice_delta_pulse = gauss(spice_time,mu=10e-9,sigma=2*spice_delta_t)
  
  dummy, v_cell_ir = apply_network(
        model,
        spice_time,spice_delta_pulse,
        params=configuration
        )
  
  dummy, v_cell_ir = resample(time,spice_time,v_cell_ir) ## resample from spice time (short sample) to global time (long sample)




  ### generate avalanche current response model ###
  i_avalanche = avalanche_current(time, **configuration) # pass dict configuration as kwargs
  
  
  ##################################################
  ##        convolve avalanche and cell IR        ##
  ##################################################
 
  ava_c_cell_fft = fft_convolve(time,[i_avalanche,v_cell_ir])
  dummy, ava_c_cell_fft = shift_time(time, ava_c_cell_fft, -20e-9) ## shift back in time to compensate for the 10 ns offsets in both IRs
  
  
    
  time_ns = time /1e-9
    
    #plt.plot(time_ns,v_meas, label="v(meas08)")
    #plt.plot(time_ns,218.5*ava_c_cell_fft, label="v(218.5*avalanche conv cell)")
    
    
  ##################################################
  ##        create signal output rootfile         ##
  ##################################################
    
  root_out = TFile("../ana_signals.root","RECREATE")
  root_out.cd()
  
  ##################################################
  ##           open garfield root file            ##
  ##################################################
  
  f = TFile(garfield_root_file)
  tree = f.Get("data_tree")
  #tree.Draw("e_drift_t")
  
  a=TBrowser()
  
  ## variables that will be filled from root tree:
  last_evt = 0
  
  garfield_signal = np.zeros(len(time))
  
  entries = tree.GetEntries()
  print("tree has {:d} entries".format(entries))
  
  processed_tracks = 0
  
  for i in range(0,entries+1):
    
    if i == entries:
      evt += 1 ## to trigger the last round of processing, when all entries from tree have been processed
    else:
      tree.GetEntry(i)
      evt = tree.evt
    
    
    if evt > last_evt: 
      ava_c_cell_c_garfield_fft = fft_convolve(time,[ava_c_cell_fft,garfield_signal])
      processed_tracks += 1
      print("new track at index {:d}".format(i))
      print("processed tracks: {:d}".format(processed_tracks))
      if plot_n_tracks and processed_tracks <= plot_n_tracks:
        plt.plot(time_ns,ava_c_cell_c_garfield_fft*1e3, plot_opt, label="signal {:03d}".format(processed_tracks), alpha=plot_alpha )
        
      ## write to root file
      root_out.cd()
      t1_sig_hist = TH1F("t1_sig_{:08d}".format(processed_tracks),"t1_sig_{:08d}".format(processed_tracks),samples,0,sample_width)
      ana_sig_hist = TH1F("ana_sig_{:08d}".format(processed_tracks),"ana_sig_{:08d}".format(processed_tracks),samples,0,sample_width)
      for i in range(0,samples):
        t1_sig_hist.SetBinContent(i+1,garfield_signal[i])
        ana_sig_hist.SetBinContent(i+1,ava_c_cell_c_garfield_fft[i])
        
      t1_sig_hist.Write()
      ana_sig_hist.Write()
      
      # clear the accumulator vector again
      garfield_signal = np.zeros(len(time)) # clear accumulator
      
      
      
    if(tree.hit_wire == hit_wire): # we hit the selected sense wire (default = 1)
      index = int(tree.e_drift_t/delta_t)
      garfield_signal[index] += 1/delta_t # fill one unit of particle into sample time slice
    
    
    
    last_evt = tree.evt
    
    
    
  
  
  
  #### load garfield signal ###
  #garfield_x, garfield_y = load_and_resample("00_garfield_signal/Fe55_kernel.csv",time)
  #garfield_y = normalize_dt(garfield_x,garfield_y) # normalize as if we had one charge

  #### load cell impulse response ###
  #dummy, i_cell = load_and_resample("02_cell_response_function/ir_current.csv", time)

  ### load a measurement ###
  dummy, v_meas = load_and_resample("meas08_resampled.txt", time, x_offset=-299e-9+40e-9)



  #root_out.Close()

  if plot_n_tracks:
    
    plt.xlabel("time (ns)")
    plt.ylabel("voltage (mV)")
    
    #plt.legend() # order a legend.
    plt.show()
    
    
  
  

if __name__=='__main__':
    calc_sig( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
