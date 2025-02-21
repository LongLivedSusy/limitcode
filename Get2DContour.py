from optparse import OptionParser
import ROOT as rt
import sys
#import rootTools
import glob
from math import *
import os
from array import *
import numpy as np
from scipy.interpolate import Rbf, interp1d
import itertools
#from GChiPairs import gchipairs
import operator
import subprocess
import time

def euclidean_norm_numpy(x1, x2):
    return np.linalg.norm(x1 - x2, axis=0)

def pause():
        import sys
        print ('press enter')
        sys.stdout.flush()
        raw_input('')
    

#y_stretch_factor, x_stretch_factor = (1140-95)/1.2*5, 1 # for DTk - numbers derive from below
#y_stretch_factor, x_stretch_factor = (185-90)/5.2, 1 # for dilepton Yuval
#y_stretch_factor, x_stretch_factor = (185-90)/1.2, 1 # for soft pion
y_stretch_factor, x_stretch_factor = (205-90)/2.5, 1 # for soft pion full lumi
#y_stretch_factor, x_stretch_factor = (220-90)/10, 1 # oversized for Money plot
#90, 185, 0.0, 5.2
#from limits.SMSConfig import sms_models
# --------------- Import by hand ------------------------
import copy


DISP_OFFSET = .25 # Extra offset needed for display purposes
DISP_OFFSET = 0.0

date = '31Aug2023b'#DTk paper 
date = '30Nov2022'
date = '1Dec2022'
date = '23Mar2023'#yuval full status, and also DT final
#date = '19Apr2023'#yuval's unblidned results
#date = '24June2023'#update after PAS
#date = '31Aug2023' # second update after pas
date = '17Nov2023' # Yuval's ressurection
date = '27Nov2023'# sam forges ahead
date = '7Dec2023'# Moritz pre-daddy party
date = '14Dec2023'#alex
date = '19Dec2023'# sams dilepton code with sams skims, 
date = '22Dec2023'# sam adds 3 systematics, 
date = '14Feb2024'# moritz lumi scaled 2016Pre
date = '16Feb2024'# moritz lumi scaled with MC
date = '7March2024'# sam adds 4 systematics
date = '7March2024systnone'# sam adds 4 systematics
date = '12March2024'# sam fixed a normalization issue
date = '18April2024' #yuval's top-up
date = '13Aug2024'#adding 3 systematics
date = '22Sep2024'
date = '31Oct2024' #round
date = '18Nov2024'#yuval unblinding
date = '23Jan2025'#Moritz freeze for preapproval
date = '28Jan2025'#Moritz freeze for preapproval, no really this time I'm sure!
date = '29Jan2025SplitBin'
date = '2Feb2025FastSimLFits'
date = '3Feb2025'#Moritz freeze really really really pinky promise
date = '16Feb2025'#Moritz post-preapproval
date = '17Feb2025'#Moritz post-preapproval, shrunken thingy
date = '19Feb2025'#Moritz post-preapproval, shrunken thingy
#date = '18Nov2024'#yuval unblinding


class SMS(object):

    def __init__(self, mgMin, mgMax, mchiMin, mchiMax,
            binWidth=1.0, nRebins=5, xsecMin=1.e-5, xsecMax=10., 
            diagonalOffset=25, smoothing=1, fixLSP0=True,##normaally smoothing = 2
            boxes='', isGluino=True, submodels=None):
        """
        Struct to hold all info associated with one SMS.
        Attributes:
            mgMin, mgMax, mchiMin, mchiMax: mass bounds for limits
            binWidth: granularity of limit scan
            nRebins: number of times to iterate swiss cross interpolation
            xsecMin, xsecMax: z range on limit plot
            diagonalOffset: where the diagonal should be located
            smoothing: RBF smoothing parameter for interpolation
            fixLSP0: set to True to avoid smoothing away limit
                behavior at low LSP mass
            boxes: analysis boxes to use for this model
            isGluino: True if this is a gluino SMS
            submodels: lists MC datasets making up this scan
        """
        self.mgMin = mgMin - DISP_OFFSET
        self.mgMax = mgMax + DISP_OFFSET
        self.mchiMin = mchiMin# - DISP_OFFSET
        self.mchiMax = mchiMax# + DISP_OFFSET
        self.binWidth = binWidth
        self.nRebins = nRebins
        self.xsecMin = xsecMin
        self.xsecMax = xsecMax
        self.diagonalOffset = diagonalOffset + DISP_OFFSET
        self.smoothing = smoothing
        self.fixLSP0 = fixLSP0
        self.boxes = boxes
        self.isGluino = isGluino
        self.submodels = submodels

sms_models = {
        'T1bbbb':SMS(600, 2300, 0, 1650),
        'T1ttbb':SMS(600, 2300, 0, 1650,
            diagonalOffset=225),
        'T1tttt':SMS(600, 2300, 0, 1650,
            diagonalOffset=225),
        'T1qqqq':SMS(600, 2300, 0, 1650),
        'T1qqqqLL':SMS(1000, 2800, 1, 2700),        
        'T2bb':SMS(100, 1500, 0, 800,
            isGluino=False),
        'T2bt':SMS(100, 1500, 0, 800, isGluino=False),
        'T2btLL':SMS(400, 2500, 1, 2000, isGluino=False),
        'T2tt':SMS(100, 1500, 0, 800, isGluino=False,
            diagonalOffset=75, submodels=[
                'T2tt_dM-10to80_genHT-160_genMET-80',
                'T2tt_mStop-150to250',  
                'T2tt_mStop-250to350',
                'T2tt_mStop-350to400',
                'T2tt_mStop-400to1200',
                ]),
        'T2qq':SMS(100, 1500, 0, 800,
            isGluino=False),
        'T5ttcc':SMS(600, 2300, 0, 1650, diagonalOffset=110),
        'T5tttt':SMS(600, 2300, 0, 1650, diagonalOffset=225),
        'T5qqqqVV':SMS(600, 2300, 0, 1650),
        #'PureHiggsino':SMS(90, 185, 0.0, 5.2), ### Yuval's wide pannel and good one
        #'PureHiggsino':SMS(90, 220, 0.0, 10), ### oversized for Money plot
        #'PureHiggsino':SMS(90, 280, 0.0, 1.2), ###  DT in PAS??
        #'PureHiggsino':SMS(95, 1140, 0.0, 1.2,5), ###  DT try to make bigger for paper
        #'PureHiggsino':SMS(90, 185, 0.0, 1.2), ### Moritz
        'PureHiggsino':SMS(90, 215, 0.0, 2.5), ### Moritz full lumi!
        'PureWino':SMS(95, 1140, 0.0, 1.2,5), ###  DT same as above
}
# ------------------ End import by hand -----------------

