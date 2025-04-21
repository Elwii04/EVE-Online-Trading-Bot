# Changes: changed all item_name to item_name
# Exchanged fixed path to Item_List with variable csv_path



import pyautogui
import time
import cv2
import pytesseract
import numpy as np
import os
import requests
import pygetwindow as gw
import time
import csv
import difflib


region = "10000002"
secondary_system_id = "30000144" #cheap trade hub perimeter
primary_system_id = "30000142" #main trade hub jita
access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkpXVC1TaWduYXR1cmUtS2V5IiwidHlwIjoiSldUIn0.eyJzY3AiOiJlc2ktbWFya2V0cy5yZWFkX2NoYXJhY3Rlcl9vcmRlcnMudjEiLCJqdGkiOiI3YzNlZWY0Ni04NDEzLTQzNjUtOTQ2Yi03MWMzY2E2NGM4YTQiLCJraWQiOiJKV1QtU2lnbmF0dXJlLUtleSIsInN1YiI6IkNIQVJBQ1RFUjpFVkU6MjExNjUzNDAzMSIsImF6cCI6IjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwidGVuYW50IjoidHJhbnF1aWxpdHkiLCJ0aWVyIjoibGl2ZSIsInJlZ2lvbiI6IndvcmxkIiwiYXVkIjpbIjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwiRVZFIE9ubGluZSJdLCJuYW1lIjoiTGVuYSBHYWxsZW50Iiwib3duZXIiOiIxNHVkNGVFOHFSNGxmazFTenJRR2t4bnRPS2s9IiwiZXhwIjoxNzA3ODM3MDk4LCJpYXQiOjE3MDc4MzU4OTgsImlzcyI6Imh0dHBzOi8vbG9naW4uZXZlb25saW5lLmNvbSJ9.SYxW38EzMY-OC3fa8NwViRRXZluSk5Y66DkWFBhfMKhxAUZAmB_nyb6YTpYZvlX1dN9W4c6tVqHWnx_iNK32ujxUwesLDfRoCA7u3TlC4ZwqssVYNS4OpWW_fFugs2IT5n5N7ey0V4gyGkqbVw3rSzHiMjcRqbW5sCSfBWm3L-K111rkk0Og0sv0kJZV1v5ISqm6RrRLHQE0VD9zOc1iMOzRd28j2D8VWQhGSxQu96yJgG5Sy1yfPzj9PSKQGE-sU0hSqv2UMTY7wpq7xtnq3hFTeosI-eLf-KnlKfQOwDjxmY_zmFN9i7pQveY8qkHI2a6p1qjsRBzJEISPuWhAnA"





