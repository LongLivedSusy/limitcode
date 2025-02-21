#!/usr/bin/env python

import os,sys
from ROOT import *
from string import *
import math

modelname = 'PureHiggsino'
date = '29Nov2022'
date = '30Nov2022'
date = '1Dec2022'
date = '23Mar2023'#yuval full status
date = '22Feb2023'#me in Nov trying to redo FS
#date = '19Apr2023'#yuval partial unblinding
date = '17Nov2023'#actually Yuval's new versions of things
date = '27Nov2023'# sam forges ahead
date = '19Dec2023'# sams dilepton code with sams skims, 
date = '22Dec2023'# sam adds 3 systematics
date = '7March2024'# sam adds 4 systematics
date = '7March2024systnone'# sam adds 4 systematics
date = '12March2024'# sam fixed a normalization issue
date = '18April2024' #yuval's top-up
#date = '5Apr2024'# sam fixed a normalization issue
date = '13Aug2024'
date = '21Sep2024'
date = '31Oct2024'
date = '18Nov2024'#yuval unblinding

dropsigsysts = False
UseShrinkFactor = False

maketestcard = False
ForceAsimov = False

ApplyCorrelatedFakeSyst = False#True
ApplyCorrelatedPromptSyst = False#True

#binstozero = [1,19,23]
binstozero = []
#binstoasimov = [19,23]
binstoasimov = []


def zero_out_certain_bins(histo, ignoreBins):
  
    for iBin in range(histo.GetNbinsX()+1):
        if iBin in ignoreBins:
            histo.SetBinContent(iBin, 0)
            histo.SetBinError(iBin, 0)
    return histo
    
    
try: FinalState = sys.argv[1]
except: 
    FinalState = '1tElectrons'
    FinalState = '2lElectrons'
    FinalState = '1tMuons'
    FinalState = '2lMuons'
    FinalState = '2lMuons_orth'
    FinalState = '1tElectrons_comb'
    FinalState = '1tMuons_comb'
    FinalState = 'spdl_comb'
    FinalState = 'spdlinc_comb'     
    FinalState = 'spdm_comb'
    FinalState = 'spdminc_comb'        
    FinalState = 'spdl_dt_comb'
    FinalState = 'DT'
    
try: Era = sys.argv[2]
except: 
    Era = 'Phase0'

# Physics processes
filesighistpairs = []
if FinalState=='DT':
     procs = ['Signal', 'Shower', 'Muon', 'Fake']
     maindir = '/afs/desy.de/user/k/kutznerv/dust/public/disapptrk/interpretation/Histograms/Indium/v18/'
     fmaster = TFile(maindir+'Background/predictionRun2_unblinded.root'); fmaster.ls()
     fmaster = TFile(maindir+'Background/predictionRun2.root'); fmaster.ls()
     hsh = fmaster.Get('hShowerBaselineMASTER_BinNumberMethod2')
     hsh.SetName('Shower')
     hmn = fmaster.Get('hMuonBaselineMASTER_BinNumberMethod3')
     hmn.SetName('Muon')
     hfk = fmaster.Get('hFakeBaselineMASTER_BinNumberMethod1')
     hfk.SetName('Fake')
     hbkgs = [hsh, hfk, hmn]
     if ForceAsimov:
        hobs = hbkgs[0].Clone()
        for h in hbkgs[1:]: hobs.Add(h)
     else: #otherwise take the observed limit:
        hobs = fmaster.Get('h_data')
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
     bgsysts = [['FakeLong', '1', 'One'],['FakeLong', '1', 'Two'],['FakeShort', '1','One'],['FakeShort', '1', 'Two'], ['ShowerLong', '2', 'One'], ['ShowerShort', '2', 'One'], ['MuonLong', '3', 'One']]
     signaldir = maindir+'Signal/'+modelname+'/*.root'
     signalfiles = os.popen('ls '+signaldir).readlines()
     for sf in signalfiles:
         filesighistpairs.append([sf, hsig_name])

