# SlicerMRUSLandmarking
Repository to create a module for slicer which improves the choosing of landmarks between MR and US volumes

### Instructions for installing the module
1. On this webpage press the green button **'Code'** and choose **'Donwload ZIP'** from the dropdown menu
2. After the .zip file is downloaded unpack it somewhere (remember the location)
3. Open Slicer3D
4. Enable developer mode as shown in the screenshot below
![Enabling develope mode](misc/enable_develope_mode.png)
5. Open the **'Extension Wizard'** module
6. From **'Extension Tools'** choose **'Select Extension'**
7. Choose the folder where the .zip file was unpacked


### Instructions for using the module

*A dummy dataset based on RESECT[1] can be found
[here](https://www.dropbox.com/sh/gabm0rqdh8kttj6/AADJfwfJnduJG4GJ92tygPufa?dl=0)*
1. Search for the module **'MRUSLandmarking'** and open it
   1. (Ignore the 'Reload and Test' section)

![Extension screenshot](./misc/GUIpreview.png)

*Starting from the top:*

1. **'Common field of view'**
   1. choose the MR and three US volumes
   2. CLick on 'Set lower threshold to 1...' to set the lower threshld of the US volumes to 1
      1. thanks to this the black border surrounding the US volumes (which consists of 0s) will disappear in the overlay
   3. Click on 'Create intersection' - this will create the intersection of the three US images (intersection as the
   logical operator - the common field of view)
   4. Wait for a few seconds for the intersection to be created and displayed

2. **'View controls'**
   1. Choose between the standard view (as seen in the screenshot) and the 3-over-3 view
   2. When the 3-over-3 view is activated, choose which row(s) (top, bottom or both) should be active
      1. 'active' meaning which controls (e.g. switching between volumes) will act on them
   3. Click on 'Switch order of displayed volumes' if you want the order in which the volumes are displayed switched

3. **'Keyblard shortcuts'**
   1. **d** - set a new fiducial
   2. **a** - move forwards through the selected volumes (two volumes are displayed at all times, e.g. 2&3 and upon
   moving forward 3&4 are displayed, then 4&1 and finally 1&2)
      1. switching the order of displayed volumes would switch e.g. from 1&2 to 2&1
   3. **s** - move backwards through the selected volumes
   4. **y** - move forwards through the created landmarks (the landmark list hast to be named 'F')
   5. **x** - move backwards through the created landmars
   6. **1** - set foreground opacity to 0.0
   7. **2** - set foreground opacity to 0.5
   8. **3** - set foreground opacity to 1.0
   9. **q** - increase foreground opacity by 0.02
   10. **2** - decrease foreground opacity by 0.02
      

[1] Xiao, Yiming, et al. "RE troSpective Evaluation of Cerebral Tumors (RESECT): A clinical database of pre‐operative
MRI and intra‐operative ultrasound in low‐grade glioma surgeries." Medical physics 44.7 (2017): 3875-3882.