# Function to translate and add the type_id to the item list
def add_item_id_to_list(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as item_list_file:
        item_list = list(csv.reader(item_list_file))
    
    with open('item_name_id.csv', 'r', encoding='utf-8') as item_name_id_file:
        item_name_id_list = list(csv.reader(item_name_id_file))
    
    for item in item_list:
        item_name = item[0]
        item_already_has_id = False
        for row in item_name_id_list:
            if row[1] == item_name:
                if len(item) >= 2 and item[1]:  # Check if the second column already contains an ID
                    item_already_has_id = True
                    break
                else:
                    item.insert(1, row[0])  # Insert the type_id to the matching item at the correct position
                    print(f"Added type_id {row[0]} to item {item_name}")
                    break  # Stop searching once a match is found
        if not item_already_has_id:
            if len(item) < 2 or not item[1]:
                item.insert(1, "")  # If no ID was found, add an empty string to the second column at the correct position
                print(f"No type_id found for item {item_name}")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as item_list_file:
        writer = csv.writer(item_list_file)
        writer.writerows(item_list)



# Search for matching type_id in the CSV file
def get_type_id(item_name, csv_path):
    global type_id
    try:
        # Open the CSV file
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
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


# Function to temporarily save the sold items in a CSV file
def temporarily_store_item(csv_path, item_name, type_id, underbid_price):
    # Check if underbid_price is None
    if underbid_price is not None:
        # Open the CSV file in write mode and write the data
        with open(csv_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([item_name, type_id])



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
            underbid_price = second_cheapest_sell_price # Underbid the second cheapest
        else:
            underbid_price = cheapest_sell_price # Underbid the cheapest
        print(f"Price to underbid: {underbid_price}")
        return underbid_price
    else:
        print("Item is not profitable")
        underbid_price = None
        return None


#API: For setting up Buy orders: Check if item is still profitable and calculate price to buy
def is_item_profitable_to_buy(region, type_id, primary_system_id, secondary_system_id):
    global overbid_price
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
        # Determine the price to overbid
        if most_expensive_buy_price <= 1.1 * second_most_expensive_buy_price:
            overbid_price = most_expensive_buy_price 
        else:
            overbid_price = second_most_expensive_buy_price
        print(f"Price to overbid: {overbid_price}")
        return overbid_price
    else:
        print("Item is not profitable")
        overbid_price = None
        return None




# 1. Block to sell Items from Hangar------------------------------------------------------------------------------------------------------------------------

#read Inventory contents and get item name and quantity
def read_inventory_contents(csv_path):
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
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
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
            matched_item_name = difflib.get_close_matches(item_name, items_list, n=1, cutoff=0.9)  # Adjust cutoff as needed
            if matched_item_name:
                # Match found, proceeding with closest match
                print("Closest match found:", matched_item_name[0])
                item_name = matched_item_name[0]
            else:
                # Handle case when no match is found
                print("No matching Item found in the list.")
                item_name = None
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
        pyautogui.write(str(int(underbid_price)))
        #press key down to reduce the price by one
        pyautogui.press('down')
        #locate and click on the sell button
        sell_button_position = pyautogui.locateCenterOnScreen("Pictures\Sell_Button.PNG", confidence=.8)
        pyautogui.moveTo(sell_button_position, duration=.3)
        pyautogui.click(sell_button_position)

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





# 2. Block to set up buy orders------------------------------------------------------------------------------------------------------------------------

def get_characters_buy_orders(access_token):
    global active_buy_orders
    # Verify the access token and get the character ID
    verify_url = "https://esi.evetech.net/verify/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(verify_url, headers=headers)

    if response.status_code == 200:
        character_id = response.json()["CharacterID"]
        print("Character ID:", character_id)
    else:
        print("Error:", response.status_code)


    # Get the market orders for the character
    url = f"https://esi.evetech.net/latest/characters/{character_id}/orders/?datasource=tranquility"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}",
        "Cache-Control": "no-cache"
    }

    market_orders = requests.get(url, headers=headers)

    if market_orders.status_code == 200:
        market_data = market_orders.json()
        print(market_data)
    else:
        print("Error:", market_orders.status_code)

    # Filter out sell orders
    active_buy_orders = [order for order in market_data if order.get('is_buy_order')]
    return active_buy_orders


# Function to check what items to setup buy orders for
def setup_buy_orders(active_buy_orders, csv_path):
    # Read items list from CSV
    items_list = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            items_list.append(row)

    pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Regional_Market.PNG', confidence=0.7), duration=0.2)
    pyautogui.click()

    # Loop through each item in the items list
    for item in items_list:
        item_name, type_id = item[0], item[1]
        existing_buy_order = False

        # Check if there is an existing buy order for the item
        for order in active_buy_orders:
            if order.get('type_id') == int(type_id):
                existing_buy_order = True
                print(f"Skipping, buy order for {item_name} already exists.")
                break

        # If there is no existing buy order, set up one
        if not existing_buy_order:
            print(f"Try setting up buy order for {item_name}...")
            setup_buy_order(item_name, type_id)



