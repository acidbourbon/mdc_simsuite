#!/bin/bash

x=0.1
y=0.1
halflength=0.4
n=5

for i in $(seq 1 $n); do
cat <<EOF

*area -0.40 -0.40 -0.40 0.40 0.40 0.40 
area -0.40 -0.40 -0.40 0.40 0.40 0.40 view x=0 3d
track $x $y -$halflength  $x $y $halflength HEED proton energy 1.93 GeV
INTEGRATION-PARAMETERS  MONTE-CARLO-COLLISIONS 1000
DRIFT TRACK MONTE-CARLO-DRIFT LINE-PRINT

EOF

done
