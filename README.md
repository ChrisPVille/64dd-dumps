# 64dd-dumps
Various data dumps from the 64DD. The .sr files are for the wonderful open-source Sigrok PulseView.

Folders:
RLL = Raw Run-Length-Limited data (more or less what's physically on the disk)
NRZ = Non-Return-to-Zero data (self-clocking data stream between RLL and SD29 chip. Mostly represents the user read/write data)
H8 = Captures related to the H8 chip
decoders = Custom sigrok decoders related to the work (very rough - Don't say I didn't warn you)
