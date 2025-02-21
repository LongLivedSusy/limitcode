#/usr/bin/env python

import os,sys
from ROOT import *
from string import *



try: FinalState = sys.argv[1]
except: 
    FinalState = '1tMuons'
    FinalState = '2lMuonsOrth'
    FinalState = '1tElectrons'
    FinalState = '2lElectrons'
    FinalState = 'spdl_comb'
    FinalState = 'spdl_dt_comb'
    FinalState = ''
    
try: Era = sys.argv[2]
except: 
    Era = '2016'
    Era = ''

firstwave = False #toggle this from now on

if firstwave:
    doStep1 = True #these things make it speedy because we want to run a bunch of combine 
    doStep2 = False # commands in parallel, but not harvest them til things have simmered down
else:
    doStep1 = False
    doStep2 = True


alsoDoSignificances = True
#--------------

# Gt the cross sections
box = FinalState+Era
modelname = 'T1qqqqLL'
modelname = 'T2btLL'
modelname = 'PureHiggsino'
#modelname = 'PureWino'

date = '220821'
date = 'asimov1923' 
date = '29Nov2022'
date = '30Nov2022'
date = '1Dec2022'
date = '23Mar2023'#yuval full status
date = '19Apr2023'#yuval's unblidned results
date = '24June2023' # new DT with higher resolution
date = '31Aug2023' # fix to hT weighting and added more data points
date = '17Nov2023' # these are now Yuval's newest inputs
#date = '22Feb2023'#me in Nov trying to redo Yuval's FS
date = '27Nov2023'# sam forges ahead
date = '7Dec2023'# Moritz pre-daddy party
date = '14Dec2023'# Moritz pre-daddy party
date = '19Dec2023'# sams dilepton code with sams skims, 
date = '22Dec2023'# sam adds 3 systematics
#date = '31Aug2023b' # coming back to DT official limits but fixing a big
date = '14Feb2024'# moritz lumi scaled 2016Pre
date = '16Feb2024'# moritz lumi scaled with MC
date = '7March2024'# sam adds 4 systematics
date = '7March2024systnone'# sam adds 4 systematics
date = '12March2024'# sam fixed a normalization issue
date = '18April2024' #yuval's top-up
date = '13Aug2024'#adding 3 systematics 
#date = '21Sep2024'# very soft dilepton
#date = '22Sep2024'# Moritz Higgsino
date = '31Oct2024' #round yuval not floor
date = '18Nov2024'#yuval unblinding
date = '23Jan2025'#Moritz freeze for preapproval
date = '28Jan2025'#Moritz freeze for preapproval, no really this time I'm sure!
date = '29Jan2025SplitBin'#moritz
date = '2Feb2025FastSimLFits'#moritz
date = '3Feb2025'#Moritz freeze really really really pinky promise
date = '16Feb2025'#Moritz post-preapproval
date = '17Feb2025'#Moritz post-preapproval, shrunken thingy
date = '19Feb2025'#Moritz private unblinding

dcdir = 'datacards/'+date+'/'+modelname+'/'
limitdir = 'limitsroot/'+date+'/'+modelname+'/'
limit2dir = 'limits2root/'+date+'/'+modelname+'/'
logdir = 'logfiles/'+date+'/'+modelname+'/'
if not os.path.exists(limitdir):
    os.system('mkdir -p '+limitdir)
if not os.path.exists(limit2dir):
    os.system('mkdir -p '+limit2dir)
if not os.path.exists(logdir):
    os.system('mkdir -p '+logdir)
    
print('logdir', logdir)


