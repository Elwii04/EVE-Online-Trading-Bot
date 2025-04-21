import cv2
import pytesseract
import numpy as np
import pygetwindow as gw
import pyautogui
import time
import win32gui, win32api, win32con

def move_to_wallet():
    global wallet_position
    wallet_position = pyautogui.locateCenterOnScreen("Pictures\Sidebar_Wallet.PNG", confidence =.7)
    print(wallet_position)
    pyautogui.moveTo(wallet_position)

def move_to_inventory():
    global inventory_position
    inventory_position = pyautogui.locateCenterOnScreen("Pictures\Sidebar_Inventory.PNG", confidence=.7)
    print(inventory_position)
    pyautogui.moveTo(inventory_position)

#detect the EVE window and check if it was successful
eve_window = gw.getWindowsWithTitle('EVE')[0]
if eve_window == None:
    print('EVE window not found')
    exit()
else:
    print('EVE window found')

#sleep for 4 secounds
time.sleep(4)

#get screenshot of EVE window
eve_screenshot = pyautogui.screenshot

#locate the wallet on sidebar
move_to_wallet()


time.sleep(1)

#define a variable for the region to take the screenshot
wallet_screenshot_region = (
    int(wallet_position.x + 140),
    int(wallet_position.y + 2),
    116,
    20
)

# Capture the screenshot of the specified region using pyautogui
wallet_screenshot = pyautogui.screenshot(region=(wallet_screenshot_region))

# Convert the screenshot to an OpenCV format
wallet_screenshot = cv2.cvtColor(np.array(wallet_screenshot), cv2.COLOR_RGB2BGR)

# Perform OCR on the captured image using pytesseract
wallet_balance = pytesseract.image_to_string(wallet_screenshot)

# Print the wallet balance
print("Your wallet balance is: " + (wallet_balance))

#filter out . and ISK and and make a int 
wallet_balance = ''.join(filter(str.isdigit, wallet_balance))
wallet_balance = int(wallet_balance)

#Navigating to the inventory
move_to_inventory()
pyautogui.click()

#read the inventory contents
inventory_screenshot = pytesseract.image_to_string("Pictures\Inventory_Test.PNG")
print(inventory_screenshot)