# cutiestix

A desktop application interface to [stix-validator](https://pypi.python.org/pypi/stix-validator) 
written in PyQt. 

## The Name?
It seems like a lot of people pronounce "Qt" as "cutie", so we end up with the 
formula: Qt + STIX = "cutiestix".

## Requirements
The **cutiestix** application has been developed and tested using the following:

* [Python 2.7](http://www.python.org)
* [PyQt 4.8.*](https://www.riverbankcomputing.com/software/pyqt/download)
* [stix-validator 2.4.0](https://github.com/STIXProject/stix-validator)

**Note:** I have seen some integer overflow issues between universal (32/64bit)
Python builds on OSX and 64bit Qt/PyQt. Your best bet is to stick with 32bit 
everything.

## Installation and Usage
To run **cutiestix** just install the requirements listed above. After 
installation, just run the `run-cutiestix.py` script found in the `scripts/`
folder.

```
$ <install PyQt from the link above>
$ cd path/to/cutiestix/repo
$ python setup.py install
$ python scripts/run-cutiestix.py
```

## Repository Layout
* `cutiestix/`: Top-evel Python package.
* `designer/`: Qt Designer files.
* `screenshots/`: Screenshots of **cutiestix**.
* `scripts/`: **cutiestix** executable scripts.
* `setup.py`: Installation script.
* `LICENSE`: Terms of use.
* `README.md`: The README (this file).

## Look and Feel
The following are screenshots of **cutiestix**. A friend of mine said that 
the color scheme made his eyes bleed so get a towel ready for your peepers.

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
* Any non-STIX files that a user attempts to add to **cutiestix** will be 
  silently filtered out. The UI should probably handle this better and notify
  the user of the dropped files, but I haven't had time to work out a nice 
  notification system that I like.
* No CybOX validation. This is by design, so it'll likely never be implemented.

## Terms
This was developed as a way to mess around with PyQt. Use at your own risk! 
See LICENSE file for complete terms.
