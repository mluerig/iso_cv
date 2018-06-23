# -*- coding: utf-8 -*-
"""
Created: 2016/03/31
Last Update: 2018/06/23
Version 0.1.3
@author: Moritz Lürig
"""

#%% import packages

import cv2
import os
import numpy as np
import numpy.ma as ma
import copy
import math
        
#%% directories

# name your project directory 
my_project_dir = "iso-cv"

if not os.getcwd() == os.path.join(os.path.abspath('..') , my_project_dir):
    if not os.path.exists(os.path.join(os.path.abspath('..') , my_project_dir)):
        os.makedirs(os.path.join(os.path.abspath('..') , my_project_dir))
    os.chdir(my_project_dir)

# you need these folders:
in_dir = "in" # raw colour images
out_dir = "out" # output directory with control images and text files

# they should be inside a main working directory
main = os.path.join(os.getcwd(), "python", "scanner")

# if they don't exist, create them 
for folder in [in_dir, out_dir]:
    if not os.path.exists(os.path.join(main, folder)):
        os.makedirs(os.path.join(os.getcwd(), "python", "scanner",  folder))

#%% set detection and phenotyping parameters
# objects are detected thresholding (colour/grayscale inage to binary image). objects can then be cleaned by performing morphological operations on images (see https://docs.opencv.org/3.4/d9/d61/tutorial_py_morphological_ops.html). objects are "closed" first and then "opened"
    
# (i) OBJECT DETECTION - find ROIs in image 
det_len_val = 100 # min length of object detected (too small values will make detection potentially noisy)

# probably no need to touch this:
det_kern_close = (5,5) # closing kernel size (how many pixels are added to border)
det_it_close = 3 # closing iteratiuons
det_kern_open = (7,7) # opening kernel size (how many pixels are removed from border)
det_it_open = 5 

# (ii) OBJECT RECOGNITION
# these are factors that can be used to increase or decrease the detection values below (at ii)). since kernel size and iterations are derived from object size, factors are being used to increase or decrease them. default is 1 (no change)

rec_kern_close_fac = 1 
rec_it_close_fac = 1 
rec_kern_open_fac = 1
rec_it_open_fac = 1


#%% procedure
    
# all steps are repeated for each image
for i in os.listdir(os.path.join(main, in_dir)):
    if os.path.isfile(os.path.join(main, in_dir, i)):
        
# make separate text-file for each image, write to out_dir
        res_file = open(os.path.join(main, out_dir,  i[0:len(i)-4] + '.txt'), 'w')
        res_file.write('PyLabel' + '\t' + 'X' + '\t'+  'Y'+ '\t'+  'Length'+ '\t'+ 'Area'+ '\t'+ 'Mean'+ '\t'+  'StdDev'+ '\t'+  'Min'+ '\t'+  'Max' + '\n')
        res_file.close()
        
# load image and convert to grayscale
        img = cv2.imread(os.path.join(main, in_dir, i))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
# =============================================================================
# i) find ROIs in image
# =============================================================================
        
# tresholding image - (adaptive thresholding for camera images, or Otsu's binarization for scanned isopods - https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html)       
        ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,299,9)

# cleanup - "closing operation" with rectangle-shaped kernel, "opening operation" with cross-shaped kernel - good for removing legs (https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html)
        kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT,det_kern_close)
        kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS,det_kern_open)
        morph1 = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel1, iterations = det_it_close)
        morph2 = cv2.morphologyEx(morph1,cv2.MORPH_OPEN,kernel2, iterations = det_it_open)

# find contours 
        ret, contours, hierarchy = cv2.findContours(copy.deepcopy(morph2),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_L1)

# loop through all contours in image
        idx = 0
        #rows = list()
        for cnt in contours:
            
# exclude small contours (fewer than 50 points - isopods are complex structures that will a lot of points - https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html)            
            if len(cnt) > 50:
                # bounding rectangle of isopod contour
                rx,ry,w,h = cv2.boundingRect(cnt)
                
# additional control mechanism - define minimal and maximal dimensions of bounding rectangle and approximate shape length (length of longer ellipse axis)
                ellipse = cv2.fitEllipse(cnt)
                center,axes,orientation = ellipse 
                L = np.mean([math.sqrt(axes[1]*axes[0]*math.pi),max(axes)])
                if L > det_len_val:
                    idx += 1
                    
# get ROI from image
                    roi=gray[max(0,ry-100):ry+h+100,max(0,rx-100):rx+w+100]                                     

