#!/usr/bin/env python

import os, sys
from ROOT import *
from string import *

# Physics processes
procs = [
    'Signal',
    'Prompt',
    'Spurious',
    'Tau'
]

# Main and alternate root files
date = '23Jan2025'#Moritz freeze for preapproval
date = '28Jan2025'#Moritz freeze for preapproval, no really this time I'm sure!
date = '29Jan2025SplitBin'
date = '2Feb2025FastSimLFits'
date = '3Feb2025'#Moritz freeze really really really pinky promise
date = '16Feb2025'#Moritz post-preapproval
date = '17Feb2025'#Moritz post-preapproval, shrunken thingy
date = '19Feb2025'#Moritz private unblinding

masterfile = TFile('FromMoritz/'+date+'/histos_20250219.root')
alternatefile = TFile('FromMoritz/'+date+'/histos_20250219_mcshapecorr.root')

#masterfile = TFile('FromMoritz/'+date+'/histos_20250217_2018signalfullsim.root')
#alternatefile = TFile('FromMoritz/'+date+'/histos_20250217_2018signalfullsim_mcshapecorr.root')

lumiscale = 138. / 17.
folderkeys = masterfile.GetListOfKeys()

foldernames = []
for key in folderkeys:
    if not 'signal' in key.GetName(): continue
    foldernames.append(key.GetName())

# Background histograms from main file
hbkg = masterfile.Get('STACK/sumsignalregions').Clone('SM')
#hobs = hbkg.Clone('data_obs')
hobs = masterfile.Get('data/datasignalregions')
hprompt = masterfile.Get('notau/notausignalregions').Clone('Prompt')
hspurious = masterfile.Get('nogenmatch/nogenmatchsignalregions').Clone('Spurious')
htau = masterfile.Get('fromtruetau/fromtruetausignalregions').Clone('Tau')

# Load shape variations (identical for all model points)
hprompt_var = alternatefile.Get('notau/notausignalregions').Clone('Prompt_variation')
hspurious_var = alternatefile.Get('nogenmatch/nogenmatchsignalregions').Clone('Spurious_variation')
htau_var = alternatefile.Get('fromtruetau/fromtruetausignalregions').Clone('Tau_variation')

# Normalize variations
hprompt_var.Scale(hprompt.Integral() / hprompt_var.Integral())
hspurious_var.Scale(hspurious.Integral() / hspurious_var.Integral())
htau_var.Scale(htau.Integral() / htau_var.Integral())

# Compute "Down" variations
hprompt_var_down = hprompt.Clone("Prompt_PromptShapeDown")
hspurious_var_down = hspurious.Clone("Spurious_SpuriousShapeDown")
htau_var_down = htau.Clone("Tau_TauShapeDown")

for i in range(1, hprompt.GetNbinsX() + 1):
    hprompt_var_down.SetBinContent(i, max(0, hprompt.GetBinContent(i) * (2 - (hprompt_var.GetBinContent(i) / hprompt.GetBinContent(i)))))
    hspurious_var_down.SetBinContent(i, max(0, hspurious.GetBinContent(i) * (2 - (hspurious_var.GetBinContent(i) / hspurious.GetBinContent(i)))))
    htau_var_down.SetBinContent(i, max(0, htau.GetBinContent(i) * (2 - (htau_var.GetBinContent(i) / htau.GetBinContent(i)))))

modelname = 'PureHiggsino'

outrootdir = 'sigbgobsroot/' + date + '/' + modelname + '/'
outdcdir = 'datacards/' + date + '/' + modelname + '/'

if not os.path.exists(outrootdir):
    os.makedirs(outrootdir)
if not os.path.exists(outdcdir):
    os.makedirs(outdcdir)

# Datacard content template
cnt = '''imax 1 number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
------------------------------------------------------------
observation     %s
------------------------------------------------------------
shapes * * %s $PROCESS $PROCESS_$SYSTEMATIC
shapes Prompt * %s Prompt Prompt_$SYSTEMATIC
shapes Spurious * %s Spurious Spurious_$SYSTEMATIC
shapes Tau * %s Tau Tau_$SYSTEMATIC
------------------------------------------------------------
'''

# Number of background processes
nbg = str(len(procs) - 1)

for f in foldernames:
    histname2get = f + '/' + f + 'signalregions'
    modelname = f.replace('signal_direct_', '')
    frn = modelname.replace("AnalysisHists", "limitinput") + '.root'
    fdn = modelname.replace("AnalysisHists", "datacard") + "_SDPRun2.txt"

    # Get signal histograms
    hsig = masterfile.Get(histname2get)
    hsig.SetName('Signal')

    # Make the output file
    fr = TFile(outrootdir + '/' + frn, 'RECREATE')

    # Write histograms to the output file
    hsig.Write()
    hprompt.Write()
    hspurious.Write()
    htau.Write()
    hobs.Write('data_obs')

    # Write shape variations
    hprompt_var.Write("Prompt_PromptShapeUp")
    hprompt_var_down.Write("Prompt_PromptShapeDown")
    hspurious_var.Write("Spurious_SpuriousShapeUp")
    hspurious_var_down.Write("Spurious_SpuriousShapeDown")
    htau_var.Write("Tau_TauShapeUp")
    htau_var_down.Write("Tau_TauShapeDown")

    print(f"Just wrote ROOT file: {outrootdir + frn}")

    # Create the datacard
    fd = open(outdcdir + '/' + fdn, 'w')

    # Number of data events
    ndata = str(hobs.Integral())
    fd.write(cnt % (nbg, ndata, outrootdir + frn, outrootdir + frn, outrootdir + frn, outrootdir + frn))

    # Yields for processes
    yields = []
    for p in procs:
        yields.append(gDirectory.Get(p).Integral())

    # Write processes and rates
    row = '%-31s ' % 'bin'
    for i in procs:
        row = row + '%-9s ' % 'SDP'
    fd.write(row + '\n')
    row = '%-31s ' % 'process'
    for i in procs:
        row = row + '%-9s ' % i
    fd.write(row + '\n')
    row = '%-31s ' % 'process'
    for i in range(len(procs)):
        row = row + '%-9i ' % i
    fd.write(row + '\n')
    row = '%-28s ' % 'rate'
    for y in yields:
        row = row + '%9.3f ' % y
    fd.write(row + '\n')

    # Add systematic uncertainties
    cnt2 = '''------------------------------------------------------------
lumi_13TeV            lnN      1.016        -            -            -      
CMS_scale_j           lnN      0.95/1.05    -            -            -      
promptScale           lnN       -          1.05         -            -      
spuriousScale         lnN       -           -           1.09         - 
tauScale              lnN       -           -            -           1.1
ddProxyEff            lnN       1.1        -            -            -      
CMS_pileup_13TeV      lnN       1.03        -            -            -
CMS_l1_ecal_prefiring lnN       1.02        -            -            -
PromptShape           shape       -         1.0          -            -
SpuriousShape         shape       -          -          1.0           -
TauShape              shape       -          -           -           1.0
------------------------------------------------------------
* autoMCStats 10 1
'''
    fd.write(cnt2)

    print(f"Just wrote datacard: {fd.name}")
    fd.close()
