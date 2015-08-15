# cutiestix

A desktop application interface to [stix-validator](https://pypi.python.org/pypi/stix-validator) 
written in PyQt. 

## The Name?
It seems like a lot of people pronounce "Qt" as "cutie", so we end up with the 
formula: Qt + STIX = "cutiestix".

## Requirements
The **cutiestix** application has been developed and tested using the following:

* Python 2.7
* Qt 4.8.*
* PyQt 4.8.*
* stix-validator 2.4.0

**Note:** I have seen some integer overflow issues between universal (32/64bit)
Python builds on OSX and 64bit Qt/PyQt. Your best bet is to stick with 32bit 
everything.

## Look and Feel
The following are screenshots of **cutiestix**.

### Main Window
The following is a screenshot of the **cutiestix** main window during a batch
validation task.  

![Main Window](https://raw.githubusercontent.com/bworrell/cutiestix/master/screenshots/mainwindow_during.png)

### Validation Error Reports
Users can view XML, STIX Best Practices, and STIX Profile validation error reports.

![Menus](https://raw.githubusercontent.com/bworrell/cutiestix/master/screenshots/menus.png)


Tabbed interface to separate validation reports.  

![Tabs] (https://raw.githubusercontent.com/bworrell/cutiestix/master/screenshots/tabs.png)

### STIX Profile Transformation
Users can transform STIX Profiles (Excel documents) into XSLT or Schematron 
documents via the `Transform` menu options.

![Menus](https://raw.githubusercontent.com/bworrell/cutiestix/master/screenshots/transform.png)

## Known Issues
The following items are known issues or deficiencies with **cutiestix**:

* Drag n' drop doesn't work in OSX. There seems to be a [bug in Qt](https://bugreports.qt.io/browse/QTBUG-40449) 
  where filenames aren't reported correctly in file drop events. I think it 
  was fixed in Qt 5 but it seems alive and well in (Py)Qt 4.8.
  
* No CybOX validation. This is by design, so it'll likely never be implemented.

## Terms
This was developed as a way to mess around with PyQt. Use at your own risk! 
See LICENSE file for complete terms.
