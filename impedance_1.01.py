# -*- coding: utf-8 -*-

import visa
import numpy as np
import sys
from datetime import datetime as dt
import pytz
from time import sleep
import glob

# sweep parameters
base = 20.
sweepstart = 1. # frequency sweep from base**sweepstart
sweepstop = 5.6 # frequency sweep end at base**sweepstop
numberOfPoints = 101
fillMode = "log" # parameter steps. linear or log
amp = 0.1 # voltage amplitude
averaging = 1 # number of averaging
bias = 0 # dc bias

# timeout for sweep(s) in second
timeout = 300

def checkSaveFileName(basefname, average):
    i = 2
    fname = "%s-ave.csv"%(basefname) if average else "%s.csv"%(basefname)
    while len(glob.glob(fname)) > 0:
        fname = "%s-ave-%g.csv"%(basefname, i) if average else "%s-%g.csv"%(basefname, i)
        i = i + 1
    if i != 2:
        print "saved file %s"%fname
    return fname

def main():
    if len(sys.argv) < 2:
        print 'input file name to save, "ave" to average'
        return 0
    else:
        basefname = sys.argv[1]
        if len(sys.argv) == 3:
            if sys.argv[2] == "ave":
                average = True
                avfc = 10
                pavfc = 10
        else:
            avfc = 1
            pavfc = 1
            average = False

    # check output file duplicate
    fname = checkSaveFileName(basefname, average)

    # open instrument
    rm = visa.ResourceManager("C:/Windows/System32/visa64.dll")
    pia = rm.open_resource('USB0::0x0957::0x0909::MY46204132::0::INSTR')

    pia.write(":DISP:CCL") # clear error message
    pia.write(":TRIG:SOUR BUS") # trigger mode BUS mode from USB
    pia.write("*CLS") # clear messages

    # setup measurement parameters
    pia.write(":FUNC:IMP:TYPE ZTD") # sets maeasurement function to Z-thd
    pia.write(":FUNC:IMP:RANG:AUTO ON") # automatic measurement range

    # make sweep parameter list
    if fillMode == "log":
        sweepList = np.logspace(sweepstart, sweepstop, num=numberOfPoints)
    else:
        sweepList = np.linspace(sweepstart, sweepstop, num=numberOfPoints)
    sweepListString = ",".join(map(lambda x: "%.8e"%x, sweepList))
    pia.write(":LIST:FREQ %s"%sweepListString) # sweep parameter to frequency
    pia.write(":LIST:MODE SEQ") # sweep mode list, sequential
    pia.write(":DISP:PAGE LIST") # shows list display

    pia.write(":APER MED, %g"%(averaging)) # measurement time medium

    pia.write(":VOLT %g"%amp) # oscillator mode to votage 0.1 V
    pia.write(":BIAS:STAT OFF")# DC bias off :BIAS:STAT?

    pia.write(":SYST:BEEP:STAT ON") # enables beep
    pia.write(":COMP:BEEP PASS") # beeps when measurement passes: default fail

    pia.write(":STAT:OPER:ENAB 0")
    pia.write(":ABOR;:INIT")

    pia.write(":TRIG") # trigger measurement

    # wait until sweep finishes by 1 sec.
    timer = 0
    sw = [0]
    while sw == [0] and timer < timeout:
        timer += 1
        # read if operation is running
        try:
            sw = pia.query_ascii_values('*OPC?') # 1 when all operation is finished
        # if error happens, wait 1 sec
        except:
            sleep(1)

    # if timeout, return error
    if timer >= timeout:
        print "sweep timeout"
        return 0

    sweepParamList = np.array(pia.query_ascii_values(":LIST:FREQ?")) # returns parameter list query
    swp = np.array([[elm] for elm in sweepParamList]) # reshape parameter list
    result = np.array(pia.query_ascii_values('FETC?')) # result
    res2 = np.reshape(result, (len(result)/4,4)) # reshape result

    # save data
    head = """data file made from Agilent E4980A Precision LCR Meter by impedance.py
URL: https://github.com/ikuehirata/Agilent_E4980A_Controller

Data file created at %s UTC
Measurement mode = %s
Osc Level = %s
DC Bias State = %s
DC Bias Level = %s
Averaging = %s
Sweep Mode = %s
Freqency\tZ\tphi""" % \
    (dt.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
     pia.query(':FUNC:IMP?').strip("\n"),
     pia.query(':VOLT?').strip('\n'),
     pia.query(':BIAS:STAT?').strip('\n'),
     pia.query(':BIAS:VOLT?').strip('\n'),
     pia.query(':APER?').strip('\n'),
     pia.query(":LIST:MODE?").strip('\n'))
    np.savetxt(fname, np.hstack((swp, res2)), delimiter='\t', header=head)
    #print np.hstack((sweepParamList, result))

    # after measurement, change display format
    pia.write(":TRIG:SOUR INT") # change to internal (continuous) trigger
    pia.write(":LIST:FREQ 1000")
    pia.write(":DISP:PAGE MEAS") # shows measurement display
    pia.write(":FUNC:IMP CPD") # shows C-PD

try:
    main()
except:
    import traceback
    print traceback.print_exc()
