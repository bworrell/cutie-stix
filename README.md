cutiestix
=========

A desktop application interface to [stix-validator](https://pypi.python.org/pypi/stix-validator) written in PyQt. 

## The Name?
It seems like a lot of people pronounce "Qt" as "cutie", so we end up with the formula: Qt + STIX = "cutiestix".

## Requirements
The **cutiestix** application has been developed and tested using the following:

* Python 2.7 (32bit)
* Qt 4.8
* PyQt 4.8.*
* stix-validator 2.4.0

**Note:** I have seen some integer overflow issues between universal (32/64bit) Python builds on OSX and 64bit Qt/PyQt. Your best bet is to stick with 32bit everything.

## Look and Feel
The following are screenshots of **cutiestix**.

### Main Window
The following is a screenshot of the main validation window of **cutiestix**.
![Main Window](https://raw.githubusercontent.com/bworrell/cutiestix/develop/screenshots/mainwindow.png)

### Validation Remediation and Reports
Users can open XML files to remediate validation errors and view validation reports (in development).
![Main Window](https://raw.githubusercontent.com/bworrell/cutiestix/develop/screenshots/menus.png)

### Terms
This was developed as a way to mess around with PyQt. Use at your own risk! See LICENSE file for complete terms.