# Function to set up buy order
def setup_buy_order(item_name, type_id):

    # Check if item is profitable to buy
    if is_item_profitable_to_buy(region, type_id, primary_system_id, secondary_system_id) is not None:
        # Set up buy order for the item
        print(f"Setting up buy order for {item_name}...")
        time.sleep(.4)
        

        # Search for the "Buy_Order_Search.PNG" picture on the screen
        search_position = pyautogui.locateCenterOnScreen('Pictures\Buy_Order_Search.PNG', confidence=0.7)
        pyautogui.moveTo(search_position.x + 220, search_position.y, duration=0.5)
        time.sleep(.2)
        pyautogui.click()
        pyautogui.write(item_name, interval=0.03)
        time.sleep(.1)
        pyautogui.press('enter')
        time.sleep(.1)
        info_icon_region = (search_position.x, search_position.y, 330, 200)
        
        try:
            info_icon = pyautogui.locateCenterOnScreen('Pictures\Info_Icon_Buy.PNG', region=info_icon_region, confidence=0.7)
        except:
            print("No info icon found, trying again...")
            pyautogui.moveTo(search_position.x, search_position.y + 30, duration=0.1)
            pyautogui.click()
            time.sleep(.2)
            
        info_icon = pyautogui.locateCenterOnScreen('Pictures\Info_Icon_Buy.PNG', region=info_icon_region, confidence=0.7)
        pyautogui.moveTo(info_icon.x - 20, info_icon.y, duration=0.1)
        pyautogui.leftClick()
        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Place_Buy_Order.PNG', confidence=0.7), duration=0.1)
        pyautogui.click()
        time.sleep(.8)
        bid_price = pyautogui.locateCenterOnScreen('Pictures\Bid_Price.PNG', confidence=0.7)
        pyautogui.moveTo(bid_price.x + 200, bid_price.y, duration=0.2)
        time.sleep(.1)
        pyautogui.doubleClick(interval=0.1)
        pyautogui.write(str(int(overbid_price)))
        time.sleep(.2)
        pyautogui.press('up')
        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Buy.PNG', confidence=0.8), duration=0.2)
        time.sleep(.1)
        pyautogui.click()

        print(f"Buy order for {item_name} has been set up.")

    else:
        print(f"Skipping, {item_name} is not profitable to buy.")




# 3. Block so update sell orders------------------------------------------------------------------------------------------------------------------------


def update_sell_orders():
    print("Updating Sell Orders")
    global old_item_name
    old_item_name = None
    
    selling_position = pyautogui.locateCenterOnScreen("Pictures\Selling.PNG", confidence=0.7)

    while True:  # Larger loop controlling the flow of the function
        loop_broken = False  # Flag to track whether any inner loop has broken
        
        # First loop
        for i in range(9):
            order_position = (selling_position.x + 300, selling_position.y + 52 + (25 * i)) # Click on the i order
            pyautogui.moveTo(order_position, duration=0.3)
            update_result = update_sell_order(csv_path)
            
            if update_result == "Item not found":
                print("Item not found, skipping...")
                continue
            elif update_result == "Completed":
                print("Breaking all Loops...")
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
                
            pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
            i + 1

        if loop_broken:
            break  # Exit the outer loop if the flag is True
        
        pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
        
        # Second loop
        while True:  # Infinite loop until the bottom of the page is reached
            pyautogui.press('down')
            pyautogui.moveTo(selling_position.x + 300, selling_position.y + 252, duration=0.2)

            update_result = update_sell_order(csv_path)
            if update_result == "Item not found":
                continue
            elif update_result == "Completed":
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
            pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
        
        if loop_broken:
            break  # Exit the outer loop if the flag is True



