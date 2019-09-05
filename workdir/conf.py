import os
import json

root_dir   = "./"
conf_file = "conf.json"

cells_dir  = root_dir+"/"+"cells"


def dump(obj):
  print( json.dumps(obj,indent=2,sort_keys=True)   )

def create_empty_conf():
  write_conf_json({
    "selected_cell" : None,
    "field_options" : []
    #"cells" : [{"name":"dummy","conf":{}}]
    })


def get_selected_cell():
  conf = get_conf_json()
  if conf["selected_cell"] is None:
    return "none"
  else:
    return conf["selected_cell"]
  
def set_selected_cell(name):
  conf = get_conf_json()
  conf["selected_cell"] = name
  write_conf_json(conf)
  



def get_field_options():
  conf = get_conf_json()
  return conf["field_options"]

def set_field_options(options):
  conf = get_conf_json()
  conf["field_options"] = options
  write_conf_json(conf)

def get_conf_json():
  if ( os.path.isfile(root_dir+"/"+conf_file) == False ) :
    create_empty_conf()
  return get_file_json(root_dir+"/"+conf_file)


def write_conf_json(conf):
  write_file_json(root_dir+"/"+conf_file,conf)
  
  
  
  
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

  
def get_cell_conf(name):
  
  
  if name in list_cells():
    return get_file_json(cells_dir+"/"+name+".json")
  ## could not find it
  raise NameError("could not find cell with name {:s}".format(name))


def list_dir(dir,**kwargs):
  ext = kwargs.get("ext","")
  files = os.listdir(dir) # returns list
  names = [] 
  for file in files:
    if ext in file:
      names += [file.replace(ext,"") ]
    
  names.sort()
  return names
  
def list_cells():
  return list_dir(cells_dir,ext=".json")
    

#def copy_cell(src_name,dest_name):
  #conf = get_conf_json()
  #cells = conf["cells"]

  #src_conf = get_cell_conf(src_name)
  #new_cell(dest_name,conf=src_conf)
  
  
#def remove_cell(name):
  #conf = get_conf_json()
  #cells = conf["cells"]
  #for cell in cells:
    #if cell["name"] == name:
      #cells.remove(cell)
      #write_conf_json(conf)
      #return
  ### could not find it
  #raise NameError("could not find cell with name {:s}".format(name))
  
