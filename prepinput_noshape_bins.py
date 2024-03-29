#!/usr/bin/env python

# Make datacards for a given set of bins

import os,sys
from ROOT import *
from string import *

maketestcard = False

if len(sys.argv) > 1: date = sys.argv[1]
if len(sys.argv) > 2: signalname = sys.argv[2]
if len(sys.argv) > 3: binstorun = sys.argv[3]

# Zero out certain bins
def zero_out_certain_bins(histo, ignoreBins):
  
    for iBin in range(histo.GetNbinsX()+1):
        if iBin in ignoreBins:
            histo.SetBinContent(iBin, 0)
            histo.SetBinError(iBin, 0)
    return histo

# bins options for inclusion in limit setting
binlists = {}
binlists['all'] = list(range(1, 49+1))
binlists['leptonbins'] = list(range(25, 48+1))
binlists['hadronbins'] = list(range(1, 24+1))
shortbins = []
longbins = []
for i in range(1,48+1):
    if i % 4 == 3 or i % 4 == 0: longbins.append(i)
    if i % 4 == 1 or i % 4 == 2: shortbins.append(i)
binlists['shortbins'] = shortbins
binlists['longbins'] = longbins
binlists['singleDT'] = list(range(1, 48+1))
binlists['doubleDT'] = [49]

#binstorun = 'doubleDT'
# Directory suffix
dirext = ''
if binstorun != 'all':
    dirext = '_'+binstorun

#date = '210520'
#date = '220818'
#date = '220914'
#date = '220924'
#date = '221007'

# Physics processes
# !!! Maybe already match here the process names and histograms
procs = [
    'Signal',
    'Shower',
    'Muon',
    'Fake'
    ]

#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v15shutterleps/'
#maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v15/'
maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v16/'

fb = TFile(maindir+'Background/predictionRun2_unblinded.root')
fb.ls()

# Get all bg histograms
hsh = fb.Get('hShowerBaselineMASTER_BinNumberMethod2')
hsh.SetName('Shower')
hmn = fb.Get('hMuonBaselineMASTER_BinNumberMethod3')
hmn.SetName('Muon')
hfk = fb.Get('hFakeBaselineMASTER_BinNumberMethod1')
hfk.SetName('Fake')
#hobs = hsh.Clone()
#hobs.SetName('h_data')
hobs = fb.Get('h_data')
#hobs.Add(hfk)
#hobs.Add(hmn)

print(hsh.Integral() + hmn.Integral() + hfk.Integral(), hobs.Integral())


#signalname = sys.argv[1] 
#print 'Signal: '+signalname
#signalname = 'T2btLL'
#signalname = 'T1qqqqLL'
#signalname = 'T1btbtLL'
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
cnt = '''imax %s number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
------------------------------------------------------------
observation           %s
------------------------------------------------------------
'''
# Number of background processes
nbg = str(len(procs) - 1)
nbins = str(len(binlists[binstorun]))

systs = ['BTag', 'Dedx', 'DtSfLong', 'DtSfShort', 'Isr', 'Jec', 'Scale', 'Trig']
if signalname == 'PureHiggsino':
    systs.remove('Scale')

sighistsup = {}
sighistsdn = {}

for f in signalfiles:
    f = f.strip()
    signalhistofile = f
    signalname = ((f.split('/'))[-1])[:-5]
    print (signalname)
    if "pm" in signalname:
        print ("******* 1:", signalname)
        signalname = signalname.replace("pm", "ne")
        print ("******* 2:", signalname)
    frn = signalname.replace("AnalysisHists", "limitinput") + '.root'
    fdn = signalname.replace("AnalysisHists", "datacard") + '.txt'
    fs = TFile(signalhistofile)
    if signalname == 'T1qqqqLL' and '1075' in signalhistofile: continue
    print ('*** Signal file:', signalhistofile)
    # Get signal histograms
    #hsig = fs.Get('hLongBaselineSystNom_BinNumberTruth')
    #hsig.SetName('Signal')
    hsig = fs.Get('hBaselineNom_BinNumberTruth')
    hsig.SetName('Signal')
#    zero_out_certain_bins(hsig, binstozero)
    for sys in systs:
        #if sys == 'Trig' or 'DtSf' in sys: continue
        #if signalname == 'PureHiggsino' and sys == 'Scale': continue
        #print sys
        sighistsup[sys] = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth')
        sighistsup[sys].SetName('Signal_'+sys+'Up')
        sighistsdn[sys] = fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
        sighistsdn[sys].SetName('Signal_'+sys+'Down')
#        zero_out_certain_bins(sighistsup[sys], binstozero)
#        zero_out_certain_bins(sighistsdn[sys], binstozero)

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
    if maketestcard: fd = open('testypoo2.txt', 'w')    
    else: fd = open(outdcdir+'/'+fdn, 'w')
    print('we hath created', outdcdir+'/'+fdn)
    # Number of data events
    ndatac = []
#    for ibin in range(1, hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
        ndatac.append('%-14s' % int(hobs.GetBinContent(ibin)) + ('%-14s' % '')*3)
    ndata = str(hobs.Integral())
    # Write the datacard header
    #print nbg, ndata, frn
    fd.write(cnt % (nbins, nbg, ''.join(ndatac)))#ndata))

    # Yields for processes
    yields = []