if FinalState in ['2lMuonsOrth','2lMuons']: 
     #, '2lElectrons'#, '2lMuons'
    procs = ['Signal', 'Jetty', 'Tautau']
    #fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_leptons_partial_unblinding.root'
    #fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_leptons.root'
    #fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_leptons_ready.root'    
    fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_leptons_ready.root'    
    print ('fmaster_name', fmaster_name)
    fmaster = TFile(fmaster_name); #fmaster.ls()#### DEBUG WITH THIS
    hjetty = fmaster.Get('bg'+FinalState+'Jetty') 
    hjetty.SetName('Jetty')
    htautau = fmaster.Get('bg'+FinalState+'Tautau') 
    htautau.SetName('Tautau')           
    hbkgs = [hjetty, htautau]
    if ForceAsimov:
       hobs = hbkgs[0].Clone()
       for h in hbkgs[1:]: hobs.Add(h)
       #otherwise take the observed limit:
    else: 
       hobs = fmaster.Get('data'+FinalState)
    folderkeys = fmaster.GetListOfKeys()
    names = []
    for key in folderkeys:
        #if not 'signal' in key.GetName(): continue
        name = key.GetName()
        if not FinalState in name: continue
        if not 'Orth' in FinalState:
            if 'Orth' in name: 
                #print ('protection', name)
                continue
        #print('checking out', name)
        if not len(name.split('_'))==2: continue 
        if not 'mChi' in name: continue
 
        names.append(key.GetName())
        filesighistpairs.append([fmaster, name])
    sigsysts = ['TrgEff','Isr','Jec','BTag','MuSf', 'ElSf']
    if dropsigsysts: sigsysts = []
    #bgsysts = []
    bgsysts = [['Jetty','shape'], ['Jetty','tfError'], ['Tautau','tfError']]
    
if FinalState in ['1tElectrons', '1tMuons']:
    procs = ['Signal', 'QqSymmetric']
    #fmaster_name = 'FromYuval/data_driven_per_year_with_systematics_on_bg/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_tracks.root'
    #fmaster_name = 'FromYuval/19Apr2023/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_tracks_partial_unblinding.root'
    #fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_tracks.root'
    #fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_tracks_ready.root'
    fmaster_name = 'FromYuval/'+date+'/sig_bg_histograms_data_driven_'+Era.lower().replace('phase0','2016')+'_tracks_ready.root'
    fmaster = TFile(fmaster_name); #fmaster.ls()#DEBUG with THIS
    hQqSymmetric = fmaster.Get('bg'+FinalState+'ChargeSymmetric') #would be nice if this were +'Jetty'
    hQqSymmetric.SetName('QqSymmetric')          
    hbkgs = [hQqSymmetric]
    if ForceAsimov:
       hobs = hbkgs[0].Clone()
       for h in hbkgs[1:]: hobs.Add(h)
    else: #otherwise take the observed limit:
       hobs = fmaster.Get('data'+FinalState)
    folderkeys = fmaster.GetListOfKeys()
    names = []
    for key in folderkeys:
        #if not 'signal' in key.GetName(): continue
        name = key.GetName()
        if not FinalState in name: continue
        if not 'mChi' in name: continue
        if not len(name.split('_'))==2: continue
        names.append(key.GetName())
        filesighistpairs.append([fmaster, name])
    sigsysts = ['TrgEff','Isr','Jec']
    if dropsigsysts: sigsysts = []
    #bgsysts = []
    bgsysts = []#####need TF uncertainty![['QqSymmetric','tfError']]


outrootdir = 'sigbgobsroot/'+date+'/'+modelname+'/'
outdcdir = 'datacards/'+date+'/'+modelname+'/'


