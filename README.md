# limitcode
limit code used for the disappearing track analysis

Steps:
1. prepinput.py : Prepares the input for limits.  

2. runlimits.py : Runs limits, but also prepares the output in a way which would be used for
the plots. This could have been done in 2 steps of course, first run the limit, then convert
the limit tree into another tree that is used in contour calculation.  It’s this way because
I had to put together the script quickly.  Example outputs are in limits2root directory.

3. Get2DContour.py : This makes all the 2D histograms and contour graphs needed for making
the limit plot.  However the swisscross interpolation does not work with a local
installation of root (I heard maybe it is available in CMSSW, but I think it quite
unlikely).  I turned it off and am using a standard interpolation.  This might be causing
unknown issues.

4. SMSPlottingCode: The limit plotting code inherited from Razor (which in turn was 
inherited from elsewhere).
In that directory, run, e.g.:
python scripts/makeSMSplots.py config/DT/T1qqqqLL_DT_exp.cfg T1qqqqLL

