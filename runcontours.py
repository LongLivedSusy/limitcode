#!/usr/bin/env python

import os,sys
from string import *

date = sys.argv[1]
procs = {'T2btLL', 'T2tbLL', 'T1btbtLL'}
#procs = {'T1btbtLL'}
ctaus = {'10', '200'}
scr = 'Get2DContour_22.py'

# Loop over the processes and ctaus:
for p in procs:
    for c in ctaus:
        cmd = 'python %s %s %s %s' % (scr, p, c, date)
        print cmd
        os.system(cmd)



