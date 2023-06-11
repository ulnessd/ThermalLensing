# PIC10F200 Assembly Code
This repository contains the Assembly language code written for 
the PIC10F200 microcontroller using the MPLAB v6.05 IDE and the 
XC8 compiler. The code is designed to interface with a larger 
Python-based application, creating a hardware-software interface 
for a Thermal Lensing Measurement project.

## Description
The main function of this code is to read from a UART interface 
and toggle a General Purpose I/O (GPIO) pin on the PIC10F200. This 
GPIO pin is then connected to a shutter control system. The UART 
interface waits for a specific signal from the Python application, 
and upon receiving it, triggers the shutter to open or close.

The assembly code follows a simple operational pattern:

1. Initialization: It sets GPIO (General Purpose Input/Output) pin GP0 as an output pin and GP2 as an input pin.

2. Mainloop: It enters an infinite loop where it sets GP0 to low and then goes into a hold state.

3. HOLDloop: In the hold state, it waits for the UART signal (coming from GP2) to go low (since UART idle state is high). When UART signal goes low, it breaks the hold state and returns to the main loop.

Once it returns to the mainloop, it sets GP0 to high for a period, and 
then it sets it to low again. This high and low toggle of GP0 
essentially controls the open and close state of the shutter.

It repeats the mainloop.

The delay function is a triple-nested loop used for creating a delay 
between opening and closing the shutter. The delay is determined by 
the value loaded into the Working Register (W) before calling the delay 
function.

#How It Fits Into The Larger Project
This code plays a critical role in the larger Thermal Lensing 
Measurement project. The larger Python-based application controls 
a thermal imaging camera (Thorlabs DCC series) to take images of 
a sample. It uses this assembly code to control a shutter mechanism 
via the FTDI USB to TTL Serial Adapter. The Python program sends 
a specific signal (b'\xFF') through the serial port. This signal 
is received by the PIC10F200, which triggers the shutter mechanism to 
open or close, effectively controlling when to capture images based 
on the thermal lensing effect.