fxsecs = {}
fxsecs['PureHiggsino'] = {}
fxsecs['PureWino'] = {}
hinoxsecfile = rt.TFile('usefulthings/CN_hino_13TeV.root')
fxsecs['PureHiggsino']['100to150']      = [hinoxsecfile.Get('fit_nom_0')]
fxsecs['PureHiggsino']['150to200']      = [hinoxsecfile.Get('fit_nom_1')]
fxsecs['PureHiggsino']['200to300']      = [hinoxsecfile.Get('fit_nom_2')]
fxsecs['PureHiggsino']['300to400']      = [hinoxsecfile.Get('fit_nom_3')]
fxsecs['PureHiggsino']['400to600']      = [hinoxsecfile.Get('fit_nom_4')]
fxsecs['PureHiggsino']['600to800']      = [hinoxsecfile.Get('fit_nom_5')]
fxsecs['PureHiggsino']['800to1000']     = [hinoxsecfile.Get('fit_nom_6')]
fxsecs['PureHiggsino']['1000to1200']    = [hinoxsecfile.Get('fit_nom_7')]
fxsecs['PureHiggsino']['1200to1500']    = [hinoxsecfile.Get('fit_nom_8')]
fxsecs['PureHiggsino']['100to150_up']   = [hinoxsecfile.Get('fit_up_0')]
fxsecs['PureHiggsino']['150to200_up']   = [hinoxsecfile.Get('fit_up_1')]
fxsecs['PureHiggsino']['200to300_up']   = [hinoxsecfile.Get('fit_up_2')]
fxsecs['PureHiggsino']['300to400_up']   = [hinoxsecfile.Get('fit_up_3')]
fxsecs['PureHiggsino']['400to600_up']   = [hinoxsecfile.Get('fit_up_4')]
fxsecs['PureHiggsino']['600to800_up']   = [hinoxsecfile.Get('fit_up_5')]
fxsecs['PureHiggsino']['800to1000_up']  = [hinoxsecfile.Get('fit_up_6')]
fxsecs['PureHiggsino']['1000to1200_up'] = [hinoxsecfile.Get('fit_up_7')]
fxsecs['PureHiggsino']['1200to1500_up'] = [hinoxsecfile.Get('fit_up_8')]
fxsecs['PureHiggsino']['100to150_dn']   = [hinoxsecfile.Get('fit_dn_0')]
fxsecs['PureHiggsino']['150to200_dn']   = [hinoxsecfile.Get('fit_dn_1')]
fxsecs['PureHiggsino']['200to300_dn']   = [hinoxsecfile.Get('fit_dn_2')]
fxsecs['PureHiggsino']['300to400_dn']   = [hinoxsecfile.Get('fit_dn_3')]
fxsecs['PureHiggsino']['400to600_dn']   = [hinoxsecfile.Get('fit_dn_4')]
fxsecs['PureHiggsino']['600to800_dn']   = [hinoxsecfile.Get('fit_dn_5')]
fxsecs['PureHiggsino']['800to1000_dn']  = [hinoxsecfile.Get('fit_dn_6')]
fxsecs['PureHiggsino']['1000to1200_dn'] = [hinoxsecfile.Get('fit_dn_7')]
fxsecs['PureHiggsino']['1200to1500_dn'] = [hinoxsecfile.Get('fit_dn_8')]

winoxsecfile_cn = rt.TFile('usefulthings/C1N2_wino_13TeV.root'); winoxsecfile_cc = rt.TFile('usefulthings/C1C1_wino_13TeV.root')
fxsecs['PureWino']['100to150']      = [winoxsecfile_cn.Get('fit_nom_0'), winoxsecfile_cc.Get('fit_nom_0')]
fxsecs['PureWino']['150to200']      = [winoxsecfile_cn.Get('fit_nom_1'), winoxsecfile_cc.Get('fit_nom_1')]
fxsecs['PureWino']['200to300']      = [winoxsecfile_cn.Get('fit_nom_2'), winoxsecfile_cc.Get('fit_nom_2')]
fxsecs['PureWino']['300to400']      = [winoxsecfile_cn.Get('fit_nom_3'), winoxsecfile_cc.Get('fit_nom_3')]
fxsecs['PureWino']['400to600']      = [winoxsecfile_cn.Get('fit_nom_4'), winoxsecfile_cc.Get('fit_nom_4')]
fxsecs['PureWino']['600to800']      = [winoxsecfile_cn.Get('fit_nom_5'), winoxsecfile_cc.Get('fit_nom_5')]
fxsecs['PureWino']['800to1000']     = [winoxsecfile_cn.Get('fit_nom_6'), winoxsecfile_cc.Get('fit_nom_6')]
fxsecs['PureWino']['1000to1200']    = [winoxsecfile_cn.Get('fit_nom_7'), winoxsecfile_cc.Get('fit_nom_7')]
fxsecs['PureWino']['1200to1500']    = [winoxsecfile_cn.Get('fit_nom_8'), winoxsecfile_cc.Get('fit_nom_8')]
fxsecs['PureWino']['100to150_up']   = [winoxsecfile_cn.Get('fit_up_0') , winoxsecfile_cc.Get('fit_up_0') ]
fxsecs['PureWino']['150to200_up']   = [winoxsecfile_cn.Get('fit_up_1') , winoxsecfile_cc.Get('fit_up_1') ]
fxsecs['PureWino']['200to300_up']   = [winoxsecfile_cn.Get('fit_up_2') , winoxsecfile_cc.Get('fit_up_2') ]
fxsecs['PureWino']['300to400_up']   = [winoxsecfile_cn.Get('fit_up_3') , winoxsecfile_cc.Get('fit_up_3') ]
fxsecs['PureWino']['400to600_up']   = [winoxsecfile_cn.Get('fit_up_4') , winoxsecfile_cc.Get('fit_up_4') ]
fxsecs['PureWino']['600to800_up']   = [winoxsecfile_cn.Get('fit_up_5') , winoxsecfile_cc.Get('fit_up_5') ]
fxsecs['PureWino']['800to1000_up']  = [winoxsecfile_cn.Get('fit_up_6') , winoxsecfile_cc.Get('fit_up_6') ]
fxsecs['PureWino']['1000to1200_up'] = [winoxsecfile_cn.Get('fit_up_7') , winoxsecfile_cc.Get('fit_up_7') ]
fxsecs['PureWino']['1200to1500_up'] = [winoxsecfile_cn.Get('fit_up_8') , winoxsecfile_cc.Get('fit_up_8') ]
fxsecs['PureWino']['100to150_dn']   = [winoxsecfile_cn.Get('fit_dn_0') , winoxsecfile_cc.Get('fit_dn_0') ]
fxsecs['PureWino']['150to200_dn']   = [winoxsecfile_cn.Get('fit_dn_1') , winoxsecfile_cc.Get('fit_dn_1') ]
fxsecs['PureWino']['200to300_dn']   = [winoxsecfile_cn.Get('fit_dn_2') , winoxsecfile_cc.Get('fit_dn_2') ]
fxsecs['PureWino']['300to400_dn']   = [winoxsecfile_cn.Get('fit_dn_3') , winoxsecfile_cc.Get('fit_dn_3') ]
fxsecs['PureWino']['400to600_dn']   = [winoxsecfile_cn.Get('fit_dn_4') , winoxsecfile_cc.Get('fit_dn_4') ]
fxsecs['PureWino']['600to800_dn']   = [winoxsecfile_cn.Get('fit_dn_5') , winoxsecfile_cc.Get('fit_dn_5') ]
fxsecs['PureWino']['800to1000_dn']  = [winoxsecfile_cn.Get('fit_dn_6') , winoxsecfile_cc.Get('fit_dn_6') ]
fxsecs['PureWino']['1000to1200_dn'] = [winoxsecfile_cn.Get('fit_dn_7') , winoxsecfile_cc.Get('fit_dn_7') ]
fxsecs['PureWino']['1200to1500_dn'] = [winoxsecfile_cn.Get('fit_dn_8') , winoxsecfile_cc.Get('fit_dn_8') ]

