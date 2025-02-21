#!/usr/bin/env python

import os,sys
from ROOT import *
from string import *
import math

modelname = 'PureHiggsino'
modelname = 'PureWino'
date = '220902'
date = '221013'
date = '221016'# zero out some bins
date = '221017'# zero out some bins
date = '221018'
date = '221019'
date = '221019mask1920'
date = '221019mask19'
date = '221019masknone'
date = '221019mask19202324'
date = '221019mask030419202324'
date = '221019mask03041923'
date = '221019mask1923'
date = '221019mask011923'
date = '221019mask01020304192021222324'
date = '221019mask171923'
date = '221019masknoneB'
date = '221019mask1923B'
date = '221019mask161923B'
date = '221019asimov161923'
date = '221019asimov161923B'
date = '221019asimov16171923B'
date = 'asimov1516171923'
date = 'asimov1923'#best DT
date = '29Nov2022'
date = '23Mar2023'
date = '24June2023'
date = '31Aug2023b' # redoing paper version after fixing bug, disappearing track

maketestcard = False
ForceAsimov = False

ApplyCorrelatedFakeSyst = True
ApplyCorrelatedPromptSyst = True


binstozero = [19]
binstozero = [0]
binstozero = [19,20,23,24]
binstozero = [3,4,19,20,23,24]
binstozero = [1,19,23]
binstozero = [1,2,3,4,19,20,21,22,23,24]
binstozero = [17,19,23]
binstozero = [16,19,23]
binstozero = []
binstoasimov = [16,19,23]
binstoasimov = [16,17,19,23]
binstoasimov = [15,16,17,19,23]
binstoasimov = [19,23]
binstoasimov = [] # this line was just added january 2024 because line above was freaky
###########Sam, could this have have been in place for your actual limits? I need to 0 these out and re-check

def zero_out_certain_bins(histo, ignoreBins):
  
    for iBin in range(histo.GetNbinsX()+1):
        if iBin in ignoreBins:
            histo.SetBinContent(iBin, 0)
            histo.SetBinError(iBin, 0)
    return histo
    
    
try: FinalState = sys.argv[1]
except: 
    FinalState = '1t_Electrons'
    FinalState = '2l_Electrons'
    FinalState = '1t_Muons'
    FinalState = '2l_Muons_orth'
    FinalState = 'spdl_comb'
    FinalState = 'spdl_dt_comb'
    FinalState = 'DT'
    
try: Era = sys.argv[2]
except: 
    Era = 'Run2'    

# Physics processes
filesighistpairs = []
if FinalState=='DT':
     procs = ['Signal', 'Shower', 'Muon', 'Fake']
     maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v18/'
     fb = TFile(maindir+'Background/predictionRun2.root'); fb.ls()
     hsh = fb.Get('hShowerBaselineMASTER_BinNumberMethod2')
     hsh.SetName('Shower')
     hmn = fb.Get('hMuonBaselineMASTER_BinNumberMethod3')
     hmn.SetName('Muon')
     hfk = fb.Get('hFakeBaselineMASTER_BinNumberMethod1')
     hfk.SetName('Fake')
     hbkgs = [hsh, hfk, hmn]
     if ForceAsimov:
        hobs = hbkgs[0].Clone()
        for h in hbkgs[1:]: hobs.Add(h)
        #otherwise take the observed limit:
     else: 
        hobs = fb.Get('h_data')
        hbkgtot = hbkgs[0].Clone()
        for h in hbkgs[1:]: hbkgtot.Add(h)
        for thebin in binstoasimov:
            hobs.SetBinContent(thebin, math.floor(hbkgtot.GetBinContent(thebin)))

     #zero_out_certain_bins(hsh, binstozero)
     #zero_out_certain_bins(hmn, binstozero)
     #zero_out_certain_bins(hfk, binstozero)
     #zero_out_certain_bins(hobs, binstozero)
            
     hsig_name = 'hBaselineNom_BinNumberTruth'
     sigsysts = ['BTag', 'Dedx', 'DtSfLong', 'DtSfShort', 'Isr', 'Jec', 'Scale', 'Trig']
     bgsysts = [['FakeLong', '1', 'One'],['FakeShort', '1','One'], ['ShowerLong', '2', 'One'], ['ShowerShort', '2', 'One'], ['MuonLong', '3', 'One']]
     signaldir = maindir+'Signal/'+modelname+'/*.root'
     signalfiles = os.popen('ls '+signaldir).readlines()
     for sf in signalfiles:
         filesighistpairs.append([sf, hsig_name])

