#!/usr/bin/env python3

import sys
import locale
import time

from dialog import Dialog

import conf
from dialogs import *

from run_garfield import *

# This is almost always a good thing to do at the beginning of your programs.
locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

                
mm_tag = ""
                
while True:

  menu_title_width = 20

  if mm_tag == "":
    code, tag = d.menu("main menu", height="30", menu_height="28",
      choices = [
                 ("","---   CELL       ---"),
                 ("01","selected: {:s}".format(conf.get_selected_cell())),
                 ("","---   FIELD      ---"),
                 ("02","set field options"),
                 ("","---   MAGNETIC   ---"),
                 ("06","set magnetic options"),
                 ("","---   GAS        ---"),
                 ("08","select gas"),
                 ("","---   DRIFT      ---"),
                 ("07","set drift options"),
                 ("",""),
                 ("","--- run GARFIELD ---"),
                 ("03","run with graphics output"),
                 ("04","run w/o graphics"),
                 ("05","only create garfield_in.txt"),
                 ("",""),
                 ("","---   analysis   ---"),
                 ("09","run macro on data"),
                 ("",""),
                 ("","---   SPICE   ---"),
                 ("11","select cell spice conf"),
                 ("10","edit circuit model in LTSpice"),
                 ("12","calc ana. signals from GARFIELD data"),
                 ("",""),
                 ("",""),
                 ("z","exit")] )
    #if code == d.OK:
      #mm_tag = tag



  #if mm_tag == "m1":
    

    
    #code, tag = d.menu("cell menu", height="30", menu_height="28",
    #choices = [
               #("01","selected: {:s}".format(conf.get_selected_cell())),
              #])




  if code == d.OK:
    
    if tag == "01":
      code, tag = dialog_cell_list()
      if code == d.OK:
        name = tag
        conf.set_selected_cell(name)
        
    if tag == "02":
      dialog_field_checklist()
    if tag == "06":
      dialog_magnetic_checklist()
    if tag == "07":
      dialog_drift_checklist()
    if tag == "08":
      dialog_gas_checklist()
    
    #if tag == "01":
      
    if tag == "03":
      run_garfield(show_graphics=True,dryrun=False)
      
    if tag == "04":
      run_garfield(show_graphics=False,dryrun=False)
      
    if tag == "05":
      run_garfield(show_graphics=False,dryrun=True)
      d.infobox("created garfield_in.txt", width=0, height=0, title="done")
      time.sleep(2)
      
    if tag == "09":
      while True:
        code, tag = dialog_ana_menu()
        if code == d.OK:
          os.system("./ana/{:s}".format(tag))
        else:
          break
        
    if tag == "10":
      while True:
        code, tag = dialog_asc_menu()
        if code == d.OK:
          os.system("wine /LTspiceXVII/XVIIx64.exe cell_spice/{:s}".format(tag))
        else:
          break
      
    if tag == "11":
      dialog_spice_conf()
      
    if tag == "12":
      os.system("cd cell_spice;  ./calc_sig.py cell_spice_conf={:s}".format(conf.get_cell_spice_conf()))
      # break until any key press
      dummy=sys.stdin.readline()
      
    if tag == "z":
      exit()
    
      
  else:
    if mm_tag == "": #already in the main menu
      d.infobox("Bye bye...", width=0, height=0, title="This is the end")
      exit()
    mm_tag = ""
      

############################    end of main menu loop ##################################

#code, tag = d.menu("MDC 3d Garfield main menu",
                   #choices=[("01", "select cell"),
                            #("02", "Item text 2"),
                            #("03", "Item text 3")])

#if codes == d.OK:
  #if tag == "01"


#if code == d.ESC:
    #d.msgbox("You got out of the menu by pressing the Escape key.")
#else:
    #text = "You got out of the menu by choosing the {} button".format(
        #button_names[code])

    #if code != d.CANCEL:
        #text += ", and the highlighted entry at that time had tag {!r}".format(
        #tag)

    #d.msgbox(text + ".", width=40, height=10)

#d.infobox("Bye bye...", width=0, height=0, title="This is the end")
#time.sleep(2)

#sys.exit(0)
