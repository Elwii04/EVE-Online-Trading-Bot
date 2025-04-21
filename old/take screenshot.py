import pygetwindow as gw
import pyautogui
import time

# Function to find the EVE Online window by its title
def find_eve_window(title):
    try:
        return gw.getWindowsWithTitle(title)[0]
    except IndexError:
        raise Exception("EVE Online window not found.")

# Specify the title of your EVE Online window
eve_window_title = "EVE"

# Find the EVE Online window
eve_window = find_eve_window(eve_window_title)

# Activate the EVE Online window to bring it to the front
eve_window.activate()

# Wait for a short moment to ensure the window is active
time.sleep(1)

# Get the position and size of the EVE Online window
eve_window_info = eve_window.box

# Capture the screenshot of the EVE Online window
eve_screenshot = pyautogui.screenshot(region=(eve_window_info[0], eve_window_info[1], eve_window_info[2], eve_window_info[3]))

# Save the screenshot to a file
eve_screenshot.save("eve_screenshot.png")

print("Screenshot saved successfully.")
