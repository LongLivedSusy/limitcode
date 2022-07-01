#!/usr/bin/env python

import os,sys
from string import *

date = sys.argv[1]

# Put your own processes here:
#procs = {'T1qqqqLL', 'T2btLL'}
#procs = {'T1btbtLL', 'T2tbLL'}
procs = {'T2btLL', 'T2tbLL', 'T1btbtLL'}
#procs = {'T1btbtLL'}
#procs = {'T2btLL'}
ctaus = {'10'}
# change the label in scripts/sms.py: ctau = ...

if not os.path.exists(date):
    os.mkdir(date)

# Loop over the processes and run the final plots:
for p in procs:
    if len(ctaus) > 0:
        for c in ctaus:
            fname = '../limits2root/%s/%s/results/%s_%s_DT_results.root' % (date, p, p, c)
            print 'Trying... '+fname
            if os.path.exists(fname):
                cmd = 'cp '+fname+' syst_results/DT/results/%s_%s_DT_results.root' % (p, c)
                #print cmd
                os.system(cmd)
                cmd = 'python scripts/makeSMSplots.py config/DT/%s_%s_DT_exp.cfg %s %s %s' % (p, c, p, date, c )
                #print cmd
                os.system(cmd)

            fname = '../limits2root/%s/%s_nolep/results/%s_%s_DT_results.root' % (date, p, p, c)
            print 'Trying... '+fname
            if os.path.exists(fname):
                cmd = 'cp '+fname+' syst_results/DT/results/%s_%s_DT_results.root' % (p, c)
                #print cmd
                os.system(cmd)
                cmd = 'python scripts/makeSMSplots.py config/DT/%s_%s_DT_exp.cfg %s %s %s nolep_' % (p, c, p, date, c )
                os.system(cmd)

            os.system('mv *%s.* %s/' % (date, date))
    else:
        cmd = 'cp ../limits2root/%s/%s/results/%s_DT_results.root syst_results/DT/results/%s_DT_results.root' % (date, p, p, p)
        print cmd
        #os.system(cmd)
        cmd = 'python scripts/makeSMSplots.py config/DT/%s_DT_exp.cfg %s %s' % (p, p, date )
        print cmd
        #os.system(cmd)

        #cmd = 'cp ../limits2root/%s/%s_nolep/results/%s_DT_results.root syst_results/DT/results/%s_DT_results.root' % (date, p, p, p)
        #print cmd
        #os.system(cmd)
        #cmd = 'python scripts/makeSMSplots.py config/DT/%s_DT_exp.cfg %s %s nolep_' % (p, p, date )
        #os.system(cmd)

        #os.system('mv *%s.* %s/' % (date, date))






#os.system(cmd)