if FinalState in ['1t_Electrons', '2l_Electrons', '1t_Muons', '2l_Muons', '2l_Muons_orth']:
    procs = ['Signal', 'SM']
    #fmaster_name = 'FromYuval/13July2022/sig_bg_histograms_data_driven_run2.root'
    fmaster_name = 'FromYuval/13Sept2020/sig_bg_histograms_data_driven_run2_0_5_bin.root'
    #fmaster_name = 'FromYuval/13Sept2020/sig_bg_histograms_data_driven_run2_0_5_bin_tautau_veto.root'   
    fmaster_name = 'FromYuval/data_driven_per_year_with_systematics_on_bg/' 
    fmaster = TFile(fmaster_name); fmaster.ls()
    hsm = fmaster.Get('bg_'+FinalState) 
    hsm.SetName('SM')
    for ibin in range(1, hsm.GetXaxis().GetNbins()+1):
        if hsm.GetBinContent(ibin)==0: 
            hsm.SetBinContent(ibin, 0.5)
            hsm.SetBinError(ibin, 0.5)            
    hbkgs = [hsm]
    hobs = hsm.Clone('h_data')
    hobs = fmaster.Get('h_data')
    
        
    folderkeys = fmaster.GetListOfKeys()
    names = []
    foldernames = []
    for key in folderkeys:
        #if not 'signal' in key.GetName(): continue
        name = key.GetName()
        if not FinalState in name: continue
        if not 'mChi' in name: continue
        names.append(key.GetName())
        filesighistpairs.append([fmaster, name])
    sigsysts = []
    bgsysts = []


outrootdir = 'sigbgobsroot/'+date+'/'+modelname+'/'
outdcdir = 'datacards/'+date+'/'+modelname+'/'

if FinalState == 'spdl_comb': 
    FinalStates = ['1t_Electrons','2l_Electrons','1t_Muons','2l_Muons_orth']
    from glob import glob
    flagshipfilenames = glob(outdcdir+'*'+FinalStates[0]+'*')
    for flagshipfilename in flagshipfilenames:
        cmd = 'combineCards.py '+flagshipfilename+' '
        for fstate in FinalStates[1:]:
            cmd+=flagshipfilename.replace(FinalStates[0],fstate)+' '
        cmd+='> '+flagshipfilename.replace(FinalStates[0],FinalState)
        print((cmd))
        os.system(cmd)
    exit(0)
    
if FinalState == 'spdl_dt_comb': 
    FinalStates = ['DT','spdl_comb']
    from glob import glob
    flagshipfilenames = glob(outdcdir+'*'+FinalStates[0]+'*')
    print(('flagshipfilenames', flagshipfilenames))
    for flagshipfilename in flagshipfilenames:
        cmd = 'combineCards.py  '+flagshipfilename+' '
        for fstate in FinalStates[1:]:
            print(('here we aa', flagshipfilename, flagshipfilename.split('dm')[-1].split('GeV')[0]))
            precisenumber = float(flagshipfilename.split('dm')[-1].split('GeV')[0].replace('p','.'))
            roundednumber = str(round(precisenumber-0.001, 2)).replace('.','p')
            precisenumber = str(precisenumber).replace('.','p')
            flagshipfilename_ = flagshipfilename.replace(precisenumber,roundednumber)
            if os.path.exists(flagshipfilename.replace(FinalStates[0],fstate)): flagshipfilename_ = flagshipfilename
            cmd+=flagshipfilename_.replace(FinalStates[0],fstate)+' '
        cmd+='> '+flagshipfilename.replace(FinalStates[0],FinalState)
        print((cmd))
        os.system(cmd)
    exit(0)
    

hobs.SetName('data_obs')