if 'comb' in FinalState and (not 'dt' in FinalState):
    #FinalStates = ['1tElectrons', '1tMuons', '2lMuonsOrth']
    if FinalState == 'spdl_comb': FinalStates = ['2lMuonsOrth','1tElectrons', '1tMuons']
    if FinalState == 'spdlinc_comb': FinalStates = ['2lMuons','1tElectrons', '1tMuons']    
    if FinalState == 'spdm_comb': FinalStates = ['2lMuonsOrth']
    if FinalState == 'spdminc_comb': FinalStates = ['2lMuons']    
    if FinalState == '1tElectrons_comb': FinalStates = ['1tElectrons']
    if FinalState == '1tMuons_comb': FinalStates = ['1tMuons']    
    from glob import glob
    print('gonna glob', outdcdir+'*'+FinalStates[0]+'*Phase1*')    
    flagshipfilenames = glob(outdcdir+'*'+FinalStates[0]+'*Phase1*')
    if 'inc' in FinalState: flagshipfilenames = [file for file in flagshipfilenames if not 'Orth' in file]
    for flagshipfilename in flagshipfilenames:
        cmd = 'combineCards.py '+flagshipfilename+' '
        precisestr = flagshipfilename.split('_dm')[-1].split('GeV')[0]
        coarsestr = str(round(float(precisestr.replace('p','.'))-0.003,2)).replace('.','p')
        mass = float(flagshipfilename.split('_dm')[0].split('GeV')[0].split('ne')[-1].split('pm')[-1])
        if not mass<501: continue
        print(precisestr, coarsestr)
        coarsename = flagshipfilename.replace('Phase1','Phase0').replace(precisestr,coarsestr)
        if not os.path.exists(coarsename): 
            coarsestr = str(round(float(precisestr.replace('p','.'))+0.003,2)).replace('.','p')
            print(precisestr, coarsestr)            
            coarsename = flagshipfilename.replace('Phase1','Phase0').replace(precisestr,coarsestr)
        if not os.path.exists(coarsename): 
            coarsestr = precisestr
            coarsename = flagshipfilename.replace('Phase1','Phase0').replace(precisestr,coarsestr)            
        cmd+=coarsename+' '  
        for fstate in FinalStates[1:]:
            cmd+=flagshipfilename.replace(FinalStates[0],fstate)+' '
            cmd+=flagshipfilename.replace(FinalStates[0],fstate).replace('Phase1','Phase0').replace(precisestr,coarsestr)+' '  +' '
        cmd+='> '+flagshipfilename.replace(FinalStates[0],FinalState).replace('Phase1','Run2')
        print (cmd)
        os.system(cmd)
    exit(0)
    
if FinalState == 'spdl_dt_comb': 
    FinalStates = ['DT','spdl_comb']
    from glob import glob
    flagshipfilenames = glob(outdcdir+'*'+FinalStates[0]+'*')
    print ('flagshipfilenames', flagshipfilenames)
    for flagshipfilename in flagshipfilenames:
        cmd = 'combineCards.py  '+flagshipfilename+' '
        for fstate in FinalStates[1:]:
            print ('here we aa', flagshipfilename, flagshipfilename.split('dm')[-1].split('GeV')[0])
            precisenumber = float(flagshipfilename.split('dm')[-1].split('GeV')[0].replace('p','.'))
            roundednumber = str(round(precisenumber-0.001, 2)).replace('.','p')
            precisenumber = str(precisenumber).replace('.','p')
            flagshipfilename_ = flagshipfilename.replace(precisenumber,roundednumber)
            if os.path.exists(flagshipfilename.replace(FinalStates[0],fstate)): flagshipfilename_ = flagshipfilename
            cmd+=flagshipfilename_.replace(FinalStates[0],fstate)+' '
        cmd+='> '+flagshipfilename.replace(FinalStates[0],FinalState)
        print (cmd)
        os.system(cmd)
    exit(0)
    



hobs.SetName('data_obs')

if not os.path.exists(outrootdir):
    os.system('mkdir -p '+outrootdir)

if not os.path.exists(outdcdir):
    os.system('mkdir -p '+outdcdir)



