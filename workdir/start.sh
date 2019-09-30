#!/bin/bash


tmux new -d -s main

tmux new-window -t main -n "menu" "./menu.py; clear; echo enter ./menu.py to start menu again ... here is a shell ; /bin/bash"

tmux new-window -t main -n "tab2" "/bin/bash"
tmux new-window -t main -n "tab3" "/bin/bash"
tmux new-window -t main -n "tab4" "/bin/bash"
tmux new-window -t main -n "tab5" "/bin/bash"
tmux new-window -t main -n "tab6" "/bin/bash"
tmux new-window -t main -n "tab7" "/bin/bash"
tmux new-window -t main -n "tab8" "/bin/bash"

tmux new-window -t main -n "jupyter" "cd jupyter;./start_jupyter.sh; /bin/bash"


tmux select-window -t main:menu

tmux a -t main