def update_sell_order(csv_path):
    global old_item_name
    global item_name
    pyautogui.rightClick()
    time.sleep(.2)
    try:
        modify_order = pyautogui.locateCenterOnScreen("Pictures\Modify_Order.PNG", confidence=0.8)
        print("modify order found")

    except:
        print("No more orders to modify") # Bottom of the page reached when there are few items
        return "Completed"


    # Click on modify order button
    pyautogui.moveTo(modify_order, duration=0.1)
    time.sleep(.1)
    pyautogui.click()
    time.sleep(.4)

    # Read item name
    type_position = pyautogui.locateCenterOnScreen("Pictures\Type.PNG", confidence=0.7) # Locate the type of item
    item_name = (int(type_position.x + 30), int(type_position.y - 33), 400, 25)
    item_name = pyautogui.screenshot(region=(item_name)) # Take a screenshot of the item name
    
    # Convert the screenshot to an opencv format
    item_name = cv2.cvtColor(np.array(item_name), cv2.COLOR_RGB2BGR)
    

    ocr_text = pytesseract.image_to_string(item_name, config="--psm 7 --oem 3") # Read the item name
    ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
    ocr_text = ocr_text.replace('@', '0')  # Replace @ with 0
    item_name = ocr_text.replace(' Il', ' II')  # Replace Il with II
    print("Processed item name: " + item_name)


    # Maybe add matching algorithm to find the closest item name in the list
    items_list = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            items_list.append(row[0])

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
            
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()

            print("Old item name: " + str(old_item_name))
            print("Item name: " + str(item_name))

            if old_item_name == item_name:
                print("Same item as last time, end of list reached.")
                return "Completed"
            else:
                old_item_name = item_name
                item_name = None
                return "Item not found"

    if old_item_name is not None and item_name == old_item_name:
        print("Same item as last time, end of list reached.")
        pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
        pyautogui.click()
        return "Completed"
    else:
        # Read old item price
        item_price_region = (int(type_position.x + 57), int(type_position.y + 50), 375, 25)
        item_price = pyautogui.screenshot(region=(item_price_region)) # Take a screenshot of the item price
        item_price = cv2.cvtColor(np.array(item_price), cv2.COLOR_RGB2BGR) # Convert the screenshot to an opencv format
        ocr_text = pytesseract.image_to_string(item_price, config="--psm 7 --oem 3") # Read the item price
        print("Raw item price: " + ocr_text)
        ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
        # Remove the ISK
        item_price = ocr_text.replace(' ISK', '').replace('.', '')
        # Remove comma and everything after the comma
        item_price = item_price.split(',')[0]
        print("Processed item price: " + item_price)
        item_price = int(item_price) # Convert the price to a integer
        
        # Calculate if item is profitable

        get_type_id(item_name, csv_path)
        print("Type ID: " + type_id)

        is_item_profitable_to_sell(region, type_id, primary_system_id, secondary_system_id)

        if underbid_price is not None: # Modify the order
            if item_price > underbid_price:
                print("I got underbid! Adjusting price...")
                pyautogui.write("{:,.0f}".format(underbid_price)) # Write the new price
                time.sleep(.2)
                pyautogui.press('down') # Lower the price
                pyautogui.press('enter') # Confirm the new price
                try:
                    time.sleep(.1)
                    pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Yes.PNG", confidence=0.7), duration=.3) # Locate the yes button
                    pyautogui.click()
                except:
                    print("No need to confirm")
                print(old_item_name)
                print(item_name)
                old_item_name = item_name
            else:
                pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                pyautogui.click()
                print("I am the cheapest, no need to modify the price. Skipping...")

        else:
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()
            print("Exiting at the bottom 2")
    




# 4. Block to update buy orders------------------------------------------------------------------------------------------------------------------------


