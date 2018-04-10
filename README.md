# Tracesniffer-GUI  WIP
![Tracesniffer-logo](resources/img/TraceSnifferLogo_small.png)

This tool provides you with a useable frontend for the existing [Tracesniffer-plugin](https://github.com/adler305/Tracesniffer-Plugin).
You can configure different settings, see all the trace-contents in a table, a plot and save the measurements for later use.

The application is a Work In Progress. The program may crash at any point. No warranty is given on
correct measurements. It is not intended to replace professional tools, but rather a quick prototyping / analyzing system for RTOS.

Please report any Issues that you find with a small explanation of how / why the issue happened. If the issue can be reproduced, we will
try to fix it as soon as we can.

## Prerequisites:

Please resolve any missing dependencies if you are not using the binaries provided (currently no binaries are provided).
This includes (but may not be limited to):
- PyQt5
- Plotly
- CSV
- QDarkStyle
- Configparser
- PySerial

## Usage-explanation:

This tool can be used to display the trace-information sent via Tracesniffer-plugin. Usually, the tool must first be configured
(see Config-explanation point) to the correct parameters.
After a usage-type is selected, the measurement can be Stopped/Started via buttonpress.
After a measurement is complete, an indication message is displayed in the Statusbox.
The Measurement can then be plotted directly in the program or saved for later evaluation purposes.
Old measurement files (.sniff) can be re-opened and displayed in table-form or plot.

## Config-explanation:

- Serial parameters
  - COM-Port: Your Serialport (choose from a list of open ports)
  - BAUD-Rate: The baud-rate set according to your UART configuration
  - StopBits / Parity: According to UART configuration
- Measurement Configuration
  - Measurement mode:
    * Singleshot: Enter a specified duration (in ticks). The measurement will be complete after the relative amount of ticks.
    * Trigger: Select a Trigger Type (see below). The measurement will be complete after a trigger-type has been found and
    the relative amount of ticks (specified in the textbox) have passed.
    * Continuous: The measurement will continue until the 'Stop-Analyzing'-button is manually pressed. CAUTION: No overflow checks
    have been implemented yet (TODO), use this mode on your own accord, buffers may overflow, the program may crash...
  - Trigger Type: Specify which Trace-information Type you want to start the Trigger on. This settings is ignored in Singleshot/Cont mode
  - Count Time Bytes: The amount of Time-Bytes you send via UART (as per Tracesniffer-plugin configuration). Default: 16-Bit = 2 Bytes
  - Save Inc_Tick Data: Since every Increment-tick signal is sent over the UART-port, it can be useful to turn this checkbox off
  in order to prevent packet-spam. (**Recommended setting: Off/Unchecked**)
  - Activate Logging: Activates debug-logging. If problems occur, a few signals which might be helpful will be logged. (**Recommended: Off/Unchecked**)
  - Save Logfile: Saves the Logfile (only if action was logged previously)
  - Wait for uC Reset: Handle a specific case, where you explicitly want to wait for a complete uC Reset. Only enable this when necessary. (i.e you KNOW that you are going to Reset the uC during the measurement)
  
  
