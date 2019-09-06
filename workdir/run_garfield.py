#!/usr/bin/env python3

import os
from gen_MDC_cell import gen_MDC_cell
import sys
import conf



def run_garfield(**kwargs):
  
  plot_out = kwargs.get("plot_out","view.ps")
  
  dryrun = int(kwargs.get("dryrun",0))
  
  show_graphics = int(kwargs.get("show_graphics",1))
  
  
  
  # create new garfield_in.txt
  os.system("> garfield_in.txt")
  
  # load init settings
  os.system("cat garfinit.txt >> garfield_in.txt")
 
  # set plot output
  with open("garfield_in.txt","a") as f:
    print("!add meta type PostScript file-name \"{:s}\"".format(plot_out), file=f)
    print("!open meta", file=f)
    print("!act meta", file=f)
    print("", file=f)
    f.close()
    
  ####### create CELL.txt ############ 
  
  cell_conf = conf.get_cell_conf(conf.get_selected_cell())
  gen_MDC_cell(**cell_conf) 
 
 
  ####### create FIELD.txt ############ 
 
  os.system("> FIELD.txt")
  
  os.system("cat field/section_head >> FIELD.txt")
  for entry in conf.get_field_options():
    if ".txt" in entry:
      os.system("cat field/{:} >> FIELD.txt".format(entry))
    if ".sh" in entry:
      os.system("sh field/{:} >> FIELD.txt".format(entry))
    
  ####### create MAGNETIC.txt ############ 
 
  os.system("> MAGNETIC.txt")
  
  os.system("cat magnetic/section_head >> MAGNETIC.txt")
  for entry in conf.get_magnetic_options():
    if ".txt" in entry:
      os.system("cat magnetic/{:} >> MAGNETIC.txt".format(entry))
    if ".sh" in entry:
      os.system("sh magnetic/{:} >> MAGNETIC.txt".format(entry))
      
  ####### create GAS.txt ############ 
 
  os.system("> GAS.txt")
  
  entry = conf.get_gas_options()
  os.system("cat gas/{:} >> GAS.txt".format(entry))
    
  ####### create DRIFT.txt ############ 
 
  os.system("> DRIFT.txt")
  
  os.system("cat drift/section_head >> DRIFT.txt")
  for entry in conf.get_drift_options():
    if ".txt" in entry:
      os.system("cat drift/{:} >> DRIFT.txt".format(entry))
    if ".sh" in entry:
      os.system("sh drift/{:} >> DRIFT.txt".format(entry))
    
    
  
  if not(show_graphics):
    # disable all LINE-PLOT commands
    os.system("perl -pi -e 's/ LINE-PLOT/ /g;' DRIFT.txt")
    os.system("perl -pi -e 's/DRIFT TRACK(.*)$/DRIFT TRACK $1 NOLINE-PLOT/g;' DRIFT.txt")
  
  # unite command files
  os.system("cat CELL.txt FIELD.txt MAGNETIC.txt GAS.txt DRIFT.txt >> garfield_in.txt")
  
    
  
  
  # call garfield
  if(not(dryrun)):
    #os.system("export LD_LIBRARY_PATH=\"./\"; ./garfield-9 < garfield_in.txt | tee garfield_out.txt")
    print("starting garfield, reading garfield_in.txt")
    os.system("export LD_LIBRARY_PATH=\"./\"; ./garfield-9 < garfield_in.txt | ./slurp_garfield_out.py")

  # view graphical output
  if show_graphics:
    os.system("ps2pdf {:s}; gv {:s} ".format(plot_out,plot_out.replace(".ps",".pdf")))
    
  os.system("rm {:s}".format(plot_out))






if __name__=='__main__':
  run_garfield( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
