import requests
import cv2
import pytesseract
import numpy as np
import pygetwindow as gw
import pyautogui
import time
import csv
import difflib

region = "10000002"
type_id = "2456"
secondary_system_id = "30000144" #cheap trade hub perimeter
primary_system_id = "30000142" #main trade hub jita




#read Inventory contents and get item name and quantity
def read_inventory_contents():
    global item_name
    global item_quantity
    global inventory_taskbar_position

    #detect inventory picture and get position
    inventory_taskbar_position = pyautogui.locateCenterOnScreen("Pictures\Inventory_Task_Bar.PNG", confidence=.7)

    my_tesseract_config = r"--psm 7 --oem 3"
    inventory_screenshot_region = (int(inventory_taskbar_position.x - 230), int(inventory_taskbar_position.y + 89), 377, 30)
    inventory_contents_screenshot = pyautogui.screenshot(region=(inventory_screenshot_region))
    #save the screenshot for debugging
    inventory_contents_screenshot.save("Tesseract Reading Region.png")

    # Convert the screenshot to an OpenCV format
    inventory_contents_screenshot = cv2.cvtColor(np.array(inventory_contents_screenshot), cv2.COLOR_RGB2BGR)

    # Perform OCR on the captured image using pytesseract
    item_name = pytesseract.image_to_string(inventory_contents_screenshot, config=my_tesseract_config)

    # Preprocess OCR text, add more if needed
    item_name = item_name.strip()  # Remove leading/trailing whitespaces

    # Check if end of list was reached
    if item_name == "Z_Not_Profitable":
        return "Z_Not_Profitable Detected"

    else:
        print("Detected RAW Name by Tesseract:", item_name)

        # Read items list from CSV
        items_list = []
        with open('Item_List.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                items_list.append(row[0])

        # OCR-detected text
        ocr_text = item_name  # Example OCR-detected text

        # Preprocess OCR text, add more if needed
        ocr_text = ocr_text.replace('@', '0')  # Replace @ with 0
        ocr_text = ocr_text.replace(' Il', ' II')  # Replace Il with II

        # Split text by spaces and extract the quantity (last element)
        split_text = ocr_text.split()
        item_quantity = split_text[-1]
        item_name = ' '.join(split_text[:-1])  # Join the remaining elements as the item name

        
        print("Detected Item name:", item_name)
        print("Quantity:", item_quantity)

        # Check for exact match in my items list
        if item_name in items_list:
            #Proceed with exact matched item
            print("Exact match found:", item_name)
        else:
            # Trying to find the closest match
            matched_item_name = difflib.get_close_matches(item_name, items_list, n=1, cutoff=0.8)  # Adjust cutoff as needed
            if matched_item_name:
                # Match found, proceeding with closest match
                print("Closest match found:", matched_item_name[0])
                item_name = matched_item_name[0]
            else:
                # Handle case when no match is found
                print("No matching Item found in the list.")
                item_name = None
                return None
            

        



# Search for matching type_id in the CSV file
def get_type_id(item_name):
    global type_id
    try:
        # Open the CSV file
        with open("Item_List.csv", newline='', encoding='utf-8') as csvfile:
            # Read the CSV file
            reader = csv.reader(csvfile)
            # Iterate through each row
            for row in reader:
                # Check if the item name matches the name in the first column
                if row[0] == item_name:
                    # Return the corresponding type_id from the second column
                    type_id = row[1]
                    return type_id
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")




#API: get sell orders in main trade hub
def get_sell_orders(region, type_id, primary_system_id):
    url = f"https://esi.evetech.net/latest/markets/{region}/orders/?datasource=tranquility&order_type=sell&page=1&type_id={type_id}"
    sell_orders_response = requests.get(url)

    if sell_orders_response.status_code == 200:
        sell_orders = sell_orders_response.json()
        filtered_sell_orders = [order for order in sell_orders if order.get('system_id') == int(primary_system_id)]
        return filtered_sell_orders
    else:
        print(f"Error calling API: {sell_orders_response.status_code}")
        return None

    
#API: get buy order in main and secound trade hub
def get_buy_orders(region, type_id, primary_system_id, secondary_system_id):
    url = f"https://esi.evetech.net/latest/markets/{region}/orders/?datasource=tranquility&order_type=buy&page=1&type_id={type_id}"
    buy_orders_response = requests.get(url)

    if buy_orders_response.status_code == 200:
        buy_orders = buy_orders_response.json()
        filtered_buy_orders = [order for order in buy_orders if order.get('system_id') in (int(primary_system_id), int(secondary_system_id))]
        return filtered_buy_orders
    else:
        print(f"Error calling API: {buy_orders_response.status_code}")
        return None



#API: For selling Item from Hangar: Check if item is still profitable and calculate price to sell
def is_item_profitable_to_sell(region, type_id, primary_system_id, secondary_system_id):
    global underbid_price
    # Get the two cheapest sell orders in Jita
    sell_orders = get_sell_orders(region, type_id, primary_system_id)
    if not sell_orders:
        print("No sell orders found")
        return None

    sorted_sell_orders = sorted(sell_orders, key=lambda x: x['price'])

    cheapest_sell_price = sorted_sell_orders[0]['price']
    second_cheapest_sell_price = sorted_sell_orders[1]['price'] if len(sorted_sell_orders) > 1 else None

    # Get the two most expensive buy orders in the perimeter station or Jita station
    buy_orders = get_buy_orders(region, type_id, primary_system_id, secondary_system_id)
    if not buy_orders:
        print("No buy orders found")
        return None

    sorted_buy_orders = sorted(buy_orders, key=lambda x: x['price'], reverse=True)

    most_expensive_buy_price = sorted_buy_orders[0]['price']
    second_most_expensive_buy_price = sorted_buy_orders[1]['price'] if len(sorted_buy_orders) > 1 else None

    # Calculate average prices
    average_sell_price = (cheapest_sell_price + second_cheapest_sell_price) / 2 if second_cheapest_sell_price else cheapest_sell_price
    average_buy_price = (most_expensive_buy_price + second_most_expensive_buy_price) / 2 if second_most_expensive_buy_price else most_expensive_buy_price

    print(f"Average sell price: {average_sell_price}")
    print(f"Average buy price: {average_buy_price}")

    # Check if the average price of the two cheapest sell orders is 30% more than the average price of the two most expensive buy orders
    if average_sell_price >= 1.3 * average_buy_price:
        print("Item is profitable")
        # Determine the price to underbid
        if cheapest_sell_price <= 0.9 * second_cheapest_sell_price:
            underbid_price = second_cheapest_sell_price # Underbid the second cheapest by 10 ISK
        else:
            underbid_price = cheapest_sell_price # Underbid the cheapest by 10 ISK
        print(f"Price to underbid: {underbid_price}")
        return underbid_price
    else:
        print("Item is not profitable")
        underbid_price = None
        return None










#if item is profitable sell at underbid price, else put item into container
def sell_or_store_item(underbid_price, item_quantity, inventory_taskbar_position):
    
    item_position = (inventory_taskbar_position.x, inventory_taskbar_position.y + 89)
    if underbid_price is not None:  #item is profitable and underbid price is calculated
        print("Selling the item")

        # Right click on the item
        pyautogui.moveTo(item_position, duration=.3)
        pyautogui.rightClick(item_position)
        time.sleep(.3)

        # Click on the "Sell This Item" button
        sell_button_position = pyautogui.locateCenterOnScreen("Pictures\Sell_This_Item.png", confidence=.8)
        if sell_button_position is not None:
            pyautogui.moveTo(sell_button_position, duration=.4)
            pyautogui.click(sell_button_position)
        else:
            print("Sell button not found")

        time.sleep(.5)

        # Find the location of the "Sell Item Prices" window
        sell_prices_position = pyautogui.locateCenterOnScreen("Pictures\Sell_Item_Prices.png", confidence=.8)
        if sell_prices_position is not None:
            print("Sell Item Prices window found at:", sell_prices_position)
        else:
            print("Sell Item Prices window not found")

        #click on the price field
        pyautogui.moveTo(sell_prices_position.x - 20, sell_prices_position.y + 15, duration=.4)
        pyautogui.click(duration=.1)
        pyautogui.click(duration=.1)
        #type in the underbid price
        pyautogui.write(str(underbid_price))
        #press key down to reduce the price by one
        pyautogui.press('down')
        #locate and click on the sell button
        sell_button_position = pyautogui.locateCenterOnScreen("Pictures\Sell_Button.PNG", confidence=.8)
        pyautogui.moveTo(sell_button_position, duration=.3)
        #pyautogui.click(sell_button_position, duration=.3)

    else: #store item in container
        # Detect the position of the container
        container_position = pyautogui.locateCenterOnScreen("Pictures\Container_Inventory.PNG", confidence=.7)
        if container_position is not None:
            # Drag and drop the item into the container
            pyautogui.moveTo(item_position, duration=.2)
            pyautogui.dragTo(container_position, duration=1.5)
            print("Item stored in the container")
        else:
            print("Container not found")


# Move item to container
def move_item_to_container():
    # Detect the position of the item
    item_position = (inventory_taskbar_position.x, inventory_taskbar_position.y + 89)
    # Detect the position of the container
    container_position = pyautogui.locateCenterOnScreen("Pictures\Container_Inventory.PNG", confidence=.7)
    if container_position is not None:
        # Drag and drop the item into the container
        pyautogui.moveTo(item_position, duration=.2)
        pyautogui.dragTo(container_position, duration=1.5)
        print("Item stored in the container")
    else:
        print("Container not found")


time.sleep(3)

#read_inventory_contents()


while True:

    if read_inventory_contents() == "Z_Not_Profitable Detected":

        print("End of list reached")
        break

    elif item_name is not None:
        get_type_id(item_name)
        #check if item is profitable
        is_item_profitable_to_sell(region, type_id, primary_system_id, secondary_system_id)
        sell_or_store_item(underbid_price, item_quantity, inventory_taskbar_position)

    else:
        move_item_to_container()
        







