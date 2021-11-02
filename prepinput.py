#!/usr/bin/env python

import os,sys
from ROOT import *
from string import *

# Zero out certain bins
def zero_out_certain_bins(histo, ignoreBins):
      
    for iBin in range(histo.GetNbinsX()+1):
        if iBin in ignoreBins:
            histo.SetBinContent(iBin, 0)
            histo.SetBinError(iBin, 0)
    return histo

# bins options for inclusion in limit setting
nobins = []
#noleptons = range(49, 80+1) + range(85, 88+1)
#onlyleptons = range(0, 48+1) + range(81, 84+1)

# before merging the 2DT bins:
#noleptons = range(25, 48+1) + range(51, 54+1)
#onlyleptons = range(1, 24+1) + range(49, 50+1)

# after merging the 2DT bins:
leptonbins = range(25, 48+1) + range(50, 51+1)
hadronbins = range(1, 24+1) + range(49, 49+1)

binstozero = nobins
#binstozero = leptonbins

# Directory suffix
dirext = ''
if len(binstozero) > 0:
    dirext = '_nolep'

date = '210520'

# Physics processes
# !!! Maybe already match here the process names and histograms
procs = [
    'Signal',
    'Prompt',
    'Fake'
    ]

#maindir = '/nfs/dust/cms/user/beinsam/LongLiveTheChi/Analyzer/CMSSW_10_1_0/src/analysis/interpretation/HistsBkgObsSig/TheWholeEnchilada/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Piano/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Piano/v2/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Xenon/v2/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Antimony/v2/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Antimony/v3/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Antimony/v5/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Antimony/v6/'
maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v9/'

fb = TFile(maindir+'Background/predictionRun2.root')

# Get all bg histograms
hpr = fb.Get('hPromptLongBaselineMASTER_BinNumberMethod2')
hpr.SetName('Prompt')
hfk = fb.Get('hFakeLongBaselineMASTER_BinNumberMethod1')
hfk.SetName('Fake')
hobs = hpr.Clone()
hobs.SetName('data_obs')
hobs.Add(hfk)

# Zeroing out
zero_out_certain_bins(hpr, binstozero)
#zero_out_certain_bins(hmu, binstozero)
#zero_out_certain_bins(hpi, binstozero)
zero_out_certain_bins(hfk, binstozero)
zero_out_certain_bins(hobs, binstozero)

#signalname = sys.argv[1] 
#print 'Signal: '+signalname
#signalname = 'T2btLL'
signalname = 'T1qqqqLL'

signaldir = maindir+'Signal/'+signalname+'/*.root'
signalfiles = os.popen('ls '+signaldir).readlines()

outrootdir = 'sigbgobsroot/'+date+'/'+signalname+dirext+'/'
outdcdir = 'datacards/'+date+'/'+signalname+dirext+'/'

if not os.path.exists(outrootdir):
    os.system('mkdir -p '+outrootdir)

if not os.path.exists(outdcdir):
    os.system('mkdir -p '+outdcdir)

# DATACARD CONTENT

# Write the datacard beginning lines
cnt = '''imax 1 number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
------------------------------------------------------------
observation     %s
------------------------------------------------------------
shapes * * %s $PROCESS $PROCESS_$SYSTEMATIC
------------------------------------------------------------
'''
# Number of background processes
nbg = str(len(procs) - 1)

for f in signalfiles:
    f = strip(f)
    signalhistofile = f
    signalname = ((f.split('/'))[-1])[:-5]
    if "pm" in signalname:
        print "******* 1:", signalname
        signalname = replace(signalname, "pm", "ne")
        print "******* 2:", signalname
    frn = replace(signalname, "AnalysisHists", "limitinput") + '.root'
    fdn = replace(signalname, "AnalysisHists", "datacard") + '.txt'
    fs = TFile(signalhistofile)
    if signalname == 'T1qqqqLL' and '1075' in signalhistofile: continue
    print '*** Signal file:', signalhistofile
    # Get signal histograms
    hsig = fs.Get('hLongBaselineSystNom_BinNumberTruth')
    hsig.SetName('Signal')
    # btag systematics
    hsigbtagup = fs.Get('hLongBaselineSystBTagUp_BinNumberTruth')
    hsigbtagup.SetName('Signal_btagUp')
    hsigbtagdown = fs.Get('hLongBaselineSystBTagDown_BinNumberTruth')
    hsigbtagdown.SetName('Signal_btagDown')
    # ISR systemtics
    hsigisrup = fs.Get('hLongBaselineSystIsrUp_BinNumberTruth')
    hsigisrup.SetName('Signal_isrUp')
    hsigisrdown = fs.Get('hLongBaselineSystIsrDown_BinNumberTruth')
    hsigisrdown.SetName('Signal_isrDown')
    #hsig.Scale(35900.)
    zero_out_certain_bins(hsig, binstozero)
    zero_out_certain_bins(hsigbtagup, binstozero)
    zero_out_certain_bins(hsigbtagdown, binstozero)
    zero_out_certain_bins(hsigisrup, binstozero)
    zero_out_certain_bins(hsigisrdown, binstozero)
    # Make the output file
    fr = TFile(outrootdir+'/'+frn, 'RECREATE') 
    # Write histograms to the output file
    hsig.Write()
    hsigbtagup.Write()
    hsigbtagdown.Write()
    hsigisrup.Write()
    hsigisrdown.Write()
    hpr.Write()
    #hmu.Write()
    #hpi.Write()
    hfk.Write()
    hobs.Write()
    #    sys.exit()
    fd = open(outdcdir+'/'+fdn, 'w')
    # Number of data events
    ndata = str(hobs.Integral())
    # Write the datacard header
    print nbg, ndata, frn
    fd.write(cnt % (nbg, ndata, outrootdir+frn))

    # Yields for processes
    yields = []
    for p in procs:
        yields.append(gDirectory.Get(p).Integral())
    print 'yields:', yields

    # Write processes and rates
    row = '%-15s ' % 'bin'
    for i in procs:
        row = row+'%-9s ' % 'DT'
    fd.write(row+'\n')
    row = '%-15s ' % 'process'
    for i in procs:
        row = row+'%-9s ' % i
    fd.write(row+'\n')
    row = '%-15s ' % 'process'
    for i in range(len(procs)):
        row = row+'%-9i ' % i
    fd.write(row+'\n')
    row = '%-15s ' % 'rate'
    for y in yields:
        row = row+'%9.3f ' % y
    fd.write(row+'\n')

    # Add random systematics
    cnt2 = ''''-----------------------------------
    Lumi     lnN    1.025     1.025     1.025    
    jes      lnN    0.98/1.03 -         -        
    btag     shape    1.      -         -         
    isr      shape    1.      -         -         
    '''
#    Closure  shape  -         1.0       1.0       1.0


    fd.write(cnt2)



