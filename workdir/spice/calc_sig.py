#!/usr/bin/env python3

import numpy as np

from sigproc_kit import *
from avalanche_current import *
from apply_network import apply_network

#from my_utils import *

import sys
import json
import os
from ROOT import TFile, TBrowser, TH1F, TTree
from array import array
  
import matplotlib.pyplot as plt

import time as time_module
import pickle

lab_setup = False


if lab_setup:
  import rigol
  import lecroy
  import pasttrec_ctrl as ptc

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
  
  
  process_n_tracks = int(kwargs.get("process_n_tracks",0))
  write_analog_waveforms = int(kwargs.get("write_analog_waveforms",0))

  ### define main working time base

  sample_width = float(kwargs.get("sample_width",2e-6))
  delta_t = kwargs.get("delta_t", 0.1e-9)
  
  samples = int(sample_width/delta_t)

  time = np.linspace(0,sample_width,samples)
  
  hit_wire = kwargs.get("hit_wire",1)

  
  plot_n_tracks = int(kwargs.get("plot_n_tracks",10))
  plot_alpha_factor = float(kwargs.get("plot_alpha_factor",2))
  plot_alpha = float(kwargs.get("plot_alpha",0.5))
  plot_opt = kwargs.get("plot_opt",'b-')
  
  
  
  
  
  
  ##################################################
  ##        create short SPICE time vector        ##
  ##################################################
  
  spice_delta_t = kwargs.get("spice_delta_t", delta_t)
  spice_sample_width = kwargs.get("spice_sample_width", 400e-9)
  spice_samples = int(spice_sample_width/spice_delta_t)
  spice_time = np.linspace(0,spice_sample_width,spice_samples)
  spice_delta_pulse = gauss(spice_time,mu=10e-9,sigma=2*spice_delta_t)
  
  
  
  ##################################################
  ##        call SPICE, calculate cell IR         ##
  ##################################################
  
  cell_spice_conf = kwargs.get("cell_spice_conf","none")
  cell_spice_conf_json = get_file_json(cell_spice_conf)
  cell_configuration = cell_spice_conf_json["configuration"]
  cell_model         = cell_spice_conf_json["model"]
  
  dummy, v_cell_ir = apply_network(
        cell_model,
        spice_time,spice_delta_pulse,
        params=cell_configuration
        )
  
  ## resample from spice time (short sample) to global time (long sample)
  dummy, v_cell_ir = resample(time,spice_time,v_cell_ir) 
  
  
  ##################################################
  ##         call SPICE, calculate FEE IR         ##
  ##################################################

  fee_spice_conf = kwargs.get("fee_spice_conf","none")
  fee_spice_conf_json = get_file_json(fee_spice_conf)
  fee_configuration = fee_spice_conf_json["configuration"]
  fee_model         = fee_spice_conf_json["model"]
  
  delta_pulse = gauss(time,mu=10e-9,sigma=2*delta_t)
  
  dummy, v_fee_ir = apply_network(
        fee_model,
        time,delta_pulse,
        params=fee_configuration
        )
  
  #plt.plot(time,v_fee_ir)
  #plt.show()

  ##################################################
  ##        calculate avalanche current IR        ##
  ##################################################

  i_avalanche = avalanche_current(time, **cell_configuration) # pass dict cell_configuration as kwargs
  
  
  ##################################################
  ##        convolve avalanche and cell IR        ##
  ##################################################
 
  ava_c_cell_fft = fft_convolve(time,[i_avalanche,v_cell_ir])
  dummy, ava_c_cell_fft = shift_time(time, ava_c_cell_fft, -20e-9)
  ## shift back in time to compensate for the 10 ns offsets in both IRs
  
  ##################################################
  ##     convolve avalanche, cell and fee IR      ##
  ##################################################
  
  r_term_par = cell_configuration["r_term_par"]
  i_fee_in = ava_c_cell_fft/float(r_term_par)
 
  ava_c_cell_c_fee_fft = fft_convolve(time,[-i_fee_in,v_fee_ir])
  dummy, ava_c_cell_c_fee_fft = shift_time(time, ava_c_cell_c_fee_fft, -10e-9)
  ## shift back in time to compensate for the 10 ns offsets in fee ir
  
  #plt.plot(time,ava_c_cell_c_fee_fft)
  #plt.show()
  
    
  time_ns = time /1e-9
    
    #plt.plot(time_ns,v_meas, label="v(meas08)")
    #plt.plot(time_ns,218.5*ava_c_cell_fft, label="v(218.5*avalanche conv cell)")
    
    
  ##################################################
  ##        create signal output rootfile         ##
  ##################################################
    
  root_out = TFile("../ana_signals.root","RECREATE")
  root_out.cd()
  
  # create output root data structure
  
  scope_data_tree = TTree("scope_data_tree","scope_data_tree") 
  
  scope_data = {
    "track_start_x":'f',
    "track_start_y":'f',
    "track_start_z":'f',
    "track_end_x":'f',
    "track_end_y":'f',
    "track_end_z":'f',
    "evt":'i',
    "t1_a":'f',
    "tot_a":'f',
    "t1_b":'f',
    "tot_b":'f'
    }


  for key in scope_data:
    val_type = scope_data[key]
    scope_data[key] = array(val_type,[0]) # replace type definition with array placeholder
    scope_data_tree.Branch(key,scope_data[key],"{:s}/{:s}".format(key,val_type.upper()))
  
  ##################################################
  ##           open garfield root file            ##
  ##################################################
  
  f = TFile(garfield_root_file)
  tree = f.Get("data_tree")
  #tree.Draw("e_drift_t")
  
  a=TBrowser()
  
  ## variables that will be filled from root tree:
  last_evt = {}
  last_evt["evt"]           = 0
  last_evt["track_start_x"] = -1000
  last_evt["track_start_y"] = -1000
  last_evt["track_start_z"] = -1000
  last_evt["track_end_x"]   = -1000
  last_evt["track_end_y"]   = -1000
  last_evt["track_end_z"]   = -1000
  
  garfield_signal = []
  
  for i in range(0,2):
    garfield_signal += [np.zeros(len(time))]
  
  entries = tree.GetEntries()
  print("tree has {:d} entries".format(entries))
  
  
  ##################################################
  ##                init pasttrec                 ##
  ##################################################
  
  if lab_setup:
    ptc.init_board("0001",1,15,4,10) # no baseline correction, threshold 10
  
  # if you use baseline correction set it to baseline dac setting + 10!
  
  
  ##################################################
  ##             go process signals!              ##
  ##################################################

  
  processed_tracks = 0
  evt = -1
  
  pickle_data_list = []
  
  for i in range(0,entries+1):
    
    
    
    if i == entries:
      evt += 1 ## to trigger the last round of processing, when all entries from tree have been processed
    else:
      tree.GetEntry(i)
      evt = tree.evt
    
    # trigger processing if we moved to the next event
    if evt > last_evt["evt"]: 
      
      t1_a = -1000
      t1_b = -1000
      tot_a = -1000
      tot_b = -1000
      
      processed_tracks += 1
      print("new track at index {:d}".format(i))
      print("processed tracks: {:d}".format(processed_tracks))
      
      for w in range(0,2):
        if np.sum(garfield_signal[w]) > 0:
          v_cell_out        = fft_convolve(time,[ava_c_cell_fft,garfield_signal[w]])
          v_fee_ana_out     = fft_convolve(time,[ava_c_cell_c_fee_fft,garfield_signal[w]])
          
          thresh_mV = fee_configuration["thresh"]*fee_configuration["thresh_dac_step"]
          v_fee_discr_out, t1, tot   = discriminate(time,v_fee_ana_out,
                                           thresh_mV,
                                           fee_configuration["hysteresis"],
                                           fee_configuration["hyst_offset"]
                                           )
          v_fee_discr_out = v_fee_discr_out*0.8 - 0.4 ## mimic LVDS at 100R
          if plot_n_tracks and (processed_tracks <= plot_n_tracks):
            plt.plot(time_ns,v_cell_out*1e3, plot_opt, label="signal {:03d}".format(processed_tracks), alpha=plot_alpha )
            
          ## write to root file
          root_out.cd()
          if (w == 0) and write_analog_waveforms: 
            # only write out waveform for wire 1 (0th array index), the fish partner wire is less important
            t1_sig_hist       = TH1F("garfield_sig_{:08d}".format(processed_tracks),
                                     "garfield_sig_{:08d}".format(processed_tracks),
                                     samples,0,sample_width)
            cell_ana_sig_hist = TH1F("cell_ana_sig_{:08d}".format(processed_tracks),
                                     "cell_ana_sig_{:08d}".format(processed_tracks),
                                     samples,0,sample_width)
            fee_ana_sig_hist = TH1F("fee_ana_sig_{:08d}".format(processed_tracks),
                                     "fee_ana_sig_{:08d}".format(processed_tracks),
                                     samples,0,sample_width)
            fee_discr_sig_hist = TH1F("fee_discr_sig_{:08d}".format(processed_tracks),
                                     "fee_discr_sig_{:08d}".format(processed_tracks),
                                     samples,0,sample_width)
            for i in range(0,samples):
              t1_sig_hist.SetBinContent(i+1,garfield_signal[w][i])
              cell_ana_sig_hist.SetBinContent(i+1,v_cell_out[i])
              fee_ana_sig_hist.SetBinContent(i+1,v_fee_ana_out[i])
              fee_discr_sig_hist.SetBinContent(i+1,v_fee_discr_out[i])
            
            pickle_data_list += [ 
                {
                  "garfield_signal":garfield_signal.copy(),
                  "v_cell_out":v_cell_out.copy(),
                  "v_fee_ana_out":v_fee_ana_out.copy(),
                  "v_fee_discr_out":v_fee_discr_out.copy(),
                  "time":time,
                  "t1":t1.copy(),
                  "tot":tot.copy()
                }
              ]
            
            t1_sig_hist.Write()
            cell_ana_sig_hist.Write()
            fee_ana_sig_hist.Write()
            fee_discr_sig_hist.Write()
        
          # clear the accumulator vector again
          garfield_signal[w] = np.zeros(len(time)) # clear accumulator
        
          
          if lab_setup:
            ##################################################
            ##              send signal to AWG              ##
            ##################################################
            # v_cell_out is voltage at parallel resistance
            r_term_par = cell_configuration["r_term_par"]
            i_in = v_cell_out/float(r_term_par)
            # use 50k to convert between AWG voltage to FEE input current
            r_cur_src = 32.8e3
            awg_volt = r_cur_src * i_in
            rigol.set_waveform(1,time,awg_volt,v_range=3)
            time_module.sleep(0.05)
            
            measure_statistics = lecroy.measure_statistics(["P3","P4"],3)
            
            measure_statistics["P3"].sort() ## median filter against noisy outlies
            measure_statistics["P4"].sort() ## 
            
            if w == 0:
              t1_a  = measure_statistics["P3"][1] ## middle element of sorted list
              tot_a = measure_statistics["P4"][1]
            else:
              t1_b  = measure_statistics["P3"][1] ## middle element of sorted list
              tot_b = measure_statistics["P4"][1]
              
          else: ## we use PASTTREC model
            if w == 0:
              t1_a  = t1
              tot_a = tot
            else:
              t1_b  = t1
              tot_b = tot
            
            
      
      scope_data["t1_a"][0]  = t1_a
      scope_data["tot_a"][0]  = tot_a
      scope_data["t1_b"][0]  = t1_b
      scope_data["tot_b"][0]  = tot_b
      scope_data["evt"][0] = last_evt["evt"]
      
      scope_data["track_start_x"][0] = last_evt["track_start_x"]
      scope_data["track_start_y"][0] = last_evt["track_start_y"]
      scope_data["track_start_z"][0] = last_evt["track_start_z"]
      scope_data["track_end_x"][0]   = last_evt["track_end_x"]
      scope_data["track_end_y"][0]   = last_evt["track_end_y"]
      scope_data["track_end_z"][0]   = last_evt["track_end_z"]
      
      scope_data_tree.Fill()
      if last_evt["evt"] % 1000 == 0:
        scope_data_tree.Write()
    
      ##################################################
      
      
      
    if(tree.hit_wire > 0 and tree.hit_wire <= 2 ): # we hit the selected sense wire (default = 1)
      index = int(tree.e_drift_t/delta_t)
      garfield_signal[tree.hit_wire-1][index] += 1/delta_t # fill one unit of particle into sample time slice
    
    
    
    last_evt["evt"] = tree.evt
    last_evt["track_start_x"] = tree.track_start_x
    last_evt["track_start_y"] = tree.track_start_y
    last_evt["track_start_z"] = tree.track_start_z
    last_evt["track_end_x"]   = tree.track_end_x
    last_evt["track_end_y"]   = tree.track_end_y
    last_evt["track_end_z"]   = tree.track_end_z
    
    
    if (process_n_tracks > 0) and processed_tracks >= process_n_tracks:
      break
    
  
  
  
  #### load garfield signal ###
  #garfield_x, garfield_y = load_and_resample("00_garfield_signal/Fe55_kernel.csv",time)
  #garfield_y = normalize_dt(garfield_x,garfield_y) # normalize as if we had one charge

  #### load cell impulse response ###
  #dummy, i_cell = load_and_resample("02_cell_response_function/ir_current.csv", time)

  ### load a measurement ###
  #dummy, v_meas = load_and_resample("meas08_resampled.txt", time, x_offset=-299e-9+40e-9)



  #root_out.Close()

  if plot_n_tracks:
    
    plt.xlabel("time (ns)")
    plt.ylabel("voltage (mV)")
    
    #plt.legend() # order a legend.
    plt.show()
    
    
  scope_data_tree.Write()
  root_out.Close()
  
  picklefile = "../{:s}.pickle".format("ana_signals")
  print("saving to "+picklefile)
  pickle.dump(pickle_data_list,open(picklefile,'wb'))
  
  

if __name__=='__main__':
    calc_sig( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
