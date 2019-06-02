#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function
import numpy as np
import cv2
# import time
# import datetime

BLUR_SIZE = 3
VERSION_CV2 = cv2.__version__

def extract_drop_profile(raw_experiment, user_inputs):
    profile_crop = image_crop(raw_experiment.image, user_inputs.drop_region)
    # profile_edges = detect_edges(profile_crop, raw_experiment, user_inputs.drop_region)
    # profile, raw_experiment.ret = detect_edges(profile_crop, raw_experiment, user_inputs.drop_region)
    profile, raw_experiment.ret = detect_edges(profile_crop, raw_experiment, user_inputs.drop_region, -1, 1)
    raw_experiment.drop_data = profile[0]

    needle_crop = image_crop(raw_experiment.image, user_inputs.needle_region)
    raw_experiment.needle_data, ret = detect_edges(needle_crop, raw_experiment, user_inputs.needle_region, raw_experiment.ret, 2)

    

    # # detect needle edges
    # needle_crop = image_crop(raw_experiment.image, user_inputs.needle_region)
    # raw_experiment.needle_data = detect_edges(needle_crop, user_inputs.needle_region)

def fill_contours(image):
    """
    Fills in largest contour in black to remove lighting effects.
    """
    # convert image to black and white
    binaryImg = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    # find largest contour in image    
    contours = cv2.findContours(binaryImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[1]
    maxContour = max(contours,key=cv2.contourArea)
    # fill in largest contour in black on image
    cv2.drawContours(image,maxContour,0,(0,0,0),-1)
    
    return image

def image_crop(image, points):
    # return image[points[0][0]:points[0][1], points[1][0]:points[1][1]]
    # return image[points[0][1]:points[1][1], points[0][0]:points[1][0]]
    # imageUD = np.flipud(image)
    # pixels are referenced as image[y][x] - row major order
    croppedImage = image[int(points[0][1]):int(points[1][1]), int(points[0][0]):int(points[1][0])]
    # fill in image with all black
#    filledImage = fill_contours(croppedImage)
    
    return croppedImage

def detect_edges(image, raw_experiment, points, ret, n_contours):
    # image = np.flipud(imageUD)
    if len(image.shape) != 2:
        image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(image,(BLUR_SIZE,BLUR_SIZE),0) # apply Gaussian blur to drop edge
    if ret == -1:
        ret, thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # calculate thresholding
    # else:
    #     ret, thresh = cv2.threshold(blur,ret,255,cv2.THRESH_BINARY) # calculate thresholding
    # these values seem to agree with 
    # - http://www.academypublisher.com/proc/isip09/papers/isip09p109.pdf
    # - http://stackoverflow.com/questions/4292249/automatic-calculation-of-low-and-high-thresholds-for-the-canny-operation-in-open
    # edges = cv2.Canny(thresh,0.5*ret,ret) # detect edges using Canny edge detection

    # error in PDT code - shouldn't threshold before Canny - otherwise Canny is useless
    edges = cv2.Canny(blur,0.5*ret,ret) # detect edges using Canny edge detection

    if float(VERSION_CV2[0]) > 2: #Version 3 of opencv returns an extra argument
        _,contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    else:
        contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    contour_lengths = [] #list to hold all areas

    for contour in contours:
      length = cv2.arcLength(contour,0)
      contour_lengths.append(length)

    indexed_contour_lengths = np.array(contour_lengths).argsort()[::-1]
    indexed_contours_to_return = indexed_contour_lengths[:n_contours]

    image_height = raw_experiment.image.shape[0]
    offset = [points[0][0], image_height - points[0][1]]
    points = []
    for index in indexed_contours_to_return:
        current_contour = contours[index][:,0]
        for i in range(current_contour.shape[0]):
            current_contour[i,1] = - current_contour[i,1]
            current_contour[i,:] = current_contour[i,:] + offset
        points.append(current_contour[current_contour[:,1].argsort()])

    return points, ret
    # points = largest_contour[largest_contour[:,1].argsort()]

 
    # # determines the largest contour.
    # # hierarchy describes parent-child relationship
    # # this routine determines the length of each contour
    # # and returns the largest
    # drop_index = 0
    # maxLength = 0.0
    # for i in range(np.max(hierarchy+1)):
    #     length = cv2.arcLength(contours[i],0)
    #     # print(i, length)
    #     if length > maxLength:
    #         maxLength = length
    #         drop_index = i


    # # the largest contour
    # largest_contour = contours[drop_index][:,0]

    # # converts the data to (x, y) data where (0, 0) is the lower-left pixel
    # image_height = raw_experiment.image.shape[0]
    # offset = [points[0][0], image_height - points[0][1]]
    # for i in range(largest_contour.shape[0]):
    #     largest_contour[i,1] = - largest_contour[i,1]
    #     largest_contour[i,:] = largest_contour[i,:] + offset
    # points = largest_contour[largest_contour[:,1].argsort()]
    
    # return points, ret

# def calculate_needle_diameter(raw_experiment, fitted_drop_data, tolerances):