def improvedSystNaming(syst):
    # Dictionary mapping old systematics to new improved names
    syst_map = {
        'BTag': 'CMS_btag_comb',
        'Dedx': 'Dedx',  # Keeping the same as no new name was provided
        'DtSfLong': 'DtSfLong',  # Assuming specific to your analysis
        'DtSfShort': 'DtSfShort',  # Assuming specific to your analysis
        'Isr': 'ps_isr',
        'Jec': 'CMS_scale_j',
        'Scale': 'QCDscale_BSMsignal',  # Example replacement, update as needed
        'TrgEff': 'CMS_eff_m_trigger_13TeV',
        'MuSf': 'CMS_scale_m',
        'ElSf': 'CMS_scale_e'
    }
    
    # Return the improved name if it exists in the map, otherwise return the original name
    return syst_map.get(syst, syst)  # If the systematic is not found in the map, return it unchanged


# DATACARD CONTENT
# Write the datacard beginning lines
cnt = '''imax %d number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
#SHRINKFACTOR=%f
------------------------------------------------------------
observation                                %s
------------------------------------------------------------
'''
# Number of background processes
nbg = str(len(procs) - 1)

if modelname == 'PureHiggsino':
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
            print ("*******:", modelpoint)        
    else: 
        hsig = f.Get(sighistname)
        modelpoint = sighistname
        modelpoint = modelpoint.replace("pm", "ne")
        if "pm" in modelpoint:
            print ("*******:", modelpoint)
    if 'Norm' in modelpoint: continue
    froot = modelpoint.replace("AnalysisHists", "limitinput") + Era+'.root'
    fdatacard = modelpoint.replace("AnalysisHists", "datacard").replace(FinalState,'_'+FinalState) + Era+'.txt'

    if not FinalState in fdatacard: fdatacard = fdatacard.replace('.txt','_'+FinalState+'.txt')
    # Get signal histograms
    #hsig = fs.Get('hLongBaselineSystNom_BinNumberTruth')
    zero_out_certain_bins(hsig, binstozero)
    hsig.SetName('Signal')
    if FinalState=='DT':
        for sys in sigsysts: # will need some help once Yuval computes systematics
            sighistsup[sys] = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth')
            sighistsup[sys].SetName('Signal_'+sys+'Up')
            sighistsdn[sys] = fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
            sighistsdn[sys].SetName('Signal_'+sys+'Down')
            zero_out_certain_bins(sighistsup[sys], binstozero)
            zero_out_certain_bins(sighistsdn[sys], binstozero)
    if FinalState in ['2lMuonsOrth','2lMuons', '1tMuons','1tElectrons']:
        for sys in sigsysts: # will need some help once Yuval computes systematics
            print('getting some help from', sighistname+'_'+sys+'Up from', f.GetName())
            sighistsup[sys] = f.Get(sighistname+'_'+sys+'Up')
            sighistsup[sys].SetName('Signal_'+sys+'Up')
            sighistsdn[sys] = f.Get(sighistname+'_'+sys+'Down')
            sighistsdn[sys].SetName('Signal_'+sys+'Down')
            zero_out_certain_bins(sighistsup[sys], binstozero)
            zero_out_certain_bins(sighistsdn[sys], binstozero)            

    # Make the output file
    #if os.path.exists(outrootdir+'/'+froot): continue
    fr = TFile(outrootdir+'/'+froot, 'RECREATE')
    # Write histograms to the output file
    if UseShrinkFactor and hsig.Integral()>0: shrinkfactor = 10./hsig.GetMaximum()
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
        #ndatac.append('%-14s' % int(hobs.GetBinContent(ibin)) + ('%-14s' % '')*(len(procs)-1))
        ndatac.append('%-14s' % int(round(hobs.GetBinContent(ibin))) + ('%-14s' % '')*(len(procs)-1))
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
    row = '%-42s ' % 'bin'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for i in procs:
        row = row+'%-14s' % ('SR'+str(ibin))
    fd.write(row+'\n')
    row = '%-42s ' % 'process'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for i in procs:
        row = row+'%-14s' % i
    fd.write(row+'\n')
    row = '%-42s ' % 'process'
    for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
      for i in range(len(procs)):
        row = row+'%-14i' % i
    fd.write(row+'\n')
    row = '%-42s ' % 'rate'
    for y in yields:
        row = row+'%-14s' % str(round(y,3))
    fd.write(row+'\n')

    # Add random systematics
    cnt2 = '''-----------------------------------------
'''
    cnt2 += '''lumi_13TeV_correlated                lnN   '''+('1.013         '+'-             '*(len(procs)-1))*hobs.GetXaxis().GetNbins()+'''
'''
#    Closure  shape  -         1.0        1.0        1.0
    fd.write(cnt2)
    for sys in sigsysts:
        rowc = []
        #rowc.append('%-14s ' % sys.strip() +'%-6s ' % 'lnN')
        rowc.append('%-14s ' % improvedSystNaming(sys) +'%-6s ' % 'lnN')
        
        if FinalState=='DT': 
            hup, hdown = fs.Get('hBaselineSyst'+sys+'Up_BinNumberTruth'), fs.Get('hBaselineSyst'+sys+'Down_BinNumberTruth')
        if FinalState in ['2lMuonsOrth','2lMuons','1tMuons','1tElectrons']: 
            hup, hdown = f.Get(sighistname+'_'+sys+'Up'), f.Get(sighistname+'_'+sys+'Down')
        hup.Scale(shrinkfactor), hdown.Scale(shrinkfactor)
        for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
          for p in procs:
              relevant = p=='Signal'
              if relevant:
                  if (hsig.GetBinContent(ibin)>0.01 and hup.GetBinContent(ibin)>0.01 and hdown.GetBinContent(ibin)>0.01) and not abs(hup.GetBinContent(ibin)==hdown.GetBinContent(ibin)): 
                      thingup, thingdown = hup.GetBinContent(ibin)/hsig.GetBinContent(ibin), hdown.GetBinContent(ibin)/hsig.GetBinContent(ibin)
                      rowc.append('%-14s' % (str(round(thingup,3))+'/'+str(round(thingdown,3))))
                  else: rowc.append('%-14s' % ('1.0'))
              else: rowc.append('%-14s' % ('-'))
        row = ''.join(rowc)
        fd.write(row+'\n')
    if FinalState=='DT':
        fd.write('''ShowerShortOne lnN    '''+'''-             -             -             -             -             -             -             -             -             2.0            -             -             -             2.0            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
    if ApplyCorrelatedPromptSyst: 
        fd.write('''ShowerLongSyst lnN    '''+'''-            1.2            -             -             -            1.2            -             -             -              -            -             -             -              -            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
    if ApplyCorrelatedFakeSyst: 
        fd.write('''FakeLongSyst lnN      '''+'''-             -             -            1.3            -             -             -            1.3            -              -            -             -             -              -            -             -             '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')
        fd.write('''FakeShortSyst lnN     '''+'''-             -             -             -             -             -             -              -            -              -            -            1.3            -              -            -            1.3            '''*int(hobs.GetXaxis().GetNbins()/4)+'''-             '''*4+'\n')        
    if FinalState=='DT':
        for bgsys in bgsysts:
          #print 'bgsys', bgsys
          hup, hdown = fmaster.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Up'), fmaster.Get('h'+bgsys[0]+'BaselineMASTER_BinNumberMethod'+bgsys[1]+bgsys[2]+'Down')
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
    else: 
        for bgsys in bgsysts:
          #print 'bgsys', bgsys
          hname = 'bg'+FinalState+'_'.join(bgsys).replace('Qq','Charge')
          #print('getting', hname)
          hsys = fmaster.Get(hname)
          #hsys.Divide(gDirectory.Get(bgsys[0]))
          rowc = []
          rowc.append('%-37s' % (bgsys[0]+bgsys[1]+'_'+Era)+('%-5s ' % 'lnN'))
          for ibin in range(1,hobs.GetXaxis().GetNbins()+1):
            for p in procs:
                relevant = p==bgsys[0]
                if relevant:
                    if gDirectory.Get(p).GetBinContent(ibin)>0: rowc.append('%-14s' % (str(round(hsys.GetBinContent(ibin)/gDirectory.Get(p).GetBinContent(ibin),3))))
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
            nuisname = FinalState+'_gma'+p.strip()+str(ibin)+'_'+Era
            rowc.append('%-42s ' % (nuisname+' gmN '+linestem))
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

