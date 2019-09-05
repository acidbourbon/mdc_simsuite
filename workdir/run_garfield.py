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
  
  gen_MDC_cell()  ## this creates CELL.txt
 
 
  ####### create FIELD.txt ############ 
 
  os.system("> FIELD.txt")
  
  with open("FIELD.txt","a") as f:
    print("&FIELD",file=f)
    print("opt nodebug",file=f)
    print("",file=f)
    f.close()
    
  for entry in conf.get_field_options():
    os.system("cat field/{:}.txt >> FIELD.txt".format(entry))
    
  
  
  # unite command files
  os.system("cat CELL.txt FIELD.txt >> garfield_in.txt")
  
  
  # call garfield
  if(not(dryrun)):
    os.system("export LD_LIBRARY_PATH=\"./\"; ./garfield-9 < garfield_in.txt")

  # view graphical output
  if show_graphics:
    os.system("ps2pdf {:s}; gv {:s} ".format(plot_out,plot_out.replace(".ps",".pdf")))


if __name__=='__main__':
  run_garfield( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