def update_buy_orders():
    print("Updating Buy Orders")
    global old_item_name
    old_item_name = None
    
    buying_position = pyautogui.locateCenterOnScreen("Pictures\Buying.PNG", confidence=0.8)

    while True:  # Larger loop controlling the flow of the function
        loop_broken = False  # Flag to track whether any inner loop has broken
        
        # First loop
        for i in range(7):
            order_position = (buying_position.x + 300, buying_position.y + 52 + (25 * i)) # Click on the i order
            pyautogui.moveTo(order_position, duration=0.3)
            update_result = update_buy_order(csv_path)
            
            if update_result == "Item not found":
                print("Item not found, skipping...")
                continue
            elif update_result == "Completed":
                print("Breaking all Loops...")
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
                
            pyautogui.click(buying_position.x + 30, buying_position.y) # Click on Market Orders Tab
            i + 1

        if loop_broken:
            break  # Exit the outer loop if the flag is True
        
        pyautogui.click(buying_position.x + 30, buying_position.y) # Click on Market Orders Tab
        
        # Second loop
        while True:  # Infinite loop until the bottom of the page is reached
            pyautogui.press('down')
            pyautogui.moveTo(buying_position.x + 300, buying_position.y + 202, duration=0.2)

            update_result = update_buy_order(csv_path)
            if update_result == "Item not found":
                continue
            elif update_result == "Completed":
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
            pyautogui.click(buying_position.x + 30, buying_position.y) # Click on Market Orders Tab
        
        if loop_broken:
            break  # Exit the outer loop if the flag is True
    


def update_buy_order(csv_path):
    global old_item_name
    global item_name
    pyautogui.rightClick()
    time.sleep(.2)
    try:
        modify_order = pyautogui.locateCenterOnScreen("Pictures\Modify_Order.PNG", confidence=0.8)
        print("modify order found")

    except:
        print("No more orders to modify") # Bottom of the page reached when there are few items
        return "Completed"


    # Click on modify order button
    pyautogui.moveTo(modify_order, duration=0.1)
    time.sleep(.1)
    pyautogui.click()
    time.sleep(.4)

    # Read item name
    type_position = pyautogui.locateCenterOnScreen("Pictures\Type.PNG", confidence=0.7) # Locate the type of item
    item_name = (int(type_position.x + 30), int(type_position.y - 33), 400, 25)
    item_name = pyautogui.screenshot(region=(item_name)) # Take a screenshot of the item name
    
    # Convert the screenshot to an opencv format
    item_name = cv2.cvtColor(np.array(item_name), cv2.COLOR_RGB2BGR)
    

    ocr_text = pytesseract.image_to_string(item_name, config="--psm 7 --oem 3") # Read the item name
    ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
    ocr_text = ocr_text.replace('@', '0')  # Replace @ with 0
    item_name = ocr_text.replace(' Il', ' II')  # Replace Il with II
    print("Processed item name: " + item_name)


    # Maybe add matching algorithm to find the closest item name in the list
    items_list = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            items_list.append(row[0])

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
            
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()

            print("Old item name: " + str(old_item_name))
            print("Item name: " + str(item_name))

            if old_item_name == item_name:
                print("Same item as last time, end of list reached.")
                return "Completed"
            else:
                old_item_name = item_name
                item_name = None
                return "Item not found"

    if old_item_name is not None and item_name == old_item_name:
        print("Same item as last time, end of list reached.")
        pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
        pyautogui.click()
        return "Completed"
    else:
        # Read old item price
        print("Reading item price")
        item_price_region = (int(type_position.x + 57), int(type_position.y + 50), 375, 25)
        item_price = pyautogui.screenshot(region=(item_price_region)) # Take a screenshot of the item price
        item_price.save("itemprice.png")
        item_price = cv2.cvtColor(np.array(item_price), cv2.COLOR_RGB2BGR) # Convert the screenshot to an opencv format
        ocr_text = pytesseract.image_to_string(item_price, config="--psm 7 --oem 3") # Read the item price
        print("Raw item price: " + ocr_text)
        ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
        # Remove the ISK
        item_price = ocr_text.replace(' ISK', '').replace('.', '')
        # Remove comma and everything after the comma
        item_price = item_price.split(',')[0]
        print("Processed item price: " + item_price)
        item_price = int(item_price) # Convert the price to a integer
        
        # Calculate if item is profitable

        get_type_id(item_name, csv_path)
        print("Type ID: " + type_id)

        is_item_profitable_to_buy(region, type_id, primary_system_id, secondary_system_id)

        if overbid_price is not None: # Modify the order
            if item_price < overbid_price:
                print("I got underbid! Adjusting price...")
                pyautogui.write("{:,.0f}".format(overbid_price)) # Write the new price
                time.sleep(.2)
                pyautogui.press('up') # Lower the price
                pyautogui.press('enter') # Confirm the new price
                try:
                    time.sleep(.1)
                    pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Yes.PNG", confidence=0.7), duration=.3) # Locate the yes button
                    pyautogui.click()
                except:
                    print("No need to confirm")
                print(old_item_name)
                print(item_name)
                old_item_name = item_name
            else:
                pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                pyautogui.click()
                print("I am on top, no need to modify the price. Skipping...")

        else:
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()
            print("Exiting at the bottom 2")



    # Set path to .CSV file for normal operation
    csv_path = "Item_List.csv"

    add_item_id_to_list(csv_path)





