

import sys
import tempfile
import os
import conf
import json

import time

from dialog import Dialog


def dialog_editbox(in_text,**kwargs):

  background_title = kwargs.get("background_title","background_title") 
  
  dummy, temp_path = tempfile.mkstemp()
  print( temp_path )

  f = open(temp_path, 'w')
  f.write( in_text)
  f.write("\n")
  f.close()

  d = Dialog(dialog="dialog")
  d.set_background_title(background_title)

  code, text = d.editbox(temp_path)
  os.remove(temp_path)
  return (code, text)


def edit_obj_json(obj):
  code, text = dialog_editbox(json.dumps(obj,indent=2,sort_keys=True))
  d = Dialog(dialog="dialog")
  if code == d.OK:
    return json.loads(text)
  else:
    return obj
  
  
  
def dialog_cell_list():

  d = Dialog(dialog="dialog")
  d.set_background_title("select a cell")
  
  choices = []

  for name in conf.list_cells():
    choices += [(name, "")]

  return d.menu("select a cell:", choices= choices )


def dialog_field_checklist():
  d = Dialog(dialog="dialog")
  d.set_background_title("FIELD section options")
  
  field_options = conf.get_field_options()
  
  choices = []
  
  for entry in conf.list_dir("./field",ext=".txt"):
    choices+= [(entry,"",(entry in field_options))]
  for entry in conf.list_dir("./field",ext=".sh"):
    choices+= [(entry,"",(entry in field_options))]
  
  if len(choices):
    code, selection = d.checklist("select FIELD options", choices=choices)
    if code == d.OK:
      conf.set_field_options(selection)
  else:
    d.infobox("no option files in ./field", width=0, height=0, title="done")
    time.sleep(2)
    
def dialog_magnetic_checklist():
  d = Dialog(dialog="dialog")
  d.set_background_title("MAGNETIC section options")
  
  magnetic_options = conf.get_magnetic_options()
  
  choices = []
  
  for entry in conf.list_dir("./magnetic",ext=".txt"):
    choices+= [(entry,"",(entry in magnetic_options))]
  for entry in conf.list_dir("./magnetic",ext=".sh"):
    choices+= [(entry,"",(entry in magnetic_options))]
    
  if len(choices):
    code, selection = d.checklist("select MAGNETIC options", choices=choices)
    if code == d.OK:
      conf.set_magnetic_options(selection)
  else:
    d.infobox("no option files in ./magnetic", width=0, height=0, title="done")
    time.sleep(2)
  
  
def dialog_drift_checklist():
  d = Dialog(dialog="dialog")
  d.set_background_title("DRIFT section options")
  
  drift_options = conf.get_drift_options()
  
  choices = []
  
  for entry in conf.list_dir("./drift",ext=".txt"):
    choices+= [(entry,"",(entry in drift_options))]
  for entry in conf.list_dir("./drift",ext=".sh"):
    choices+= [(entry,"",(entry in drift_options))]
    
  if len(choices):
    code, selection = d.checklist("select DRIFT options", choices=choices)
    if code == d.OK:
      conf.set_drift_options(selection)
  else:
    d.infobox("no option files in ./drift", width=0, height=0, title="done")
    time.sleep(2)
    
def dialog_gas_checklist():
  d = Dialog(dialog="dialog")
  d.set_background_title("GAS section options")
  
  gas_options = conf.get_gas_options()
  
  choices = []
  
  for entry in conf.list_dir("./gas",ext=".txt"):
    choices+= [(entry,"",(entry in gas_options))]
  #for entry in conf.list_dir("./gas",ext=".sh"):
    #choices+= [(entry,"",(entry in gas_options))]
    
  if len(choices):
    code, selection = d.radiolist("select GAS options", choices=choices)
    if code == d.OK:
      conf.set_gas_options(selection)
  else:
    d.infobox("no option files in ./gas", width=0, height=0, title="done")
    time.sleep(2)
  
  
  #, width=width, height=height, list_height=list_height)
