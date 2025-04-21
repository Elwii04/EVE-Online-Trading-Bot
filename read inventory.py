import pytesseract

my_tesseract_config = r"--psm 7 --oem 3"

inventory_screenshot = pytesseract.image_to_string("Pictures\Test1.PNG", config=my_tesseract_config)
print(inventory_screenshot)