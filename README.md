# iso-cv
**mass-phenotyping of isopods using the opencv library** 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [installation](#installation)
- [output/response](#outputresponse)
- [working principle](#working-principle)
- [camera script](#camera-script)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## introduction

**iso-cv** (-> **iso**pod-**c**omputer**v**ision) is a collection of scripts for mass phenotyping using the opencv library in python. These scripts have been used with the freshwater isopod *Asellus aquaticus*, for the scientific background refer to [http://luerig.net/Research/#Isopods](http://luerig.net/Research/#Isopods). For more detailed information on the actual code refer to the inline annotations inside the python scripts.

**Please feel free to get in touch with me if you need help running the script or have questions about customizing it for your own study-system/organism: [contact @ eawag](http://www.eawag.ch/en/aboutus/portrait/organisation/staff/profile/moritz-luerig/show/)**


<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig1.png" />

---

## installation

- python (3.6)
- opencv (3.3.1) + dependencies (more info here: https://stackoverflow.com/questions/23119413/how-do-i-install-python-opencv-through-conda)

install, for example, with anaconda (https://www.anaconda.com/download/):

```
conda update conda
conda install -c conda-forge opencv 
conda install opencv numpy os math copy
```

IMPORTANT: The script is not standalone, so a python interpreter needs to be used to modify and execute the script (e.g. [Spyder](https://github.com/spyder-ide/spyder)). Directories and input data need to be specified beforehand inside the script. At some point in the future I may provide a standalone executable version of the program.


---

## output/response

There are two types of procedures: one was programmed for use with scanner-images that contain many specimens, the other is intended for camera-images that contain only single isopods. Both scripts create control images to check whether the segmentation was accurate, and text-files that contain the phenotypic information:

- length
- area size
- mean grayscale value
- maximum grayscale value
- minimum grayscale value
- standard deviation of grayscale values (variation among pixels)

Additionally, a numeric label and x/y coordinates for the pixels are included so the control images can be attributed to the phenotypic information.

<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig2.png" />

*Left: dead specimens of A. aquaticus that were scanned in a modified flatbed-scanner. Right: alive specimen that was photographed with a camera-stand*
  
Images created with a flatbed scanner have consistent exposure and fixed resolution, so no brightness or scale information needs to be processed prior to phenotyping if the scanner settings are kept the same. For images taken with a camera it is important to ensure reproducible brightness/exposure and distance from the specimens across multiple measurements. Moreover, camera images tend to have more noise and light-artifacts, which may require some treatment to make the scripts work.  

---

## working principle

The scripts are using thresholding algorithms to segment the foreground, in our case the isopod, from the background. Depending on the type of image, a different type of algorithm is used for segmentation (adaptive thresholding for camera images, or Otsu's binarization for scanned isopods). Have a look at the opencv documentation for more details on thresholding: [https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html)

**i) - Finding the ROI.** From a thresholded image then a binary mask can be created to select the region of interest (ROI) that will be inlcuded for phenotyping. This approach is computatively more intensive than simply segmenting the whole image, but delivers better results as a ROI tends to have smaller variability as the whole image, which improves the result of the thresholding algorithms.  

<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig3.png" />

*From left to right: the original image from the scanner is converted to grayscale, thresholded (using one of the thresholding algorithms - white is "foreground", black is "background"), a bounding rectangle is drawn around the foreground area showing the region of interest (ROI), the ROI is used for the actual image analysis*

**ii) - Segmentation inside the ROI.**  Within the ROI another thresholding operation is performed, but this time we need to get an "isopod-foreground" that is is clean as possible, and without legs and antennae. This is achieved with morphological operations, by which we first close holes and then erode the perimeter of the contour around the ispod. Once this has been done, a mask is created that spcecifies the area to be segmented from the image and thus the pixels that will be used to calculate the phenotype metrics. 

[https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html)

<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig4.png" />

*From left to right: ROI, thresholded ROI, mask after morphological operations, segmented isopod, area in ROI that was used for segmentation and the extraction of phenotypic information*

After the extraction, the data should be checked for errors and false positives such as artifacts or reflections from the scanner, or, as in this case, an isopod that was not completely inside the scanning area.

<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig5.png" />

---

## camera script

Pictures from a camera stand usually require additional treatment before they can be processed:

1) Scale needs to be set for every set of pictures with different camera zoom
2) Brightness / exposure can be different and needs to be matched
3) Different cleaning operations have to be performed to remove noise and reflections from the images 

<img src="https://github.com/mluerig/iso-cv/raw/master/assets/iso-cv-fig6.png" />

*Left: colour/brightness control card with scale on it. Middle: different exposure (brighter image). Right: different zoom (zoomed in)*




