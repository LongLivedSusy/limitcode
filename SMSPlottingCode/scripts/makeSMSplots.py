import sys, os
from inputFile import *
from smsPlotXSEC import *
from smsPlotCONT import *
from smsPlotBrazil import *

#os.system('rm plots/*')

if __name__ == '__main__':
    rt.gROOT.SetBatch()

    # read input arguments
    filename = sys.argv[1]
    modelname = sys.argv[1].split("/")[-1].split("_")[0]
    analysisLabel = sys.argv[1].split("/")[-1].split("_")[1]
    outputname = sys.argv[2]

    # read the config file
    print ('attempting to open this great file', filename)
    fileIN = inputFile(filename)
    fileIN.HISTOGRAM['histogram'].Print('v')
    fileIN.HISTOGRAM['histogram'].LabelsDeflate('X')
    fileIN.HISTOGRAM['histogram'].LabelsDeflate('X')
    fileIN.HISTOGRAM['histogram'].LabelsDeflate('X')
    fileIN.HISTOGRAM['histogram'].LabelsDeflate('X')
    fileIN.HISTOGRAM['histogram'].LabelsDeflate('X')        
    # classic temperature histogram
    xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.EXPECTED2, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, fileIN.BOXES, "")
    xsecPlot.Draw()
    if 'purehiggsino' in modelname.lower():
        fsatoshi = rt.TFile('SatoshiDmChipmChi10.root')
        dmrad_chipm_chi10 = fsatoshi.Get('dmrad_chipm_chi10')
        dmrad_chipm_chi10.SetLineColor(rt.kGreen+1)
        dmrad_chipm_chi10.Draw('same')
    if 'purewino' in modelname.lower():       
        def delta_m_over_mev(m_chi):
                    t = m_chi[0]  # since t = m_chi / GeV, and GeV = 1 for this purpose
                    numerator = 21.8641 + 8.68343*t + 0.0568066*pow(t,2)
                    denominator = 1 + 0.0530366*t + 0.000345101*pow(t,2)
                    return 0.001* numerator / denominator
        dmrad_chipm_chi10_wino = rt.TF1("func", delta_m_over_mev, 100, 1100, 0)
        dmrad_chipm_chi10_wino.SetLineColor(rt.kGreen+1)
        dmrad_chipm_chi10_wino.Draw("same")
        

        
    xsecPlot.Save("plots/%sXSEC" %outputname)

    os.system('python scripts/whiphtml.py "plots/*.png"')
    print ('cp plots/* /afs/desy.de/user/b/beinsam/www/SoftDilepton/HiggsinoMaskBins3')

    # only lines
    #contPlot = smsPlotCONT(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.EXPECTED2, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, fileIN.BOXES, "")
    #contPlot.Draw()
    #contPlot.Save("%sCONT" %outputname)

    # brazilian flag (show only 1 sigma)
    #brazilPlot = smsPlotBrazil(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.EXPECTED2, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, fileIN.BOXES, "")
    #brazilPlot.Draw()
    #brazilPlot.Save("%sBAND" %outputname)
