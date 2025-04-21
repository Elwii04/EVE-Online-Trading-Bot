import cv2
import pytesseract
import numpy as np
import pygetwindow as gw

# Initialize Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

# Get handle to EVE game window
eve_window = gw.getWindowsWithTitle('EVE')[0]

while True:

    # Take screenshot of EVE window
    eve_image = eve_window.screenshot()

    # Convert to OpenCV format
    eve_image = np.array(eve_image) 

    # Convert to grayscale
    eve_gray = cv2.cvtColor(eve_image, cv2.COLOR_BGR2GRAY)

    # Threshold image to extract text
    _, eve_thresh = cv2.threshold(eve_gray, 127, 255, cv2.THRESH_BINARY)

    # Perform OCR on thresholded image 
    eve_text = pytesseract.image_to_string(eve_thresh)

    print(eve_text)

    # Delay to avoid hogging resources
    cv2.waitKey(1000)