# =============================================================================
# ii) work with ROI
# =============================================================================
                    
                    ret, roi_thresh = cv2.threshold(roi,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
                    
# adaptive kernel size and number of iterations of morphology-operations - this is a trick to deal with a broad size spectrum. bigger kernels and more iterations for large isopods, smaller kernels and fewer iterations. 
# THIS WILL HAVE THE BIGGEST EFFECT ON THE RESULTS
                    
                    if L > 600:
                        k3 = 3; niter3 = int(round(L * 0.005) -4)  * rec_kern_close_fac
                        k4 = 9; niter4 = int(round(L * 0.007))   * rec_it_close_fac

                    else:
                        k3 = 3; niter3 = int(round(L * 0.015) - 4)  * rec_kern_open_fac
                        k4 = 5; niter4 = int(round(L * 0.03) - 8) *  rec_it_open_fac
                        
                    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT,(k3,k3))
                    morph3 = cv2.morphologyEx(roi_thresh,cv2.MORPH_CLOSE,kernel3, iterations = niter3)
                    
                    kernel4 = cv2.getStructuringElement(cv2.MORPH_CROSS,(k4,k4))
                    morph4 = cv2.morphologyEx(morph3,cv2.MORPH_OPEN,kernel4, iterations = niter4)
                    
                    
# create contour, centroid, and min. circle diameter (for length). the contour will be needed to create the mask (the "cookie-cutter"), the centroid will be used to draw a circle, then circle diameter is the length of our isopod                   
                    ret1, contours1, hierarchy1 = cv2.findContours(copy.deepcopy(morph4),cv2.RETR_LIST ,cv2.CHAIN_APPROX_TC89_L1)       
                    if contours1:
                        areas = [cv2.contourArea(cnt1) for cnt1 in contours1]                
                        shape = contours1[np.argmax(areas)]
                        (cx,cy),radius = cv2.minEnclosingCircle(shape)
                        
# create the mask and create a masked array ("TRUE" pixels will be included, "FALSE" pixels excluded)
                        mask = np.zeros_like(morph4) # Create mask where white is what we want, black otherwise
                        mask = cv2.drawContours(mask, contours1, np.argmax(areas), 255, -1) # Draw filled contour in mask
                        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
                        masked =  ma.array(data=roi, mask = np.logical_not(mask))
                    
# calculate metrics for the pixels inside the mask
                    M = cv2.moments(shape)
                    a = int((M['m10']/M['m00'])+max(0,rx-100))
                    b = int((M['m01']/M['m00'])+max(0,ry-100))
                    c = (int(radius) * 2)/94.6876
                    d = np.mean(masked) # mean grayscale value
                    e = np.std(masked) # standard deviation of grayscale values
                    f = np.min(masked) 
                    g = np.max(masked)
                    area = (cv2.contourArea(shape)/94.6876)/94.6876
  
# =============================================================================
# iii) create control image and text files that contain the results
# =============================================================================    
    
# write ROI info (centroid-coordinates and label) and metrics to file                           
                    res_file = open(os.path.join(main, out_dir, i[0:len(i)-4] + '.txt'), 'a')
                    res_file.write(str(idx) + '\t' + str(round(a,2)) + '\t' + str(round(b,2)) + "\t" + str(round(c,2)) + "\t" + str(round(area,2)) + "\t" +str(round(d,2)) + "\t" + str(round(e,2)) + "\t" + str(round(f,2)) + "\t" +  str(round(g,2))+ "\n")
                    res_file.close()
                    
                    
# draw bounding rectangle, contour and circle into original image to check if they are correct
                    roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
                    roi = cv2.circle(roi,(int(cx),int(cy)),int(radius),(255,0,0),3)
                    roi = cv2.drawContours(roi, [shape], 0, (0,255,0), 3)   

# draw ROI-box and label into original image
                    img[max(0,ry-100):ry+h+100,max(0,rx-100):rx+w+100] = roi                    
                    img = cv2.rectangle(img,(max(0,rx-100),max(0,ry-100)),(rx+w+100,ry+h+100),(0,0, 255),3)
                    cv2.putText(img, str(idx),(a,b), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),7,cv2.LINE_AA)

# save control image                    
        cv2.imwrite(os.path.join(out_dir , i[0:len(i)-4] + '_' + 'output.jpg'), img)   
        print(i)



    

                    