if modelname=='PureHiggsino': 
    higgsinoxsecfile = TFile('usefulthings/CN_hino_13TeV.root')
    hinoxsec_100to150_ = higgsinoxsecfile.Get('fit_nom_0')
    hinoxsec_150to200 = higgsinoxsecfile.Get('fit_nom_1')
    hinoxsec_200to300 = higgsinoxsecfile.Get('fit_nom_2')
    hinoxsec_300to400 = higgsinoxsecfile.Get('fit_nom_3')
    hinoxsec_400to600 = higgsinoxsecfile.Get('fit_nom_4')
    hinoxsec_600to800 = higgsinoxsecfile.Get('fit_nom_5')
    hinoxsec_800to1000 = higgsinoxsecfile.Get('fit_nom_6')
    hinoxsec_1000to1200 = higgsinoxsecfile.Get('fit_nom_7')
    hinoxsec_1200to1500 = higgsinoxsecfile.Get('fit_nom_8')
    
if 'Wino' in modelname:
    winoxsecfile_cn = TFile('usefulthings/C1N2_wino_13TeV.root'); winoxsecfile_cc = TFile('usefulthings/C1C1_wino_13TeV.root')
    winoxsec_100to150_cn = winoxsecfile_cn.Get('fit_nom_0'); winoxsec_100to150_cc = winoxsecfile_cc.Get('fit_nom_0')
    winoxsec_150to200_cn = winoxsecfile_cn.Get('fit_nom_1'); winoxsec_150to200_cc = winoxsecfile_cc.Get('fit_nom_1')
    winoxsec_200to300_cn = winoxsecfile_cn.Get('fit_nom_2'); winoxsec_200to300_cc = winoxsecfile_cc.Get('fit_nom_2')
    winoxsec_300to400_cn = winoxsecfile_cn.Get('fit_nom_3'); winoxsec_300to400_cc = winoxsecfile_cc.Get('fit_nom_3')
    winoxsec_400to600_cn = winoxsecfile_cn.Get('fit_nom_4'); winoxsec_400to600_cc = winoxsecfile_cc.Get('fit_nom_4')
    winoxsec_600to800_cn = winoxsecfile_cn.Get('fit_nom_5'); winoxsec_600to800_cc = winoxsecfile_cc.Get('fit_nom_5')
    winoxsec_800to1000_cn = winoxsecfile_cn.Get('fit_nom_6'); winoxsec_800to1000_cc = winoxsecfile_cc.Get('fit_nom_6')
    winoxsec_1000to1200_cn = winoxsecfile_cn.Get('fit_nom_7'); winoxsec_1000to1200_cc = winoxsecfile_cc.Get('fit_nom_7')
    winoxsec_1200to1500_cn = winoxsecfile_cn.Get('fit_nom_8') ; winoxsec_1200to1500_cc = winoxsecfile_cc.Get('fit_nom_8')