#    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
      for p in procs:
        #yields.append(gDirectory.Get(p).Integral())
        yields.append(gDirectory.Get(p).GetBinContent(ibin))

    # Write processes and rates
    row = '%-21s ' % 'bin'
#    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
      for i in procs:
        row = row+'%-14s' % ('SR'+str(ibin))
    fd.write(row+'\n')
    row = '%-21s ' % 'process'
#    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
      for i in procs:
        row = row+'%-14s' % i
    fd.write(row+'\n')
    row = '%-21s ' % 'process'
#    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
      for i in range(len(procs)):
        row = row+'%-14i' % i
    fd.write(row+'\n')
    row = '%-21s ' % 'rate'
    for y in yields:
        row = row+'%-14s' % str(round(y,3))
    fd.write(row+'\n')

    # Add random systematics
    cnt2 = '''-----------------------------------------
'''
    cnt2 += '''Lumi           lnN    '''+ '''1.025         -             -             -             '''*len(binlists[binstorun])+'''
'''
    cnt2 += '''jes            lnN    '''+ '''0.98/1.03     -             -             -             '''*len(binlists[binstorun])+'''
'''
#    Closure  shape  -         1.0       1.0       1.0
    fd.write(cnt2)    
    for sys in systs:
      #print 'sys', sys
      rowc = []
      rowc.append('%-14s ' % sys.strip() +'%-6s ' % 'lnN')
      hup, hdown = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth'), fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
#      for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for ibin in binlists[binstorun]:
        for p in procs:
            relevant = p=='Signal'
            if relevant:
                if (hup.GetBinContent(ibin)>0 and hdown.GetBinContent(ibin)>0) and not abs(hup.GetBinContent(ibin)==hdown.GetBinContent(ibin)): rowc.append('%-14s' % (str(round(hup.GetBinContent(ibin)/hsig.GetBinContent(ibin),3))+'/'+str(round(hdown.GetBinContent(ibin)/hsig.GetBinContent(ibin),3))))
                else: rowc.append('%-14s' % ('1.0'))
            else: rowc.append('%-14s' % ('-'))
      row = ''.join(rowc)
      fd.write(row+'\n')
    fd.write('ShowerShortOne lnN    ')
    for ibin in binlists[binstorun]:
      if ibin % 4 == 3 or ibin % 4 == 0: 
        fd.write('-             2.0           -             -             ')
      else:
        fd.write('-             -             -             -             ')
    fd.write('\n')
    for bgsys in [['FakeLong', '1', 'One'],['FakeLong', '1', 'Two'],['FakeShort', '1','One'],['FakeShort', '1', 'Two'], ['ShowerLong', '2', 'One'], ['MuonLong', '3', 'One']]:#, ['ShowerShort', '2', 'One']
      #print 'bgsys', bgsys
      
      hup, hdown = fb.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Up'), fb.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Down')
      rowc = []
      rowc.append('%-14s ' % (bgsys[0]+bgsys[2]).strip()+('%-6s ' % 'lnN'))
#      for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for ibin in binlists[binstorun]:
        for p in procs:
            relevant = bgsys[0].split('Long')[0].split('Short')[0]==p
            if relevant: 
                if (hup.GetBinContent(ibin)>0 and hdown.GetBinContent(ibin)>0) and not abs(hup.GetBinContent(ibin)==hdown.GetBinContent(ibin)): rowc.append('%-14s' % (str(round(hup.GetBinContent(ibin)/gDirectory.Get(p).GetBinContent(ibin),3))+'/'+str(round(hdown.GetBinContent(ibin)/gDirectory.Get(p).GetBinContent(ibin),3))))
                else: rowc.append('%-14s' % ('1.0'))
            else: rowc.append('%-14s' % ('-'))
      row = ''.join(rowc)
      fd.write(row+'\n')
      del rowc
            
#    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
    for ibin in binlists[binstorun]:
        for p in procs:
            hp = gDirectory.Get(p)
            rowc = []
#            if hp.GetBinError(ibin)>0: linestem = str(float('%.3g' % (hp.GetBinContent(ibin)**2/hp.GetBinError(ibin)**2)))
            if hp.GetBinError(ibin)>0: N = int(float('%.3g' % (hp.GetBinContent(ibin)**2/hp.GetBinError(ibin)**2)))
            else: continue #else: continue#linestem = '0'
            linestem = str(N)
            if float(linestem.split('.')[-1])==0: linestem = str(int(float(linestem)))
            nuisname = 'gma'+p.strip()+str(ibin)
            rowc.append('%-21s ' % (nuisname+' gmN '+linestem))
#            for ibin_ in range(1,hobs.GetXaxis().GetNbins()+1):
            for ibin_ in binlists[binstorun]:
                for p_ in procs:
                    if not (ibin_==ibin and p_==p): 
                        rowc.append('%-14s' % ('-'))
                        continue
                    if hp.GetBinContent(ibin)>0: rowc.append('%-14s' % str(round(hp.GetBinContent(ibin)/N,4)))
                    else: rowc.append('%-14s' % ('0'))
            row = ''.join(rowc)
            #os.system('echo '+row+' >> '+fd.name)
            fd.write(row+'\n')
            del rowc
    #fd.write('''ShowerShortOne lnN    '''+'''0.98/1.03     -             -             -             '''*hobs.GetXaxis().GetNbins()+''')
    fs.Close()       
    fd.close()
    if maketestcard: exit(0)

