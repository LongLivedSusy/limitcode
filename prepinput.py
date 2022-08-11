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

#date = '210520'
date = '220705'

# Physics processes
# !!! Maybe already match here the process names and histograms
procs = [
    'Signal',
    'Shower',
    'Muon',
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
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v9/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v14/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v14shutterleps/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v15/'
maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v16/'

fb = TFile(maindir+'Background/predictionRun2.root')

# Get all bg histograms
hsh = fb.Get('hShowerBaselineMASTER_BinNumberMethod2')
hsh.SetName('Shower')
hmn = fb.Get('hMuonBaselineMASTER_BinNumberMethod3')
hmn.SetName('Muon')
hfk = fb.Get('hFakeBaselineMASTER_BinNumberMethod1')
hfk.SetName('Fake')
hobs = hsh.Clone()
hobs.SetName('data_obs')
hobs.Add(hfk)
hobs.Add(hmn)

#1   hShowerBaselineMASTER_BinNumberMethod2  
hsh1u = fb.Get('hShowerLongBaselineMASTER_BinNumberMethod2OneUp')
hsh1u.SetName('Shower_LongOneUp')
hsh1d = fb.Get('hShowerLongBaselineMASTER_BinNumberMethod2OneDown')
hsh1d.SetName('Shower_LongOneDown')
hsh2u = fb.Get('hShowerShortBaselineMASTER_BinNumberMethod2OneUp')
hsh2u.SetName('Shower_ShortOneUp')
hsh2d = fb.Get('hShowerShortBaselineMASTER_BinNumberMethod2OneDown')
hsh2d.SetName('Shower_ShortOneDown')

#7   hFakeBaselineMASTER_BinNumberMethod1
hfk1u = fb.Get('hFakeLongBaselineMASTER_BinNumberMethod1OneUp')
hfk1u.SetName('Fake_LongOneUp')
hfk1d = fb.Get('hFakeLongBaselineMASTER_BinNumberMethod1OneDown')
hfk1d.SetName('Fake_LongOneDown')
hfk2u = fb.Get('hFakeLongBaselineMASTER_BinNumberMethod1TwoUp')
hfk2u.SetName('Fake_LongTwoUp')
hfk2d = fb.Get('hFakeLongBaselineMASTER_BinNumberMethod1TwoDown')
hfk2d.SetName('Fake_LongTwoDown')
hfk3u = fb.Get('hFakeShortBaselineMASTER_BinNumberMethod1OneUp')
hfk3u.SetName('Fake_ShortOneUp')
hfk3d = fb.Get('hFakeShortBaselineMASTER_BinNumberMethod1OneDown')
hfk3d.SetName('Fake_ShortOneDown')
hfk4u = fb.Get('hFakeShortBaselineMASTER_BinNumberMethod1TwoUp')
hfk4u.SetName('Fake_ShortTwoUp')
hfk4d = fb.Get('hFakeShortBaselineMASTER_BinNumberMethod1TwoDown')
hfk4d.SetName('Fake_ShortTwoDown')

#17  hMuonBaselineMASTER_BinNumberMethod3
hmn1u = fb.Get('hMuonLongBaselineMASTER_BinNumberMethod3OneUp')
hmn1u.SetName('Muon_LongOneUp')
hmn1d = fb.Get('hMuonLongBaselineMASTER_BinNumberMethod3OneDown')
hmn1d.SetName('Muon_LongOneDown')

# Zeroing out
zero_out_certain_bins(hsh, binstozero)
zero_out_certain_bins(hmn, binstozero)
#zero_out_certain_bins(hpi, binstozero)
zero_out_certain_bins(hfk, binstozero)
zero_out_certain_bins(hobs, binstozero)

#signalname = sys.argv[1] 
#print 'Signal: '+signalname
#signalname = 'T2btLL'
#signalname = 'T1qqqqLL'
signalname = 'T1btbtLL'
#signalname = 'T2tbLL'
#signalname = 'PureHiggsino'

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

systs = ['BTag', 'Dedx', 'DtSfLong', 'DtSfShort', 'Isr', 'Jec', 'Scale', 'Trig']
if signalname == 'PureHiggsino':
    systs.remove('Scale')
sighistsup = {}
sighistsdn = {}

for f in signalfiles:
    f = strip(f)
    signalhistofile = f
    signalname = ((f.split('/'))[-1])[:-5]
    print signalname
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
    #hsig = fs.Get('hLongBaselineSystNom_BinNumberTruth')
    #hsig.SetName('Signal')
    hsig = fs.Get('hBaselineNom_BinNumberTruth')
    hsig.SetName('Signal')
    zero_out_certain_bins(hsig, binstozero)
    for sys in systs:
        #if sys == 'Trig' or 'DtSf' in sys: continue
        #if signalname == 'PureHiggsino' and sys == 'Scale': continue
        #print sys
        sighistsup[sys] = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth')
        sighistsup[sys].SetName('Signal_'+sys+'Up')
        sighistsdn[sys] = fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
        sighistsdn[sys].SetName('Signal_'+sys+'Down')
        zero_out_certain_bins(sighistsup[sys], binstozero)
        zero_out_certain_bins(sighistsdn[sys], binstozero)

    # Make the output file
    fr = TFile(outrootdir+'/'+frn, 'RECREATE') 
    # Write histograms to the output file
    hsig.Write()
    for sys in systs:
        #if sys == 'Trig' or 'DtSf' in sys: continue
        sighistsup[sys].Write()
        sighistsdn[sys].Write()
    hmn.Write()
    hsh.Write()
    hfk.Write()
    hobs.Write()
    # Write BG syst histos
    hsh1u.Write()
    hsh1d.Write()
    hsh2u.Write()
    hsh2d.Write()
    hfk1u.Write()
    hfk1d.Write()
    hfk2u.Write()
    hfk2d.Write()
    hfk3u.Write()
    hfk3d.Write()
    hfk4u.Write()
    hfk4d.Write()
    hmn1u.Write()
    hmn1d.Write()
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
    cnt2 = ''''-----------------------------------------
    Lumi     lnN    1.025     1.025     1.025     1.025
    jes      lnN    0.98/1.03 -         -         -
'''
#    Closure  shape  -         1.0       1.0       1.0
    fd.write(cnt2)
    for sys in systs:
        #if sys == 'Trig' or 'DtSf' in sys: continue
        row = '    '+strip(sys)+'   shape    1.      -         -       -'
        fd.write(row+'\n')
    cnt3 = '''    LongOne     shape    -     1     1     1
    ShortOne     shape     -   1     -     1
    LongTwo      shape     -   -     -     1
    ShortTwo     shape     -   -     -     1
    '''
    fd.write(cnt3)

