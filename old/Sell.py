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


# Search for matching type_id in the CSV file
def get_type_id(update_name):
    global type_id
    try:
        # Open the CSV file
        with open("Item_List.csv", newline='', encoding='utf-8') as csvfile:
            # Read the CSV file
            reader = csv.reader(csvfile)
            # Iterate through each row
            for row in reader:
                # Check if the item name matches the name in the first column
                if row[0] == update_name:
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
            update_result = update_sell_order()
            
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

            update_result = update_sell_order()
            if update_result == "Item not found":
                continue
            elif update_result == "Completed":
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
            pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
        
        if loop_broken:
            break  # Exit the outer loop if the flag is True








def update_sell_order():
    global old_item_name
    global update_name
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
    update_name = (int(type_position.x + 30), int(type_position.y - 33), 400, 25)
    update_name = pyautogui.screenshot(region=(update_name)) # Take a screenshot of the item name
    
    # Convert the screenshot to an opencv format
    update_name = cv2.cvtColor(np.array(update_name), cv2.COLOR_RGB2BGR)
    

    ocr_text = pytesseract.image_to_string(update_name, config="--psm 7 --oem 3") # Read the item name
    ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
    ocr_text = ocr_text.replace('@', '0')  # Replace @ with 0
    update_name = ocr_text.replace(' Il', ' II')  # Replace Il with II
    print("Processed item name: " + update_name)


    # Maybe add matching algorithm to find the closest item name in the list
    items_list = []
    with open('Item_List.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            items_list.append(row[0])

    if update_name in items_list:
            #Proceed with exact matched item
            print("Exact match found:", update_name)
    else:
        # Trying to find the closest match
        matched_item_name = difflib.get_close_matches(update_name, items_list, n=1, cutoff=0.8)  # Adjust cutoff as needed
        if matched_item_name:
            # Match found, proceeding with closest match
            print("Closest match found:", matched_item_name[0])
            update_name = matched_item_name[0]
        else:
            # Handle case when no match is found
            print("No matching Item found in the list.")
            
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()

            print("Old item name: " + str(old_item_name))
            print("Item name: " + str(update_name))

            if old_item_name == update_name:
                print("Same item as last time, end of list reached.")
                return "Completed"
            else:
                old_item_name = update_name
                update_name = None
                return "Item not found"

    if old_item_name is not None and update_name == old_item_name:
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

        get_type_id(update_name)
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
                print(update_name)
                old_item_name = update_name
            else:
                pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                pyautogui.click()
                print("I am the cheapest, no need to modify the price. Skipping...")

        else:
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()
            print("Exiting at the bottom 2")
    









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
            update_result = update_buy_order()
            
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

            update_result = update_buy_order()
            if update_result == "Item not found":
                continue
            elif update_result == "Completed":
                loop_broken = True  # Set flag to True if the inner loop breaks
                break  # Exit the inner loop
                
            pyautogui.click(buying_position.x + 30, buying_position.y) # Click on Market Orders Tab
        
        if loop_broken:
            break  # Exit the outer loop if the flag is True
    





def update_buy_order():
    global old_item_name
    global update_name
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
    update_name = (int(type_position.x + 30), int(type_position.y - 33), 400, 25)
    update_name = pyautogui.screenshot(region=(update_name)) # Take a screenshot of the item name
    
    # Convert the screenshot to an opencv format
    update_name = cv2.cvtColor(np.array(update_name), cv2.COLOR_RGB2BGR)
    

    ocr_text = pytesseract.image_to_string(update_name, config="--psm 7 --oem 3") # Read the item name
    ocr_text = ocr_text.strip() # Remove leading and trailing whitespaces
    ocr_text = ocr_text.replace('@', '0')  # Replace @ with 0
    update_name = ocr_text.replace(' Il', ' II')  # Replace Il with II
    print("Processed item name: " + update_name)


    # Maybe add matching algorithm to find the closest item name in the list
    items_list = []
    with open('Item_List.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            items_list.append(row[0])

    if update_name in items_list:
            #Proceed with exact matched item
            print("Exact match found:", update_name)
    else:
        # Trying to find the closest match
        matched_item_name = difflib.get_close_matches(update_name, items_list, n=1, cutoff=0.8)  # Adjust cutoff as needed
        if matched_item_name:
            # Match found, proceeding with closest match
            print("Closest match found:", matched_item_name[0])
            update_name = matched_item_name[0]
        else:
            # Handle case when no match is found
            print("No matching Item found in the list.")
            
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()

            print("Old item name: " + str(old_item_name))
            print("Item name: " + str(update_name))

            if old_item_name == update_name:
                print("Same item as last time, end of list reached.")
                return "Completed"
            else:
                old_item_name = update_name
                update_name = None
                return "Item not found"

    if old_item_name is not None and update_name == old_item_name:
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

        get_type_id(update_name)
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
                print(update_name)
                old_item_name = update_name
            else:
                pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                pyautogui.click()
                print("I am on top, no need to modify the price. Skipping...")

        else:
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()
            print("Exiting at the bottom 2")


















time.sleep(3)

#update_sell_orders()
update_buy_orders()