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
                 ("","---     CELL      ---"),
                 ("01","selected: {:s}".format(conf.get_selected_cell())),
                 ("",""),
                 ("","---     FIELD     ---"),
                 ("02","set plot options"),
                 ("",""),
                 ("","---  run GARFIELD ---"),
                 ("03","run with graphics output"),
                 ("04","run w/o graphics"),
                 ("05","only create garfield_in.txt"),
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
        #cell_conf = conf.get_cell_conf(cell_name)
        #d.infobox("", width=0, height=0, title="This is the end")
        #time.sleep(1)
    if tag == "02":
      dialog_field_checklist()
      #print(selection)
      #d.infobox(conf.dump(selection), width=0, height=0, title="")
      #time.sleep(2)
    
    #if tag == "01":
      
    if tag == "03":
      run_garfield(show_graphics=True,dryrun=False)
      
    if tag == "04":
      run_garfield(show_graphics=False,dryrun=False)
      
    if tag == "05":
      run_garfield(show_graphics=False,dryrun=True)
      d.infobox("created garfield_in.txt", width=0, height=0, title="done")
      time.sleep(2)
      
        
      
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