toFix = []
def interpolate2D(hist,epsilon=1,smooth=0,diagonalOffset=0,fixLSP0=False,refHist=None):

    #######return hist
    #return hist
    x = array('d',[])
    y = array('d',[])
    z = array('d',[])
    
    binWidth = float(hist.GetXaxis().GetBinWidth(1))
    
    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            if hist.GetBinContent(i,j)>0.:
                if refHist!=None and refHist.GetBinContent(i,j) > 0.:
                        x.append(hist.GetXaxis().GetBinCenter(i)*x_stretch_factor)
                        y.append(hist.GetYaxis().GetBinCenter(j)*y_stretch_factor)
                        z.append(rt.TMath.Log(hist.GetBinContent(i,j)/refHist.GetBinContent(i,j)))
                else:
                    x.append(hist.GetXaxis().GetBinCenter(i)*x_stretch_factor)
                    y.append(hist.GetYaxis().GetBinCenter(j)*y_stretch_factor)
                    z.append(rt.TMath.Log(hist.GetBinContent(i,j)))

    mgMin = hist.GetXaxis().GetBinCenter(1)#*x_stretch_factor
    mgMax = hist.GetXaxis().GetBinCenter(hist.GetNbinsX())#*x_stretch_factor  
    mchiMin = hist.GetYaxis().GetBinCenter(1)*y_stretch_factor
    mchiMax = hist.GetYaxis().GetBinCenter(hist.GetNbinsY())*y_stretch_factor
    
    myX = np.linspace(mgMin, mgMax,int((mgMax-mgMin)/binWidth+1))
    myY = np.linspace(mchiMin, mchiMax, int((mchiMax-mchiMin)/(binWidth)+1))
    myXI, myYI = np.meshgrid(myX,myY)

    #rbf = Rbf(x, y, z,function='gaussian', norm=euclidean_norm_numpy)
    rbf = Rbf(x, y, z,function='multiquadric', epsilon=epsilon,smooth=smooth) 
    myZI = rbf(myXI, myYI)
    
    #rbf_nosmooth = Rbf(x, y, z, function='multiquadric',epsilon=epsilon,smooth=100)
    rbf_nosmooth = Rbf(x, y, z, function='multiquadric',epsilon=epsilon,smooth=100) #usually 100
    otherY = array('d',[mchiMin])
    lineXI, lineYI = np.meshgrid(myX,otherY)
    lineZI = rbf_nosmooth(lineXI, lineYI)
     

    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            xLow = hist.GetXaxis().GetBinCenter(i)*x_stretch_factor
            yLow = hist.GetYaxis().GetBinCenter(j)*y_stretch_factor

            #continue
            #print('len(lineZI[j-1])', len(lineZI[j-1]))
            if j==1 and fixLSP0:
                hist.SetBinContent(i,j,rt.TMath.Exp(lineZI[j-1][i-1]))
                continue

            if refHist!=None:
                hist.SetBinContent(i,j,refHist.GetBinContent(i,j)*rt.TMath.Exp(myZI[j-1][i-1]))
            else:
                try:
                   hist.SetBinContent(i,j,rt.TMath.Exp(myZI[j-1][i-1]))
                except: 
                    pass
    return hist


def fix_hist_byhand(hist, model, box, clsType, gchipairs):
    return
    if 'Obs' in clsType:
        print ('actually gonna do something', clsType)
        for (mg,mchi) in gchipairs:            
            obs = hist.GetBinContent(hist.FindBin(mg,mchi))
            exp = xsecUL['Exp'].GetBinContent(xsecUL['Exp'].FindBin(mg,mchi))
            expPlus2 = xsecUL['ExpPlus2'].GetBinContent(xsecUL['ExpPlus2'].FindBin(mg,mchi))
            expPlus = xsecUL['ExpPlus'].GetBinContent(xsecUL['ExpPlus'].FindBin(mg,mchi))
            expMinus = xsecUL['ExpMinus'].GetBinContent(xsecUL['ExpMinus'].FindBin(mg,mchi))
            expMinus2 = xsecUL['ExpMinus2'].GetBinContent(xsecUL['ExpMinus2'].FindBin(mg,mchi))
            if hist.GetBinContent(hist.FindBin(mg,mchi))==0:
                if (mg,mchi) not in toFix:                
                    toFix.append((mg,mchi))
                    print ('grew on condition 1 to', (mg,mchi))
            elif obs<expPlus2 or obs>expMinus2:
                hist.SetBinContent(hist.FindBin(mg,mchi),exp)
                if (mg,mchi) not in toFix:
                    toFix.append((mg,mchi))
                    print ('grew on condition 2 to', (mg,mchi))
        print ('end of hand fixer', toFix)