if not os.path.exists(outrootdir):
    os.system('mkdir -p '+outrootdir)

if not os.path.exists(outdcdir):
    os.system('mkdir -p '+outdcdir)

# DATACARD CONTENT

# Write the datacard beginning lines
cnt = '''imax %d number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
#SHRINKFACTOR=%f
------------------------------------------------------------
observation            %s
------------------------------------------------------------
'''
# Number of background processes
nbg = str(len(procs) - 1)

if modelname in ['PureHiggsino','PureWino']:
    try: sigsysts.remove('Scale')
    except: a = 1

sighistsup = {}
sighistsdn = {}

for pairthingy in filesighistpairs:
    f, sighistname = pairthingy
    
    if type(f)==type('bananas'):
        f = f.strip()
        fs = TFile(f)
        hsig = fs.Get(sighistname)
        hsig.SetDirectory(0)
        modelpoint = ((f.split('/'))[-1])[:-5]
        modelpoint = modelpoint.replace("pm", "ne")
        modelpoint = 'mChi'+modelpoint.split('mChi')[-1]
        if "pm" in modelpoint:
            print(("*******:", modelpoint)        )
    else: 
        hsig = f.Get(sighistname)
        modelpoint = sighistname
        modelpoint = modelpoint.replace("pm", "ne")
        if "pm" in modelpoint:
            print(("*******:", modelpoint)        )
    froot = modelpoint.replace("AnalysisHists", "limitinput") + Era+'.root'
    fdatacard = modelpoint.replace("AnalysisHists", "datacard") + '.txt'
    if not FinalState in fdatacard: fdatacard = fdatacard.replace('.txt','_'+FinalState+Era+'.txt')
    # Get signal histograms
    #hsig = fs.Get('hLongBaselineSystNom_BinNumberTruth')
    zero_out_certain_bins(hsig, binstozero)
    hsig.SetName('Signal')
    for sys in sigsysts: # will need some help once Yuval computes systematics
        sighistsup[sys] = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth')
        sighistsup[sys].SetName('Signal_'+sys+'Up')
        sighistsdn[sys] = fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
        sighistsdn[sys].SetName('Signal_'+sys+'Down')
        zero_out_certain_bins(sighistsup[sys], binstozero)
        zero_out_certain_bins(sighistsdn[sys], binstozero)        

    # Make the output file
    #if os.path.exists(outrootdir+'/'+froot): continue
    fr = TFile(outrootdir+'/'+froot, 'RECREATE')
    # Write histograms to the output file
    if hsig.Integral()>0: shrinkfactor = 10./hsig.GetMaximum()
    else: shrinkfactor = 1.0
    hsig.Scale(shrinkfactor)    
    hsig.Write()
    for sys in sigsysts:
        sighistsup[sys].Scale(shrinkfactor)
        sighistsup[sys].Write()
        sighistsdn[sys].Scale(shrinkfactor)
        sighistsdn[sys].Write()
        
    for hbkg in hbkgs: hbkg.Write()
    # Write BG syst histos
    if maketestcard: fd = open('testypoo2.txt', 'w')    
    else: fd = open(outdcdir+'/'+fdatacard, 'w')
    print('we hath created', outdcdir+'/'+fdatacard)
    # Number of data events
    ndatac = []
    for ibin in range(1, hobs.GetXaxis().GetNbins()+1):
        ndatac.append('%-14s' % int(hobs.GetBinContent(ibin)) + ('%-14s' % '')*3)
    ndata = str(hobs.Integral())
    # Write the datacard header
    #print nbg, ndata, froot
    fd.write(cnt % (hobs.GetXaxis().GetNbins(), nbg, shrinkfactor, ''.join(ndatac)))#ndata))

    # Yields for processes
    yields = []

    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for p in procs:
        #yields.append(gDirectory.Get(p).Integral())
        yields.append(gDirectory.Get(p).GetBinContent(ibin))

    # Write processes and rates
    row = '%-21s ' % 'bin'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for i in procs:
        row = row+'%-14s' % ('SR'+str(ibin))
    fd.write(row+'\n')
    row = '%-21s ' % 'process'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for i in procs:
        row = row+'%-14s' % i
    fd.write(row+'\n')
    row = '%-21s ' % 'process'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
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
    cnt2 += '''Lumi            lnN    '''+'''1.025         -             -             -             '''*hobs.GetXaxis().GetNbins()+'''
'''
#    Closure  shape  -         1.0        1.0        1.0
    fd.write(cnt2)
    for sys in sigsysts:
      rowc = []
      rowc.append('%-14s ' % sys.strip() +'%-6s ' % 'lnN')
      
      hup, hdown = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth'), fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
      hup.Scale(shrinkfactor), hdown.Scale(shrinkfactor)
      for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
        for p in procs:
            relevant = p=='Signal'
            if relevant:
                if (hsig.GetBinContent(ibin)>0 and hup.GetBinContent(ibin)>0 and hdown.GetBinContent(ibin)>0) and not abs(hup.GetBinContent(ibin)==hdown.GetBinContent(ibin)): rowc.append('%-14s' % (str(round(hup.GetBinContent(ibin)/hsig.GetBinContent(ibin),3))+'/'+str(round(hdown.GetBinContent(ibin)/hsig.GetBinContent(ibin),3))))
                else: rowc.append('%-14s' % ('1.0'))
            else: rowc.append('%-14s' % ('-'))
      row = ''.join(rowc)
      fd.write(row+'\n')
    if True:
        fd.write('''ShowerShortOne lnN    '''+'''-             -             -             -             -             -             -             -             -             2.0            -             -             -             2.0            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
    if ApplyCorrelatedPromptSyst: 
        fd.write('''ShowerLongSyst lnN    '''+'''-            1.2            -             -             -            1.2            -             -             -              -            -             -             -              -            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
    if ApplyCorrelatedFakeSyst: 
        fd.write('''FakeLongSyst lnN      '''+'''-             -             -            1.3            -             -             -            1.3            -              -            -             -             -              -            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
        fd.write('''FakeShortSyst lnN     '''+'''-             -             -             -             -             -             -              -            -              -            -            1.3            -              -            -            1.3            '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')        
    for bgsys in bgsysts:
      #print 'bgsys', bgsys
      
      hup, hdown = fb.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Up'), fb.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Down')
      rowc = []
      rowc.append('%-14s ' % (bgsys[0]+bgsys[2]).strip()+('%-6s ' % 'lnN'))
      for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
        for p in procs:
            relevant = bgsys[0].split('Long')[0].split('Short')[0]==p
            if relevant: 
                if (hup.GetBinContent(ibin)>0 and hdown.GetBinContent(ibin)>0) and not abs(hup.GetBinContent(ibin)==hdown.GetBinContent(ibin)): rowc.append('%-14s' % (str(round(hup.GetBinContent(ibin)/gDirectory.Get(p).GetBinContent(ibin),3))+'/'+str(round(hdown.GetBinContent(ibin)/gDirectory.Get(p).GetBinContent(ibin),3))))
                else: rowc.append('%-14s' % ('1.0'))
            else: rowc.append('%-14s' % ('-'))
      row = ''.join(rowc)
      fd.write(row+'\n')
      del rowc
            
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
        for p in procs:
            hp = gDirectory.Get(p)
            rowc = []
            #if hp.GetBinError(ibin)>0: linestem = str(float('%.3g' % (hp.GetBinContent(ibin)**2/hp.GetBinError(ibin)**2)))
            if hp.GetBinError(ibin)>0: N = int(float('%.3g' % (hp.GetBinContent(ibin)**2/hp.GetBinError(ibin)**2)))
            else: continue #else: continue#linestem = '0'
            N = max(1,N)
            linestem = str(N)
            if float(linestem.split('.')[-1])==0: linestem = str(int(float(linestem)))
            nuisname = FinalState+'_gma'+p.strip()+str(ibin)
            rowc.append('%-21s ' % (nuisname+' gmN '+linestem))
            for ibin_ in range(1,hobs.GetXaxis().GetNbins()+1):
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
    if type(f)==type('bananas'): fs.Close()        
    fd.close()
    if type(f)==type('bananas'):fs.Close()
    if maketestcard: exit(0)

