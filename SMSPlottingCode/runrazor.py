#!/usr/bin/env python

import os,sys
from string import *

date = sys.argv[1]

# Put your own processes here:
#procs = {'T1qqqqLL', 'T2btLL'}
procs = {'T5ttcc'}

if not os.path.exists(date):
    os.mkdir(date)

# Loop over the processes and run the final plots:
for p in procs:
    cmd = 'cp ../limits2root/%s/%s/%s_AnaBoost_results.root syst_results/AnaBoost/results/%s_AnaBoost_results.root' % (date, p, p, p)
    print cmd
    os.system(cmd)
    cmd = 'python scripts/makeSMSplots.py config/AnaBoost/%s_AnaBoost_exp.cfg %s %s' % (p, p, date )
    print cmd
    os.system(cmd)

    os.system('mv *%s.* %s/' % (date, date))






#os.system(cmd)