def set_palette(name="default", ncontours=144):
    # For the canvas:
    rt.gStyle.SetCanvasBorderMode(0)
    rt.gStyle.SetCanvasColor(rt.kWhite)
    rt.gStyle.SetCanvasDefH(400) #Height of canvas
    rt.gStyle.SetCanvasDefW(500) #Width of canvas
    rt.gStyle.SetCanvasDefX(0)   #POsition on screen
    rt.gStyle.SetCanvasDefY(0)
        
    # For the Pad:
    rt.gStyle.SetPadBorderMode(0)
    # rt.gStyle.SetPadBorderSize(Width_t size = 1)
    rt.gStyle.SetPadColor(rt.kWhite)
    rt.gStyle.SetPadGridX(False)
    rt.gStyle.SetPadGridY(False)
    rt.gStyle.SetGridColor(0)
    rt.gStyle.SetGridStyle(3)
    rt.gStyle.SetGridWidth(1)
        
    # For the frame:
    rt.gStyle.SetFrameBorderMode(0)
    rt.gStyle.SetFrameBorderSize(1)
    rt.gStyle.SetFrameFillColor(0)
    rt.gStyle.SetFrameFillStyle(0)
    rt.gStyle.SetFrameLineColor(1)
    rt.gStyle.SetFrameLineStyle(1)
    rt.gStyle.SetFrameLineWidth(1)
    
    # set the paper & margin sizes
    rt.gStyle.SetPaperSize(20,26)
    rt.gStyle.SetPadTopMargin(0.085)
    rt.gStyle.SetPadRightMargin(0.15)
    rt.gStyle.SetPadBottomMargin(0.15)
    rt.gStyle.SetPadLeftMargin(0.17)
    
    # use large Times-Roman fonts
    rt.gStyle.SetTitleFont(42,"xyz")  # set the all 3 axes title font
    rt.gStyle.SetTitleFont(42," ")    # set the pad title font
    rt.gStyle.SetTitleSize(0.06,"xyz") # set the 3 axes title size
    rt.gStyle.SetTitleSize(0.06," ")   # set the pad title size
    rt.gStyle.SetLabelFont(42,"xyz")
    rt.gStyle.SetLabelSize(0.05,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(42)
    rt.gStyle.SetTextSize(0.08)
    rt.gStyle.SetStatFont(42)
    
    # use bold lines and markers
    rt.gStyle.SetMarkerStyle(8)
    #rt.gStyle.SetHistLineWidth(1.85)
    rt.gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes
    
    #..Get rid of X error bars
    rt.gStyle.SetErrorX(0.001)
    
    # do not display any of the standard histogram decorations
    rt.gStyle.SetOptTitle(1)
    rt.gStyle.SetOptStat(0)
    #rt.gStyle.SetOptFit(11111111)
    rt.gStyle.SetOptFit(0)
    
    # put tick marks on top and RHS of plots
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)
    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.95, 0.95, 0.65, 0.15]
        green = [1.00, 0.85, 0.7, 0.5, 0.3]
        blue  = [0.95, 0.6, 0.3, 0.45, 0.65]
    elif name == "chris":
        stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
        red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
        green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
        blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
    elif name == "blue":
        stops = [ 0.0, 0.5, 1.0]
        red =   [ 0.0, 1.0, 0.0]
        green = [ 0.0, 0.0, 0.0]
        blue =  [ 1.0, 0.0, 0.0]
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
        #from PlotsSMS/python/smsPlotXSEC.py
        stops = [0.00, 0.20, 0.70, 0.90, 1.00]
        red   = [0.00, 0.00, 1.00, 1.00, 1.00]
        green = [0.00, 1.00, 1.00, 0.30, 0.00]
        blue  = [1.00, 1.00, 0.00, 0.20, 0.00]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
    
    npoints = len(s)
    rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    rt.gStyle.SetNumberContours(ncontours)


if __name__ == '__main__':
    
    
    rt.gROOT.SetBatch()
    
    dirext = ""
    parser = OptionParser()
    parser.add_option('-b','--box',dest="box", default="DT",type="string",
                  help="box name")
