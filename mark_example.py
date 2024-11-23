import os
import sys
from SourceFiles.teproteus import TEProteusAdmin as TepAdmin
import matplotlib.pyplot as plt
import numpy as np

# connect and initialize
admin = TepAdmin() #required to control PXI module
sid = 8 #PXI slot WDS found
inst = admin.open_instrument(slot_id=sid)
resp = inst.send_scpi_query("*IDN?")
print('connected to: ' + resp) # Print *IDN
inst.send_scpi_cmd('*CLS; *RST')
# Set rates for DAC
sampleRateDAC = 0.5E9
# Set CF
ncoFreq = 10E6
# wavefore parameters
max_dac = 65535  # Max Dac
half_dac = max_dac / 2  # DC Level
data_type = np.uint16  # DAC data type
onLen = 32 * 20  # Pulse on time multiple of 32 or 28ns
segTime = onLen / (sampleRateDAC)
print('On time')
print(segTime)
dacWaveOn_I = np.ones(onLen)
dacWaveOn_I = dacWaveOn_I * max_dac
dacWaveOn_I = dacWaveOn_I.astype(data_type)
dacWaveOn_Q = dacWaveOn_I/2
# reshapes for IQIQIQIQIQ....
arr_tuple = (dacWaveOn_I, dacWaveOn_Q)
dacWaveOn_IQ = np.vstack(arr_tuple).reshape((-1,), order='F')
plt.plot(dacWaveOn_IQ)
# AWG channel
ch = 1  # everythinf after relates to CH 1
cmd = ':INST:CHAN {0}'.format(ch)
# inst.send_scpi_cmd(cmd)
# cmd = ':FREQ:RAST {0}'.format(2.5E9)  # force to max 16 bit DAC
# inst.send_scpi_cmd(cmd)
# inst.send_scpi_cmd(':INIT:CONT ON')
################################################################################
# Define segment memory
segnum = 1
cmd = ':TRAC:DEF {0}, {1}'.format(segnum, len(dacWaveOn_IQ))
inst.send_scpi_cmd(cmd)
# Select the segment
cmd = ':TRAC:SEL {0}'.format(segnum)
inst.send_scpi_cmd(cmd)
# Increase the timeout before writing binary-data:
# inst.timeout = 30000
# Send the binary-data with *OPC? added to the beginning of its prefix.
inst.write_binary_data('*OPC?; :TRAC:DATA', dacWaveOn_IQ)
# Set normal timeout
inst.timeout = 10000
resp = inst.send_scpi_query(':SYST:ERR?')
print("Trace Download Error = ")
print(resp)
cmd = ':SOUR:MODE DUC'
resp = inst.send_scpi_cmd(cmd)
cmd = ':SOUR:INT X4'
resp = inst.send_scpi_cmd(cmd)
cmd = ':SOUR:IQM ONE'
resp = inst.send_scpi_cmd(cmd)
sampleRateDACInt = sampleRateDAC * 4
print('Interpolated Sample Clk Freq {0}'.format(sampleRateDACInt))
cmd = ':FREQ:RAST {0}'.format(sampleRateDACInt)
resp = inst.send_scpi_cmd(cmd)
resp = inst.send_scpi_query(':SYST:ERR?')
print("IQ Set Error = ")
print(resp)
cmd = ':SOUR:NCO:CFR1 {0}'.format(ncoFreq)
resp = inst.send_scpi_cmd(cmd)
print('NCO CF: {0}'.format(ncoFreq))
################################################################################
# Direct RF Output CH
cmd = ':INST:CHAN {0}'.format(ch)
inst.send_scpi_cmd(cmd)
cmd = ':TASK:COMP:LENG 1'
inst.send_scpi_cmd(cmd)
cmd = ':TASK:COMP:SEL 1'
inst.send_scpi_cmd(cmd)
cmd = ':TASK:COMP:SEGM 1'
inst.send_scpi_cmd(cmd)
cmd = ':TASK:COMP:NEXT1 1'
inst.send_scpi_cmd(cmd)
cmd = ':TASK:COMP:WRITE'
inst.send_scpi_cmd(cmd)
cmd = ':SOUR:FUNC:MODE TASK'
inst.send_scpi_cmd(cmd)
################################################################################
cmd = ':OUTP ON'
rc = inst.send_scpi_cmd(cmd)
resp = inst.send_scpi_query(':SYST:ERR?')
print("End of CH1 Gen Error = ")
print(resp)
################################################################################

