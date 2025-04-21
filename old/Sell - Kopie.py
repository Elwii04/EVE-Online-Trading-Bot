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
def is_item_profitable(region, type_id, primary_system_id, secondary_system_id):
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





def update_sell_orders():
    print("Updating Sell Orders")
    old_item_name = None
    
    selling_position = pyautogui.locateCenterOnScreen("Pictures\Selling.PNG", confidence=0.7)

    while True:  # Infinite loop until the bottom of the page is reached
        

        for i in range(9):

            order_position = (selling_position.x + 300, selling_position.y + 52 + (25 * i)) # Click on the i order
            pyautogui.moveTo(order_position, duration=0.3)
            if update_sell_order() is not None:
                pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
                i + 1
            else:
                pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
                break

        else:
            break
    

        pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
        
        while True:  # Infinite loop until the bottom of the page is reached
            pyautogui.press('down')
            pyautogui.moveTo(selling_position.x + 300, selling_position.y + 252, duration=0.2)

            if update_sell_order() is None:
                break

            pyautogui.click(selling_position.x + 30, selling_position.y) # Click on Market Orders Tab
        else:
            break

        break









def update_sell_order():
    global old_item_name
    global item_name
    pyautogui.rightClick()
    time.sleep(.2)
    try:
        modify_order = pyautogui.locateCenterOnScreen("Pictures\Modify_Order.PNG", confidence=0.8)
        print("modify order found")

    except:
        print("No more orders to modify") # Bottom of the page reached when there are few items
        return None


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
    with open('Item_List.csv', newline='', encoding='utf-8') as csvfile:
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


            if old_item_name is not None:
                if item_name == old_item_name:
                    print("Same item as last time, end of list reached.")
                    pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                    pyautogui.click()
                    return None
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

                get_type_id(item_name)
                print("Type ID: " + type_id)

                is_item_profitable(region, type_id, primary_system_id, secondary_system_id)

                if underbid_price is not None: # Modify the order
                    if item_price > underbid_price:
                        print("I got underbid! Adjusting price...")
                        pyautogui.write("{:,.0f}".format(underbid_price)) # Write the new price
                        time.sleep(.2)
                        pyautogui.press('down') # Lower the price
                        pyautogui.press('enter') # Confirm the new price
                        print(old_item_name)
                        print(item_name)
                        old_item_name = item_name

                else:
                    pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
                    pyautogui.click()



        else:
            # Handle case when no match is found
            print("No matching Item found in the list.")
            old_item_name = item_name
            print("Old item Name: " + old_item_name)
            pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Cancel.PNG", confidence=0.7), duration=.3) # Locate the cancel button
            pyautogui.click()




    




    
    









#locate the market orders tab
#pyautogui.moveTo(pyautogui.locateCenterOnScreen("Pictures\Market_Orders.PNG", confidence=0.7), duration=0.3) # Activate the market orders tab
#pyautogui.click()

time.sleep(3)

update_sell_orders()