def writeTree(box, modelname, limit2dir, mchipm, dm, xsecULObs, xsecULExpPlus2, xsecULExpPlus, xsecULExp, xsecULExpMinus, xsecULExpMinus2, signif):
    #tmpFileName = "%s/%s_xsecUL_mchipm_%s_dm_%s_%s.root" %("/tmp", modelname, mg, mchi, box)
    outputFileName = "%s/%s_xsecUL_mchipm_%s_dm_%s_%s.root" %(limit2dir, modelname, mchipm, dm, box)
    print('creating', outputFileName)
    fileOut = TFile.Open(outputFileName, "recreate")

    if 1==1:
        xsecTree = TTree("xsecTree", "xsecTree")
        try:
            from ROOT import MyStruct
        except ImportError:
            myStructCmd = "struct MyStruct{Double_t mchipm;Double_t dm; Double_t x; Double_t y;"
            ixsecUL = 0
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+0)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+1)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+2)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+3)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+4)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+5)
            myStructCmd+= "Double_t Significance;"            
            ixsecUL+=6
            myStructCmd += "}"
            gROOT.ProcessLine(myStructCmd)
            from ROOT import MyStruct
        
        s = MyStruct()
        xsecTree.Branch("mchipm", AddressOf(s,"mchipm"),'mchipm/D')
        xsecTree.Branch("dm", AddressOf(s,"dm"),'dm/D')
        xsecTree.Branch("x", AddressOf(s,"x"),'x/D')
        xsecTree.Branch("y", AddressOf(s,"y"),'y/D')    
    
    s.mchipm = mchipm
    s.dm = dm
    if 'T1x' in modelname:
        s.x = float(modelname[modelname.find('x')+1:modelname.find('y')].replace('p','.'))
        s.y = float(modelname[modelname.find('y')+1:].replace('p','.'))
    elif modelname == 'T1bbbb':
        s.x = 1
        s.y = 0
    elif modelname == 'T1tttt':
        s.x = 0
        s.y = 1
    else:
        s.x = -1
        s.y = -1

    ixsecUL = 0
    xsecTree.Branch("xsecULObs_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+0)),'xsecUL%i/D'%(ixsecUL+0))
    xsecTree.Branch("xsecULExpPlus2_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+1)),'xsecUL%i/D'%(ixsecUL+1))
    xsecTree.Branch("xsecULExpPlus_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+2)),'xsecUL%i/D'%(ixsecUL+2))
    xsecTree.Branch("xsecULExp_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+3)),'xsecUL%i/D'%(ixsecUL+3))
    xsecTree.Branch("xsecULExpMinus_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+4)),'xsecUL%i/D'%(ixsecUL+4))
    xsecTree.Branch("xsecULExpMinus2_%s"%box, AddressOf(s,"xsecUL%i"%(ixsecUL+5)),'xsecUL%i/D'%(ixsecUL+5))
    xsecTree.Branch("Significance_%s"%box, AddressOf(s,"Significance"),'Significance/D')

    exec('s.xsecUL%i = xsecULObs[ixsecUL]'%(ixsecUL+0))
    exec('s.xsecUL%i = xsecULExpPlus2[ixsecUL]'%(ixsecUL+1))
    exec('s.xsecUL%i = xsecULExpPlus[ixsecUL]'%(ixsecUL+2))
    exec('s.xsecUL%i = xsecULExp[ixsecUL]'%(ixsecUL+3))
    exec('s.xsecUL%i = xsecULExpMinus[ixsecUL]'%(ixsecUL+4))
    exec('s.xsecUL%i = xsecULExpMinus2[ixsecUL]'%(ixsecUL+5))
    exec('s.Significance = signif')    
    ixsecUL += 4
    
    xsecTree.Fill()
    
    fileOut.cd()
    xsecTree.Show(0)
    xsecTree.Write()
    
    fileOut.Close()
    
    #outputFileName = "%s/%s_xsecUL_mchipm_%s_dm_%s_%s.root" %(limit2dir, modelname, mchipm, dm, box)
    print("INFO: xsec UL values being written to %s"%outputFileName)
    
    #special_call(["mv",tmpFileName,outputFileName],0)
        
    return outputFileName



print("this is where it's kind of all starting from in the limit stuff", dcdir)

if not 'Orth' in FinalState: datacards =[file.strip() for file in os.popen('ls '+dcdir+'*'+FinalState+'*'+Era+'.txt').readlines() if 'Orth' not in file]
else: datacards = os.popen('ls '+dcdir+'*'+FinalState+'*'+Era+'.txt').readlines()#*mChipm100GeV_dm0p46


# write results to a tree
xsecULObs	= 0.
xsecULExpMinus2 = 0.
xsecULExpMinus  = 0.
xsecULExp	= 0.
xsecULExpPlus   = 0.
xsecULExpPlus2  = 0.
signif          = 0.

#[0,250]
#[0,5]

gameon = False
gameon = True
icmd = 1
for datacard in datacards:
    if not FinalState in datacard: 
        continue # this is superfluous
    
    #if not 'mChine115GeV_dm1p268GeV' in datacard:
    #    continue
    print(datacard)
            
      
    ##if not '100GeV_dm0p259' in datacard: continue      
    #if not gameon:
    #    if '300GeV_dm3p315GeV' in datacard: 
    #       gameon = True
    #    else: continue
        
    datacard = datacard.strip()
    fln = datacard.split('/')[3].split('.')[0].replace("datacard", "") .replace('Chine','Chipm')

    logfile = logdir+fln+'.log'
    print('Running:', fln)
    #get shrink factor:
    cardlines = open(datacard).readlines()
    shrinkfactor = 1.0
    for line in cardlines:
        if 'SHRINKFACTOR' in line:
            shrinkfactor = float(line.strip().split('=')[-1])
            break
    print('got shrinker', shrinkfactor)
            
    if alsoDoSignificances: 
        #cmd = 'combine -M AsymptoticLimits ' + datacard + ' --name ' + fln + ' --setParameters r=0.1 >& ' + logfile + ' && combine -M Significance ' + datacard + ' --name ' + fln + '_sig --setParameters r=0.1 -t 0 >> ' + logfile
        cmd = 'combine -M AsymptoticLimits ' + datacard + ' --name ' + fln + ' --setParameters r=0.1 >& ' + logfile + ' && combine -M HybridNew ' + datacard + '  --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 50 -i 10 -s -1 >> ' + logfile
         
    else: cmd = 'combine -M AsymptoticLimits '+datacard+' --name '+fln+' --setParameters r=0.1 >& '+logfile
    #cmd = 'combine -M HybridNew ' + datacard + ' --name ' + fln + ' --setParameters r=0.1 --testStat LHC >& ' + logfile
    if not icmd%16==0: cmd+=' &'#cores
    print(cmd)
    if doStep1: os.system(cmd)
    icmd+=1
    limitfln = limitdir+'higgsCombine'+fln+'.AsymptoticLimits.mH120.root'
    if doStep2: os.system('mv *'+fln+'*.root '+limitfln)    
    print('limitfln', limitfln)
    if 'SDP' in FinalState:
        mparent = float(limitfln.split('mChi')[-1].split('_dm')[0])
        deltam = float(limitfln.split('_dm')[-1].split('_'+FinalState)[0].replace('p','.'))
    elif 'DT' in FinalState:
        print('what we got to work with:', limitfln)
        mparent = float(limitfln[limitfln.find('mChipm')+6:limitfln.find('GeV_dm')])
        deltam = float(limitfln[limitfln.find('_dm')+3:limitfln.find('GeV_'+FinalState)].replace('p','.'))
    elif '1t' in FinalState or '2l' in FinalState or 'spd' in FinalState:
        print('operating on', limitfln   )
        mparent = float(limitfln[limitfln.find('mChipm')+6:limitfln.find('GeV_dm')])
        #deltam = float(limitfln[limitfln.find('_dm')+3:limitfln.rfind('GeV_')].replace('p','.'))
        deltam = float(limitfln[limitfln.find('_dm')+3:limitfln.rfind('GeV')].replace('p','.'))
    elif FinalState=='SDM':
        print('operating on', limitfln  , limitfln[limitfln.find('_M')+2:limitfln.find('GeV_dm')])
        mparent = float(limitfln[limitfln.find('_M')+2:limitfln.find('GeV_dm')])
        #deltam = float(limitfln[limitfln.find('_dm')+3:limitfln.rfind('GeV_')].replace('p','.'))
        deltam = float(limitfln[limitfln.find('_dm')+3:limitfln.rfind('_SDM')].replace('p','.'))/2.0 
        
    if deltam<0.14:
        print('skipping below pion mass')
        continue#don't interpret below the pion mass

    '''
    mparent = float(limitfln[limitfln.find('M')+1:limitfln.find('Dm')])
    deltam = float(limitfln[limitfln.find('Dm')+2:limitfln.rfind('.Asym')].replace('p','.'))
    '''
    
    if not doStep2: continue
    
    print('dissecting', limitfln)

    print('logfile', logfile)

    
    log = open(logfile).readlines()
    if modelname == 'PureHiggsino':
        if mparent<150: refXsec = 0.001*hinoxsec_100to150_.Eval(mparent)
        elif mparent>150 and mparent<200: refXsec = 0.001*hinoxsec_150to200.Eval(mparent)
        elif mparent>=200 and mparent<300: refXsec = 0.001*hinoxsec_200to300.Eval(mparent)
        elif mparent>=300 and mparent<400: refXsec = 0.001*hinoxsec_300to400.Eval(mparent)
        elif mparent>=400 and mparent<600: refXsec = 0.001*hinoxsec_400to600.Eval(mparent)
        elif mparent>=600 and mparent<800: refXsec = 0.001*hinoxsec_600to800.Eval(mparent)
        elif mparent>=800 and mparent<1000: refXsec = 0.001*hinoxsec_800to1000.Eval(mparent)
        elif mparent>=1000 and mparent<1200: refXsec = 0.001*hinoxsec_1000to1200.Eval(mparent) 
        elif mparent>1200:                 refXsec = 0.001*hinoxsec_1200to1500.Eval(mparent) 
    if 'Wino' in modelname:
        if mparent<150:                  refXsec = 0.001*(winoxsec_100to150_cn.Eval(mparent)+winoxsec_100to150_cc.Eval(mparent))
        elif mparent>150 and mparent<200: refXsec = 0.001*(winoxsec_150to200_cn.Eval(mparent)+winoxsec_150to200_cc.Eval(mparent))
        elif mparent>=200 and mparent<300: refXsec = 0.001*(winoxsec_200to300_cn.Eval(mparent)+winoxsec_200to300_cc.Eval(mparent))
        elif mparent>=300 and mparent<400: refXsec = 0.001*(winoxsec_300to400_cn.Eval(mparent)+winoxsec_300to400_cc.Eval(mparent))
        elif mparent>=400 and mparent<600: refXsec = 0.001*(winoxsec_400to600_cn.Eval(mparent)+winoxsec_400to600_cc.Eval(mparent))
        elif mparent>=600 and mparent<800: refXsec = 0.001*(winoxsec_600to800_cn.Eval(mparent)+winoxsec_600to800_cc.Eval(mparent))
        elif mparent>=800 and mparent<1000: refXsec = 0.001*(winoxsec_800to1000_cn.Eval(mparent)+winoxsec_800to1000_cc.Eval(mparent))
        elif mparent>=1000 and mparent<1200: refXsec = 0.001*(winoxsec_1000to1200_cn.Eval(mparent) +winoxsec_1000to1200_cc.Eval(mparent))
        elif mparent>1200:                 refXsec = 0.001*(winoxsec_1200to1500_cn.Eval(mparent)+winoxsec_1200to1500_cc.Eval(mparent))
    print(mparent, refXsec)

    #refXsec = 1

    xsecULObs	= 0.
    xsecULExpMinus2 = 0.
    xsecULExpMinus  = 0.
    xsecULExp	= 0.
    xsecULExpPlus   = 0.
    xsecULExpPlus2  = 0.
    signif          = 0.    

    for line in log:
        if "Observed Limit:" in line:
            xsecULObs = refXsec*float(line.split()[4])*shrinkfactor
        elif "Expected  2.5%:" in line:
            xsecULExpMinus2 = refXsec*float(line.split()[4])*shrinkfactor
        elif "Expected 16.0%:" in line:
            xsecULExpMinus = refXsec*float(line.split()[4])*shrinkfactor
        elif "Expected 50.0%:" in line:
            xsecULExp = refXsec*float(line.split()[4])*shrinkfactor
        elif "Expected 84.0%:" in line:
            xsecULExpPlus = refXsec*float(line.split()[4])*shrinkfactor
        elif "Expected 97.5%:" in line:
            xsecULExpPlus2 = refXsec*float(line.split()[4])*shrinkfactor
        elif "Significance:" in line:
            signif = float(line.split()[1])
    if xsecULExp==0.: xsecULObs = 0. 

    writeTree(box, modelname, limit2dir, float(mparent), float(deltam), [xsecULObs], [xsecULExpPlus2], [xsecULExpPlus], [xsecULExp], [xsecULExpMinus], [xsecULExpMinus2], signif)
print('we done')

