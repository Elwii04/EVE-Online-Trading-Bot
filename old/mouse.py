import pyautogui
import time


try:
    while True:
        print(pyautogui.position())
        time.sleep(.8)
except KeyboardInterrupt:
    print("Bot stopped by user")
