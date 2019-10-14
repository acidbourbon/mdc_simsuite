#!/bin/bash

mkdir -p $(jupyter --data-dir)/nbextensions
cp /opt/jupyter_vim_binding $(jupyter --data-dir)/nbextensions/vim_binding

#uncomment the following lines if you want vim-bindings in your notebooks
# jupyter nbextension disable vim_binding/vim_binding
jupyter nbextension enable vim_binding/vim_binding

jupyter notebook --port 8888 --no-browser --ip 0.0.0.0 --NotebookApp.token=''