#    parser.add_option('-m','--model',dest="model", default="T2btLL",type="string",
#                  help="signal model name")
    parser.add_option('-m','--model',dest="model", default="T1qqqqLL",type="string",
                  help="signal model name")
    parser.add_option('--toys',dest="doHybridNew",default=False,action='store_true',
                  help="for toys instead of asymptotic")
    parser.add_option('-e','--energy',dest="energy",type="int",default=13,
                  help="Energy (in TeV) to consider (Run 2: 13, HL: 14 or HE: 27 TeV)")
    parser.add_option('--xsec-file',dest="refXsecFile",default="2Dlimitplot/usefulthings/glu_xsecs_13TeV.txt",type="string",
                  help="Input directory")
    parser.add_option('--no-smooth', dest='noSmooth', action='store_true', 
                  help='Draw grid without interpolation')
    parser.add_option('-s',dest="signif", action="store_true",
                      default=False,    help="Plot significance instead of limit")
    parser.add_option('--blind', dest="blind", action="store_true",
                      default=False, help='Do not calculate the observed limit')
    
    (options,args) = parser.parse_args()

    print (options)
    
    box = options.box
    model = options.model
    directory = "limits2root/"+date+"/"+model+dirext+"/"
    
    
    
    refXsecFile = options.refXsecFile
    if "T2" in options.model: refXsecFile = refXsecFile.replace("gluino","stop")
    if options.energy != 13: refXsecFile = refXsecFile.replace("13",str(options.energy))
    doHybridNew = options.doHybridNew
                
    set_palette("rainbow",255)
    rt.gStyle.SetOptStat(0)
    rt.gROOT.ProcessLine(".L macros/swissCrossInterpolate.h+")
    rt.gSystem.Load("macros/swissCrossInterpolate_h.so")

    

    try:
        sms = sms_models[model]
    except KeyError:
        sys.exit("Model {} is not implemented!".format(model))
    mgMin = sms.mgMin
    mgMax = sms.mgMax
    mchiMin = sms.mchiMin
    
    mchiMax = sms.mchiMax
    diagonalOffset = sms.diagonalOffset
    if options.energy>13:
        if model == "T2tt":
            mgMax   = 2025 + DISP_OFFSET
            mchiMax =  850 + DISP_OFFSET
            if options.signif:
                mchiMax = 675 + DISP_OFFSET
        elif   model == "T1tttt":
            if options.energy == 14:
                mgMax   = 3025 + DISP_OFFSET
            elif options.energy == 27:
                mgMax   = 3525 + DISP_OFFSET
            mchiMax = 1725 + DISP_OFFSET
        elif model == "T5ttcc":
            if options.energy == 14:
                mgMax   = 3025 + DISP_OFFSET
            elif options.energy == 27:
                mgMax   = 3525 + DISP_OFFSET
            mchiMax = 1525 + DISP_OFFSET
    binWidth = sms.binWidth
    nRebins = sms.nRebins
    if not options.signif:
        xsecMin = sms.xsecMin
        xsecMax = sms.xsecMax
    else:
        xsecMin = 0
        xsecMax = 10
    smoothing = sms.smoothing
    fixLSP0 = sms.fixLSP0
    print('fixLSP0', fixLSP0)
    
    # Make a xsec tree first578
    
    haddOutputs = []
    gchipairs = []
    #for result in glob.glob(directory+'/combine/RazorBoost_'+box+'_'+model+'_*.log'):
    #    mg   = float(result.replace(".log","").split("_")[-2:][0])
    #    mchi = float(result.replace(".log","").split("_")[-2:][1])
    #    gchipairs.append((mg,mchi))
    #    haddOutputs.append("%s/%s_xsecUL_mg_%s_mchi_%s_%s.root" %(directory, model, mg, mchi, box))
    infiles = directory+"/"+model+"_xsecUL_*_*_*_*_"+box+".root"
    print ('infiles', infiles)
    ###maybe no need to change this? SBif options.signif: infiles = directory+"/"+model+"_signif_mg_*_mchi_*.?_"+box+".root"
    for result in glob.glob(infiles):
        haddOutputs.append(result)
        print ('result', result)
        mg   = float(result.replace("_"+box+".root","").split("_")[-3])
        mchi = float(result.replace("_"+box+".root","").split("_")[-1])
        gchipairs.append((mg,mchi))
    print ('gchipairs', gchipairs)

    if options.signif:
        print (directory+"/"+model+"_signif_*_"+box+".root")
        haddout = "%s/%s_signif_%s.root %s"%(directory+"/results",model,box," ".join(haddOutputs))
    else:
        print ('path and thingies', directory+'/results')
        print ('haddOutputs', "%s/%s_xsecUL_Asymptotic_%s.root"%(directory+"/results",model,box),  haddOutputs)
        haddout = "%s/%s_xsecUL_Asymptotic_%s.root %s"%(directory+"/results",model,box," ".join(haddOutputs))
        print ('going to do a hadd out', haddout)
    if not os.path.exists(directory+"/results"): subprocess.call(["mkdir", "-p", directory+"/results"])
    
    os.system("hadd -f "+haddout)
    #os.system("rm %s"%(" ".join(haddOutputs)))

    if options.signif and False: ##sam adding the and False
        xsecFile = rt.TFile.Open("%s/%s_signif_%s.root"%(directory+"/results",model,box))
        print ("%s/%s_signif_%s.root"%(directory+"/results",model,box))
        xsecTree = xsecFile.Get("signifTree")
    else:
        print ('xsec file:', "%s/%s_xsecUL_Asymptotic_%s.root"%(directory+"/results",model,box))
        xsecFile = rt.TFile.Open("%s/%s_xsecUL_Asymptotic_%s.root"%(directory+"/results",model,box))
        xsecTree = xsecFile.Get("xsecTree")
        print ('just grabbed', xsecTree, 'from', "%s/%s_xsecUL_Asymptotic_%s.root"%(directory+"/results",model,box))
        xsecGluino =  rt.TH2D("xsecGluino","xsecGluino",int((mgMax-mgMin)/(binWidth/x_stretch_factor)),mgMin, mgMax,int((mchiMax-mchiMin)/(binWidth/y_stretch_factor)), mchiMin, mchiMax)
        xsecGluinoPlus =  rt.TH2D("xsecGluinoPlus","xsecGluinoPlus",int((mgMax-mgMin)/(binWidth/x_stretch_factor)),mgMin, mgMax,int((mchiMax-mchiMin)/(binWidth/y_stretch_factor)), mchiMin, mchiMax)
        xsecGluinoMinus =  rt.TH2D("xsecGluinoMinus","xsecGluinoMinus",int((mgMax-mgMin)/(binWidth/x_stretch_factor)),mgMin, mgMax,int((mchiMax-mchiMin)/(binWidth/y_stretch_factor)), mchiMin, mchiMax)

    if options.signif:
        clsTypes = ["Signif"]
        titleMap = {"Signif":"Significance"}
        whichCLsVar = {"Signif":"signif_%s"%(box)}
        
        clsTypes = ["Significance"]
        titleMap = {"Significance":"Significance"}
        whichCLsVar = {"Significance":"Significance"}        
    else:
        if options.blind:
            clsTypes = ["Exp","ExpMinus","ExpMinus2","ExpPlus","ExpPlus2"]
            titleMap = {"Exp":"Expected","ExpMinus":"Expected-1#sigma","ExpPlus":"Expected+1#sigma",
                        "ExpMinus2":"Expected-2#sigma","ExpPlus2":"Expected+2#sigma"}
            whichCLsVar = {"Exp":"xsecULExp_%s"%(box),"ExpPlus":"xsecULExpMinus_%s"%(box),"ExpMinus":"xsecULExpPlus_%s"%(box),
                           "ExpPlus2":"xsecULExpMinus2_%s"%(box),"ExpMinus2":"xsecULExpPlus2_%s"%(box)}            
        else:
            clsTypes = ["Exp","ExpMinus","ExpMinus2","ExpPlus","ExpPlus2","Obs","ObsMinus","ObsPlus"]
            titleMap = {"Exp":"Expected","ExpMinus":"Expected-1#sigma","ExpPlus":"Expected+1#sigma",
                        "ExpMinus2":"Expected-2#sigma","ExpPlus2":"Expected+2#sigma",
                        "ObsMinus":"Observed-1#sigma", "ObsPlus":"Observed+1#sigma","Obs":"Observed"}
            whichCLsVar = {"Obs":"xsecULObs_%s"%(box),"ObsPlus":"xsecULObs_%s"%(box),"ObsMinus":"xsecULObs_%s"%(box),
                           "Exp":"xsecULExp_%s"%(box),"ExpPlus":"xsecULExpMinus_%s"%(box),"ExpMinus":"xsecULExpPlus_%s"%(box),
                           "ExpPlus2":"xsecULExpMinus2_%s"%(box),"ExpMinus2":"xsecULExpPlus2_%s"%(box)}
    
    smooth = {}
    for clsType in clsTypes:
        smooth[clsType] = smoothing
                       
    xsecUL = {}
    logXsecUL = {}
    rebinXsecUL = {}
    subXsecUL = {}
    contourFinal = {}

    subboxes = box.split("_")
    
    if not options.signif:
        if model=='PureHiggsino': fxsec = fxsecs['PureHiggsino']
        if 'Wino' in model: fxsec = fxsecs['PureWino']
        for i in range(1,xsecGluino.GetNbinsX()+1):
            xLow = xsecGluino.GetXaxis().GetBinCenter(i)
            for j in range(1,xsecGluino.GetNbinsY()+1):
                yLow = xsecGluino.GetYaxis().GetBinCenter(j)
                xsecVal, xsecValup, xsecValdown = 0,0,0
                if xLow<150:
                    for comp in fxsec['100to150']: xsecVal         += 0.001*comp.Eval(max(100,xLow))
                    for comp in fxsec['100to150_up']: xsecValup    += 0.001*comp.Eval(max(100,xLow))
                    for comp in fxsec['100to150_dn']: xsecValdown  += 0.001*comp.Eval(max(100,xLow))
                elif xLow>=150 and xLow<200: 
                    for comp in fxsec['150to200']: xsecVal         += 0.001*comp.Eval(max(150,xLow))
                    for comp in fxsec['150to200_up']: xsecValup    += 0.001*comp.Eval(max(150,xLow))
                    for comp in fxsec['150to200_dn']: xsecValdown  += 0.001*comp.Eval(max(150,xLow))
                elif xLow>=200 and xLow<300: 
                    for comp in fxsec['200to300']: xsecVal         += 0.001*comp.Eval(max(200,xLow))
                    for comp in fxsec['200to300_up']: xsecValup    += 0.001*comp.Eval(max(200,xLow))
                    for comp in fxsec['200to300_dn']: xsecValdown  += 0.001*comp.Eval(max(200,xLow))
                elif xLow>=300 and xLow<400: 
                    for comp in fxsec['300to400']: xsecVal         += 0.001*comp.Eval(max(300,xLow))
                    for comp in fxsec['300to400_up']: xsecValup    += 0.001*comp.Eval(max(300,xLow))
                    for comp in fxsec['300to400_dn']: xsecValdown  += 0.001*comp.Eval(max(300,xLow))
                elif xLow>=400 and xLow<600: 
                    for comp in fxsec['400to600']: xsecVal         += 0.001*comp.Eval(max(400,xLow))
                    for comp in fxsec['400to600_up']: xsecValup    += 0.001*comp.Eval(max(400,xLow))
                    for comp in fxsec['400to600_dn']: xsecValdown  += 0.001*comp.Eval(max(400,xLow))
                elif xLow>=600 and xLow<800: 
                    for comp in fxsec['600to800']: xsecVal         += 0.001*comp.Eval(max(600,xLow))
                    for comp in fxsec['600to800_up']: xsecValup    += 0.001*comp.Eval(max(600,xLow))
                    for comp in fxsec['600to800_dn']: xsecValdown  += 0.001*comp.Eval(max(600,xLow))
                elif xLow>=800 and xLow<1000: 
                    for comp in fxsec['800to1000']: xsecVal         += 0.001*comp.Eval(max(800,xLow))
                    for comp in fxsec['800to1000_up']: xsecValup    += 0.001*comp.Eval(max(800,xLow))
                    for comp in fxsec['800to1000_dn']: xsecValdown  += 0.001*comp.Eval(max(800,xLow))
                elif xLow>=1000 and xLow<1200:
                    for comp in fxsec['1000to1200']: xsecVal        += 0.001*comp.Eval(max(1000,xLow))
                    for comp in fxsec['1000to1200_up']: xsecValup   += 0.001*comp.Eval(max(1000,xLow))
                    for comp in fxsec['1000to1200_dn']: xsecValdown += 0.001*comp.Eval(max(1000,xLow))                                                                                                 
                elif xLow>=1200:
                    for comp in fxsec['1200to1500']: xsecVal        += 0.001*comp.Eval(max(1200,xLow))
                    for comp in fxsec['1200to1500_up']: xsecValup   += 0.001*comp.Eval(max(1200,xLow))
                    for comp in fxsec['1200to1500_dn']: xsecValdown += 0.001*comp.Eval(max(1200,xLow))
                #xsecErr = .05*xsecVal                                    
                xsecGluino.SetBinContent(i,j,xsecVal)
                xsecGluinoPlus.SetBinContent(i,j,xsecValup)
                xsecGluinoMinus.SetBinContent(i,j,xsecValdown)

        c = rt.TCanvas('c', 'c', 600, 600)
        xsecGluino.Draw('colz text')
        c.SaveAs('xsecGluino.pdf')
        
        # now rebin xsecGluino the correct number of times
