

import sys
import tempfile
import os
import conf
import json

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
  
  code, selection = d.checklist("select FIELD options", choices=choices)
  if code == d.OK:
    conf.set_field_options(selection)
  
  
  
  #, width=width, height=height, list_height=list_height)
