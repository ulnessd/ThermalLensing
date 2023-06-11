# Thermal Lensing Application

This is a Python GUI application designed to control a Thorlabs DCC series camera and a shutter controlled by a PIC10F200 microcontroller. The communication with the PIC10F200 microcontroller is facilitated using a DTech FTDI USB to TTL Serial Adapter 5V. The application is built using Tkinter for GUI and PySerial for serial communication.

## Installation

The software runs on Python and has several dependencies that can be installed via pip. Below are the steps to setup and run the project.

1. Clone the repository:

```bash
git clone https://github.com/ulnessd/ThermalLensing.git
```
2. Install the dependencies:
Navigate to the project directory and run the following command:

```bash
pip install -r requirements.txt
```

## Usage
To use the program, navigate to the project directory and run the main python file:

```bash
python AquisitionProgram.py
```

Follow the prompts in the GUI to select the COM port and control the shutter and camera.

## Hardware Setup
The software is designed to control a Thorlabs DCC series camera and a shutter using a PIC10F200 microcontroller.

### Thorlabs DCC family Cameras
Note: you will need to get put the following dll files in your working directory
 - uc480_64.dll (for Windows 64 bit)
 - uc480_tools_64.dll
 - us480DotNet.dll

These are in this repository but also available from Thorlabs directly.

As a separate test you can use
```bash
python CameraViewer.py
```

### Serial Commnication with PIC microcontroller
The DTech FTDI USB to TTL Serial Adapter 5V is used for communication with the microcontroller.
As a separate test you can use
```bash
python SerialToggle.py
```

The camera and shutter should be connected to the same system running the application.

For specific instructions and code related to the PIC10F200 microcontroller, see the README file in the pic10f200 directory.

For specific instructions and code related to the camera setup and image analysis, see the README file in the image_analysis directory.