#        for i in range(0,nRebins):
#            xsecGluino = rt.swissCrossRebin(xsecGluino,"NE")
#            xsecGluinoPlus = rt.swissCrossRebin(xsecGluinoPlus,"NE")
#            xsecGluinoMinus = rt.swissCrossRebin(xsecGluinoMinus,"NE")


    xyPairExp = {}
    
    for clsType in clsTypes:
        print('gonna make a new thing', "xsecUL_%s_%s"%(model,clsType))
        xsecUL[clsType] = rt.TH2D("xsecUL_%s_%s"%(model,clsType),"xsecUL_%s_%s"%(model,clsType),int((mgMax-mgMin)/(binWidth/x_stretch_factor)),mgMin, mgMax,int((mchiMax-mchiMin)/(binWidth/y_stretch_factor)), mchiMin, mchiMax)
        print('made it', "xsecUL_%s_%s"%(model,clsType))
        xsecTree.Show(0)
        xsecTree.Project("xsecUL_%s_%s"%(model,clsType),"dm:mchipm",whichCLsVar[clsType])
        print('projected it', "xsecUL_%s_%s"%(model,clsType))
        if not options.signif:     ##could move this to after the interpolation       
            #fix_hist_byhand(xsecUL[clsType],model,box,clsType, gchipairs)
            a = 2
        
        print ("INFO: doing interpolation for %s"%(clsType))
        for i in range(1,xsecUL[clsType].GetNbinsX()+1):
            xLow = xsecUL[clsType].GetXaxis().GetBinCenter(i)
            for j in range(1,xsecUL[clsType].GetNbinsY()+1):
                yLow = xsecUL[clsType].GetYaxis().GetBinCenter(j)
                if xsecUL[clsType].GetBinContent(i, j) != 0:
                    continue
                #if xLow >= yLow+diagonalOffset and xLow <= (mgMax-25)-binWidth/2:
                #xsecVal = thyXsec[int(xLow),int(yLow)]
                #xsecErr =  thyXsecErr[int(xLow),int(yLow)]
                ###Val = xsecUL[clsType].Interpolate(xLow, yLow)
                #xsecUL[clsType].SetBinContent(i,j,Val)
                if box=='DT':
                    if yLow>1: xsecUL[clsType].SetBinContent(i,j,999)

        
        # do swiss cross average in real domain
        #rebinXsecUL[clsType] = rt.swissCrossInterpolate(xsecUL[clsType],"NE")
        #rebinXsecUL[clsType] = xsecUL[clsType].Interpolate(1329, 1231)

        print ('xbin', xsecUL[clsType].GetXaxis().GetNbins(), 'ybin', xsecUL[clsType].GetYaxis().GetNbins() )
        # do scipy multi-quadratic interpolation in log domain
        #rebinXsecUL[clsType] = interpolate2D(rebinXsecUL[clsType],epsilon=5,smooth=smooth[clsType],diagonalOffset=diagonalOffset,fixLSP0=fixLSP0)
        
        rebinXsecUL[clsType] = interpolate2D(xsecUL[clsType],epsilon=5,smooth=smooth[clsType],diagonalOffset=diagonalOffset,fixLSP0=fixLSP0)
        #rebinXsecUL[clsType] = rt.swissCrossInterpolate(xsecUL[clsType],"NE")
        c = rt.TCanvas('c', 'c', 600, 600)
        xsecUL[clsType].Draw('colz')

        #c.Update()
        #pause()
        c.SaveAs('c_'+clsType+'.pdf')

        # only for display purposes of underlying heat map: do swiss cross average then scipy interpolation 
        if not options.noSmooth:
            
            xsecUL[clsType] = rt.swissCrossInterpolate(xsecUL[clsType],"NE")
            print ('here we are', xsecUL)
            #xsecUL[clsType] = interpolate2D(xsecUL[clsType], epsilon=5,smooth=smooth[clsType],diagonalOffset=diagonalOffset,fixLSP0=fixLSP0)
            print ('post interpolate')

        # fix axes
        xsecUL[clsType].GetXaxis().SetRangeUser(xsecUL[clsType].GetXaxis().GetBinCenter(1),xsecUL[clsType].GetXaxis().GetBinCenter(xsecUL[clsType].GetNbinsX()))
        xsecUL[clsType].GetYaxis().SetRangeUser(xsecUL[clsType].GetYaxis().GetBinCenter(1),xsecUL[clsType].GetYaxis().GetBinCenter(xsecUL[clsType].GetNbinsY()))
        
    c = rt.TCanvas("c","c",500,500)
    
    for clsType in clsTypes:
        xsecUL[clsType].SetName("xsecUL_%s_%s_%s"%(clsType,model,box))
        xsecUL[clsType].SetTitle("%s %s, %s #sigma #times Branching Fraction"%(model,box.replace("_","+"),titleMap[clsType]))
        xsecUL[clsType].SetTitleOffset(1.5)
        xsecUL[clsType].SetXTitle("m_{#tilde{#chi}^{#pm}_{1}} [GeV]")
        xsecUL[clsType].GetXaxis().SetTitleOffset(0.95)
        xsecUL[clsType].SetYTitle("#Delta m(#tilde{#chi}^{#pm}_{1}, #tilde{#chi}^{0}_{1})[GeV]")
        xsecUL[clsType].GetYaxis().SetTitleOffset(1.25)

        subXsecUL[clsType] = rebinXsecUL[clsType].Clone()
        
        fileOut = rt.TFile.Open("test.root", "update")
        subXsecUL[clsType].Write(subXsecUL[clsType].GetName()+"_beforesub")
        #xsecGluino.Write(xsecGluino.GetName()+"_sub")
        # subtract the predicted xsec
        if not options.signif:
            if clsType=="ObsMinus":
                subXsecUL[clsType].Add(xsecGluinoMinus,-1)
            elif clsType=="ObsPlus":
                subXsecUL[clsType].Add(xsecGluinoPlus,-1)
            else:
                subXsecUL[clsType].Add(xsecGluino,-1)
        subXsecUL[clsType].Write(subXsecUL[clsType].GetName()+"_aftersub")
        fileOut.Close()

        if options.signif:
            contours = array('d',[5.0])
            # Force connect points above the plot range
            biny = subXsecUL[clsType].GetYaxis().FindBin(mchiMax-DISP_OFFSET-(binWidth/y_stretch_factor))
            for binx in range(1, subXsecUL[clsType].GetNbinsX()+1):
                if subXsecUL[clsType].GetBinContent(binx,biny)>5.0:
                    subXsecUL[clsType].SetBinContent(binx,biny+1,4.999)
            binx = subXsecUL[clsType].GetXaxis().FindBin(mgMax-DISP_OFFSET-(binWidth/x_stretch_factor))
            for biny in range(1, subXsecUL[clsType].GetNbinsY()+1):
                if subXsecUL[clsType].GetBinContent(binx,biny)>5.0:
                    subXsecUL[clsType].SetBinContent(binx+1,biny,4.999)
        else:
            contours = array('d',[0.0])
            # Force zero values outside the plot range, so curves don't end up splitted
            for binx in range(1, subXsecUL[clsType].GetNbinsX()+1):
                subXsecUL[clsType].SetBinContent(binx,subXsecUL[clsType].GetNbinsY(),0)
        subXsecUL[clsType].SetContour(1,contours)

        print ('xsecMin, xsecMax: ', xsecMin, xsecMax)
        xsecUL[clsType].SetMinimum(xsecMin)
        xsecUL[clsType].SetMaximum(xsecMax)
        rebinXsecUL[clsType].SetMinimum(xsecMin)
        rebinXsecUL[clsType].SetMaximum(xsecMax)
        print ('A')
        if options.signif:
            subXsecUL[clsType].SetMaximum(6.)
            subXsecUL[clsType].SetMinimum(4.)
        else:
            subXsecUL[clsType].SetMaximum(1.)
            subXsecUL[clsType].SetMinimum(-1.)
        print ('B')
        c.SetLogz(0)
        print ('B1')    
        print(subXsecUL[clsType], subXsecUL[clsType].GetEntries(), subXsecUL[clsType].Integral())   
        subXsecUL[clsType].Draw("CONT Z LIST")
        print ('B2')        
        c.Update()
        print ('B3')
        conts = rt.gROOT.GetListOfSpecials().FindObject("contours")
        print ('B4')
        xsecUL[clsType].Draw("CONTZ")
        print ('C')
        contour0 = conts.At(0)
        curv = contour0.First()
        finalcurv = rt.TGraph(1)
        try:
            curv.SetLineWidth(3)
            curv.SetLineColor(rt.kBlack)
            curv.Draw("lsame")
            finalcurv = curv.Clone()
            maxN = curv.GetN()
        except AttributeError:
            print ("ERROR: no curve drawn for box=%s, clsType=%s -- no limit "%(box, clsType))

        for i in range(1, contour0.GetSize()):
            curv = contour0.After(curv)
            curv.SetLineWidth(3)
            curv.SetLineColor(rt.kBlack)
            curv.Draw("lsame")
            if curv.GetN()>maxN:
                maxN = curv.GetN()
                finalcurv = curv.Clone()

        contourFinal[clsType] = finalcurv
        contourFinal[clsType].SetName("%s_%s_%s"%(clsType,model,box))

        if not options.signif: c.SetLogz(1)
        c.Print("%s/%s_INTERP_%s_%s.png"%(directory+"/results",model,box,clsType))

    if options.signif:
        outFile = rt.TFile.Open("%s/%s_%s_signif.root"%(directory+"/results",model,box),"recreate")
    else:
        outFile = rt.TFile.Open("%s/%s_%s_results.root"%(directory+"/results",model,box),"recreate")
    for clsType in clsTypes:
        contourFinal[clsType].Write()
        print ('writing ', xsecUL[clsType].GetName(), xsecUL[clsType].GetMinimum(), xsecUL[clsType].GetMaximum())
        xsecUL[clsType].Write()

    if not options.signif:
        smoothOutFile = rt.TFile.Open("%s/%s_smoothXsecUL_%s.root"%(directory+"/results",model,box), "recreate")
        
        smoothXsecTree = rt.TTree("smoothXsecTree", "smoothXsecTree")
        myStructCmd = "struct MyStruct2{Double_t mg;Double_t mchi;Double_t x;Double_t y;"
        ixsecUL = 0
        if options.blind:
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+0)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+1)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+2)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+3)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+4)
            ixsecUL+=5
        else:
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+0)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+1)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+2)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+3)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+4)
            myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+5)            
            ixsecUL+=6
        myStructCmd += "}"
        rt.gROOT.ProcessLine(myStructCmd)
        from ROOT import MyStruct2
        
        s = MyStruct2()
        smoothXsecTree.Branch("mchi", rt.AddressOf(s,"mg"),'mg/D')
        smoothXsecTree.Branch("dm", rt.AddressOf(s,"mchi"),'mchi/D')
        smoothXsecTree.Branch("x", rt.AddressOf(s,"x"),'x/D')
        smoothXsecTree.Branch("y", rt.AddressOf(s,"y"),'y/D')
        if 'T1x' in model:
            s.x = float(model[model.find('x')+1:model.find('y')].replace('p','.'))
            s.y = float(model[model.find('y')+1:].replace('p','.'))
        elif model == 'T1bbbb':
            s.x = 1
            s.y = 0
        elif model == 'T1tttt':
            s.x = 0
            s.y = 1
        else:
            s.x = -1
            s.y = -1
        
        
        ixsecUL = 0
        if options.blind:
            smoothXsecTree.Branch("xsecULExpPlus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL)),'xsecUL%i/D'%(ixsecUL))
            smoothXsecTree.Branch("xsecULExpPlus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+1)),'xsecUL%i/D'%(ixsecUL+1))
            smoothXsecTree.Branch("xsecULExp_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+2)),'xsecUL%i/D'%(ixsecUL+2))
            smoothXsecTree.Branch("xsecULExpMinus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+3)),'xsecUL%i/D'%(ixsecUL+3))
            smoothXsecTree.Branch("xsecULExpMinus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+4)),'xsecUL%i/D'%(ixsecUL+4))
        else:
            smoothXsecTree.Branch("xsecULObs_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+0)),'xsecUL%i/D'%(ixsecUL+0))
            smoothXsecTree.Branch("xsecULExpPlus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+1)),'xsecUL%i/D'%(ixsecUL+1))
            smoothXsecTree.Branch("xsecULExpPlus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+2)),'xsecUL%i/D'%(ixsecUL+2))
            smoothXsecTree.Branch("xsecULExp_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+3)),'xsecUL%i/D'%(ixsecUL+3))
            smoothXsecTree.Branch("xsecULExpMinus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+4)),'xsecUL%i/D'%(ixsecUL+4))
            smoothXsecTree.Branch("xsecULExhinoxsec_100to150pMinus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+5)),'xsecUL%i/D'%(ixsecUL+5))

        for mg in np.linspace(mgMin-(binWidth)/2,mgMax+(binWidth)-(binWidth/2),binWidth):
            for mchi in np.linspace(mchiMin-(binWidth/y_stretch_factor)/2,mchiMax+(binWidth/y_stretch_factor)-(binWidth/2/y_stretch_factor),binWidth/y_stretch_factor):
                s.mg = mg
                s.mchi = mchi

                if not options.blind:
                    xsecULObs = xsecUL["Obs"].GetBinContent(xsecUL["Obs"].FindBin(mg,mchi))
                xsecULExp = xsecUL["Exp"].GetBinContent(xsecUL["Exp"].FindBin(mg,mchi))
                xsecULExpPlus = xsecUL["ExpMinus"].GetBinContent(xsecUL["ExpMinus"].FindBin(mg,mchi))
                xsecULExpMinus = xsecUL["ExpPlus"].GetBinContent(xsecUL["ExpPlus"].FindBin(mg,mchi))
                xsecULExpPlus2 = xsecUL["ExpMinus2"].GetBinContent(xsecUL["ExpMinus2"].FindBin(mg,mchi))
                xsecULExpMinus2 = xsecUL["ExpPlus2"].GetBinContent(xsecUL["ExpPlus2"].FindBin(mg,mchi))

                if options.blind:
                    exec ('s.xsecUL%i = xsecULExpPlus2'%(ixsecUL+0))
                    exec ('s.xsecUL%i = xsecULExpPlus'%(ixsecUL+1))
                    exec ('s.xsecUL%i = xsecULExp'%(ixsecUL+2))
                    exec ('s.xsecUL%i = xsecULExpMinus'%(ixsecUL+3))
                    exec ('s.xsecUL%i = xsecULExpMinus2'%(ixsecUL+4))
                else:
                    exec ('s.xsecUL%i = xsecULObs'%(ixsecUL+0))
                    exec ('s.xsecUL%i = xsecULExpPlus2'%(ixsecUL+1))
                    exec ('s.xsecUL%i = xsecULExpPlus'%(ixsecUL+2))
                    exec ('s.xsecUL%i = xsecULExp'%(ixsecUL+3))
                    exec ('s.xsecUL%i = xsecULExpMinus'%(ixsecUL+4))
                    exec ('s.xsecUL%i = xsecULExpMinus2'%(ixsecUL+5))
        
                if xsecULExp > 0.:
                    smoothXsecTree.Fill()
        
        smoothOutFile.cd()
        smoothXsecTree.Write()
        smoothOutFile.Close()

    print ('just created', outFile.GetName())
    outFile.Close()
    print (len(gchipairs), "total points")
    print (len(toFix), "points to fix")
    print (toFix)
