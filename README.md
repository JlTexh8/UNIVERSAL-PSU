# UNIVERSAL PSU - ESP32 Live Power Monitor ⚡️

## Overview
This open-source project allows repair technicians to monitor real-time voltage and current consumption directly on a PC screen. It is designed to help diagnose short circuits and power rail issues on logic boards without taking up valuable workspace.

## 🚀 Project Roadmap & Versions
We are developing this tool in stages to support the repair community:
* **[x] Version 4.0 (Current):** USB COM Communication. Reads data directly via serial port.
* **[ ] Version 2.0 (Planned):** WIFI Communication. Wireless monitoring interface.

## Hardware Required
To replicate this project, you will need the following components:
* **Microcontroller:** ESP32 
* **Sensor:** INA260 (Precision digital current and power monitor)
* Jumper wires.

## Installation (USB COM Version)
1. Download the executable `.exe` file from the **Releases** section on the right side of this page.
2. Connect your ESP32 via USB.
3. Open the program to start viewing real-time power consumption.
*(Developers: The raw `.py` source code is available in the main branch for auditing and modification).*

## Support the Community
If this tool helped you diagnose a board, feel free to star this repository, share it with other technicians, or contribute to the code!
