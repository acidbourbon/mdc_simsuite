#!/usr/bin/env python3

import numpy as np

from sigproc_kit import *
from apply_network import apply_network

import sys
import json
import os
from ROOT import TFile, TBrowser, TH1F
from scipy import interpolate
  
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit



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





def func(x, pktime, gain_correction, TCR1, TCC1, TCR2, TCC2):
  #print("called func with x of size {:d}".format(len(x)))
  #print("pktime: {:e}, gain_correction: {:e}".format(pktime,gain_correction))
  
  
  test_curr = 9.146e-6
  spice_sample_width = 1000e-9
  spice_delta_t = 0.5e-9
  spice_samples = int(spice_sample_width/spice_delta_t)
  spice_time = np.linspace(0,spice_sample_width,spice_samples)
  heavi_test_y = 0 + test_curr*(spice_time>10e-9)*(spice_time<459e-9)
    
  fee_conf = "pasttrec_pkt15ns.fee.json"
  fee_conf_json = get_file_json(fee_conf)
  
  configuration = fee_conf_json["configuration"]
  model         = fee_conf_json["model"]
  
  configuration["pktime"] = pktime
  configuration["gain_correction"] = gain_correction
  configuration["TCR1"] = TCR1
  configuration["TCC1"] = TCC1
  configuration["TCR2"] = TCR2
  configuration["TCC2"] = TCC2
    
  dummy, v_fee_heavi_y = apply_network(
          model,
          spice_time,heavi_test_y,
          params=configuration
          )

  f = interpolate.interp1d(spice_time,v_fee_heavi_y,bounds_error=False, fill_value=0.)
  output = f(x/1e9)
  return output.astype(np.float32)

def test(**kwargs):
  
  
  
  model_ir = True
  model_heavi = True
  fit_heavi = False
  
  
  
  ##################################################
  ##           call SPICE, generate IR            ##
  ##################################################
  
  ### only process short time sample with SPICE
  fee_conf = "pasttrec_pkt15ns.fee.json"
  fee_conf_json = get_file_json(fee_conf)
  
  configuration = fee_conf_json["configuration"]
  model         = fee_conf_json["model"]
  
  
  
  
  spice_delta_t = kwargs.get("spice_delta_t", 0.1e-9)
  spice_sample_width = kwargs.get("spice_sample_width", 1000e-9)
  spice_samples = int(spice_sample_width/spice_delta_t)
  spice_time = np.linspace(0,spice_sample_width,spice_samples)
  spice_delta_pulse = gauss(spice_time,mu=10e-9,sigma=2*spice_delta_t)
  
  
  if model_ir:
    
    dummy, v_fee_ir = apply_network(
          model,
          spice_time,spice_delta_pulse,
          params=configuration
          )
    
    #dummy, v_fee_ir = resample(time,spice_time,v_fee_ir) ## resample from spice time (short sample) to global time (long sample)

    v_fee_ir = normalize_max(v_fee_ir)
    #v_fee_ir = normalize_dt(spice_time,v_fee_ir)
    
    m_ir_x, m_ir_y = read_csv("measured_ir/ir_direct.csv")
    m_ir_y = normalize_max(m_ir_y)
    #m_ir_y = normalize_dt(m_ir_x,m_ir_y)
    
    # plot?
    if True:
      
      plt.plot(m_ir_x*1e9-65.9,m_ir_y,label="measured direct IR")
      plt.plot(spice_time*1e9-10,v_fee_ir,label="spice_IR")
      plt.xlabel("time (ns)")
      plt.ylabel("voltage (V)")
      
      plt.legend() # order a legend.
      plt.show()
    
    
  
  if model_heavi:
  
    
    m_heavi_x, m_heavi_y = read_csv("measured_ir/ir_int.csv")
    baseline = np.mean(m_heavi_y[0:int(len(m_heavi_y)/10)])
    m_heavi_y -= baseline
    

    
    test_curr = 9.146e-6
    heavi_test_y = 0 + test_curr*(spice_time>10e-9)*(spice_time<459e-9)
    
    dummy, v_fee_heavi_y = apply_network(
          model,
          spice_time,heavi_test_y,
          params=configuration
          )

    
    # plot?
    if True:
      
      plt.plot(m_heavi_x*1e9-65.9,m_heavi_y,label="measured PT heaviside reaction")
      plt.plot(spice_time*1e9-10,v_fee_heavi_y,label="simulated PT heaviside reaction")
      plt.xlabel("time (ns)")
      plt.ylabel("voltage (V)")
      
      plt.legend() # order a legend.
      plt.show()
      
    if fit_heavi:
      # make a fit
      m_heavi_x-=55.9e-9
      
      popt0 =  [  configuration["pktime"],
                  configuration["gain_correction"],
                  configuration["TCR1"],
                  configuration["TCC1"],
                  configuration["TCR2"],
                  configuration["TCC2"]
                  ]
      
      m_heavi_x*=1e9
      
      xdata = m_heavi_x.astype(np.float32)
      ydata = m_heavi_y.astype(np.float32)
      
      popt, pcov = curve_fit(func, xdata, ydata, p0=popt0)
      print("popt:")
      print(popt)
      print("pcov:")
      print(pcov)
      plt.plot(m_heavi_x,m_heavi_y,label="measurement")
      plt.plot(m_heavi_x,func(m_heavi_x, *popt),label="fit")
      
      plt.legend()
      plt.show()
             
    
    
  
  

if __name__=='__main__':
    test( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