# 5. Block Sell items and setup buy orders for them-------------------------------------------------------------------------------------------------------
    
# Sell and set up buy orders
def sell_and_buy():

    # Set path to .CSV file
    csv_path = "sold_items.csv"

    # Clear the sold_items.csv file
    open('sold_items.csv', 'w').close()

    while True:

        if read_inventory_contents(csv_path) == "Z_Not_Profitable Detected":

            print("End of list reached")
            break

        elif item_name is not None:
            get_type_id(item_name, csv_path)
            #check if item is profitable
            is_item_profitable_to_sell(region, type_id, primary_system_id, secondary_system_id)
            sell_or_store_item(underbid_price, item_quantity, inventory_taskbar_position)
            temporarily_store_item(csv_path, item_name, type_id, underbid_price)

        else:
            move_item_to_container()

    # Just set active buy orders to Plex as it is not needed
    active_buy_orders = [{'duration': 90, 'escrow': 1.01, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T11:28:27Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712360599, 'price': 1.01, 'range': 'station', 'region_id': 10000002, 'type_id': 29668, 'volume_remain': 1, 'volume_total': 1}]

    time.sleep(3)
    csv_path = "sold_items.csv"
    setup_buy_orders(active_buy_orders, csv_path)








# Main Loop:------------------------------------------------------------------------------------------------------------------------------------------------





# Set path to .CSV file for normal operation
csv_path = "Item_List.csv"

add_item_id_to_list(csv_path)


while True:

    if read_inventory_contents(csv_path) == "Z_Not_Profitable Detected":

        print("End of list reached")
        break

    elif item_name is not None:
        get_type_id(item_name, csv_path)
        #check if item is profitable
        is_item_profitable_to_sell(region, type_id, primary_system_id, secondary_system_id)
        sell_or_store_item(underbid_price, item_quantity, inventory_taskbar_position)

    else:
        move_item_to_container()


time.sleep(3)
get_characters_buy_orders(access_token)


setup_buy_orders(active_buy_orders, csv_path)


try:
    while True:
        csv_path = "Item_List.csv"
        # Wait for 5 minutes before updating the orders
        time.sleep(260)

        print("Starting in 40s...")

        time.sleep(40)

        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Market_Orders.PNG', confidence=0.7), duration=0.2)
        pyautogui.click()

        update_sell_orders()


        update_buy_orders()

        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Inventory_Deactivated.PNG', confidence=0.7), duration=0.2)
        pyautogui.click()
        time.sleep(1)


        sell_and_buy()

        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Inventory_Deactivated.PNG', confidence=0.7), duration=0.2)
        pyautogui.click()

except KeyboardInterrupt:
    print("Bot stopped by user")


