# Agilent_E4980A_Controller
Agilent E4980A Precision LCR Meter controller by PyVISA.  

### Requirement ###
+ Python 2.x
+ NumPy
+ PyVISA

### Usage ###
Run the program with output file name as an argument  
    ``python impedance.py output``
then you will get ``output.csv``. Customize setups accordingly. Commands can be found at [Agilent E4980A/AL Precision LCR Meter Users Guide](https://literature.cdn.keysight.com/litweb/pdf/E4980-90210.pdf?id=789356).  


### What this does ###
1. Setups connection to Agilent E4980A Precision LCR Meter by USB (Check l. 55 for USB address setting)
2. Setups sweep parameters in ll. 61-83
3. Performs sweep by BUS trigger (timeout for sweep is customized by ``sleepdelay``)
4. Saves frequency, impedance (ohm), and phase (deg).
5. Sets back trigger to internal mode  

-----
# Updates  
2017 Nov 21 Version 1.01 bug fix for saving data
2017 Nov 20 Version 1.00  
