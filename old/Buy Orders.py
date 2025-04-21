import requests
import csv
import pyautogui
import time
import cv2
import pytesseract
import numpy as np


region = "10000002"
type_id = "2456"
secondary_system_id = "30000144" #cheap trade hub perimeter
primary_system_id = "30000142" #main trade hub jita
access_token = "eyJhbGciOiJSUzI1NiIsImtpZC********************************************************************************************************************JjYjE2NzhkOC02MDNmLTRlMDktYjVjYS03NjE3NzE3MDhhZmIiLCJraWQiOiJKV1QtU2lnbmF0dXJlLUtleSIsInN1YiI6IkNIQVJBQ1RFUjpFVkU6MjExNjUzNDAzMSIsImF6cCI6IjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwidGVuYW50IjoidHJhbnF1aWxpdHkiLCJ0aWVyIjoibGl2ZSIsInJlZ2lvbiI6IndvcmxkIiwiYXVkIjpbIjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwiRVZFIE9ubGluZSJdLCJuYW1lIjoiTGVuYSBHYWxsZW50Iiwib3duZXIiOiIxNHVkNGVFOHFSNGxmazFTenJRR2t4bnRPS2s9IiwiZXhwIjoxNzA3Nzc0MDczLCJpYXQiOjE3MDc3NzI4NzMsImlzcyI6Imh0dHBzOi8vbG9naW4uZXZlb25saW5lLmNvbSJ9.D9qCuW0j_zxevYPABvhz9hLE0QSGZIVSPSj0pzmtcvlwt9p2GaFFrionabkH7OK2l5ET_B24SmVX3MdPwBjpaeNcJ73uM3XyUFAbga2rUD6bG5NBJbzDaT7EHGj3tR8Byta7OmgR3J6d01uYmVouwmk8OhovPrV4QLkBbVoVmHOZ_13b2Uf5SKODqtKM64a-W74l2Z6or85bD2Wz8RTHiYQJa02P0GAN5ND5gaI948dUNq61i_E5Fo8i0lHi7cr8FEMYjr9fgTKtbFfiOIlN8e6A0UQfS4SIe9-vkkoWyq5ZateZDVvQiQ_fIRyLUJtvzIj5IsCv0mN1dH5aAnQIEw"

# Function to translate and add the type_id to the item list
def add_item_id_to_list():
    with open('Item_List.csv', 'r', encoding='utf-8') as item_list_file:
        item_list = list(csv.reader(item_list_file))
    
    with open('item_name_id.csv', 'r', encoding='utf-8') as item_name_id_file:
        item_name_id_list = list(csv.reader(item_name_id_file))
    
    for item in item_list:
        item_name = item[0]
        item_already_has_id = False
        for row in item_name_id_list:
            if row[1] == item_name:
                if len(item) >= 2:  # Check if the second column already contains an ID
                    item_already_has_id = True
                    break
                else:
                    item.append(row[0])  # Add the type_id to the matching item
                    print(f"Added type_id {row[0]} to item {item_name}")
                    break  # Stop searching once a match is found
        if not item_already_has_id:
            item.append("")  # If no ID was found, add an empty string to the second column
            print(f"No type_id found for item {item_name}")
    
    with open('Item_List.csv', 'w', newline='', encoding='utf-8') as item_list_file:
        writer = csv.writer(item_list_file)
        writer.writerows(item_list)





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
def setup_buy_orders(active_buy_orders):
    # Read items list from CSV
    items_list = []
    with open('Item_List.csv', newline='', encoding='utf-8') as csvfile:
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
            

# Placeholder function to set up buy order
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
        pyautogui.write(item_name, interval=0.1)
        time.sleep(.2)
        pyautogui.press('enter')
        time.sleep(.5)
        info_icon_region = (search_position.x, search_position.y, 300, 200)
        
        try:
            info_icon = pyautogui.locateCenterOnScreen('Pictures\Info_Icon_Buy.PNG', region=info_icon_region, confidence=0.7)
        except:
            print("No info icon found, trying again...")
            pyautogui.moveTo(search_position.x, search_position.y + 30, duration=0.2)
            pyautogui.click()
            time.sleep(.5)
            
        info_icon = pyautogui.locateCenterOnScreen('Pictures\Info_Icon_Buy.PNG', region=info_icon_region, confidence=0.7)
        pyautogui.leftClick(info_icon.x - 20, info_icon.y, duration=0.5)
        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Place_Buy_Order.PNG', confidence=0.7))
        pyautogui.click()
        time.sleep(.8)
        bid_price = pyautogui.locateCenterOnScreen('Pictures\Bid_Price.PNG', confidence=0.7)
        pyautogui.moveTo(bid_price.x + 200, bid_price.y, duration=0.5)
        time.sleep(.2)
        pyautogui.doubleClick(interval=0.1)
        pyautogui.write("{:,.0f}".format(overbid_price))
        time.sleep(.2)
        pyautogui.press('up')
        pyautogui.moveTo(pyautogui.locateCenterOnScreen('Pictures\Buy.PNG', confidence=0.8), duration=0.2)
        time.sleep(.1)
        pyautogui.click()

        print(f"Buy order for {item_name} has been set up.")

    else:
        print(f"Skipping, {item_name} is not profitable to buy.")
    
    
    
    
active_buy_orders = [{'duration': 90, 'escrow': 1.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-08T15:24:30Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6710971292, 'price': 1.0, 'range': 'station', 'region_id': 10000002, 'type_id': 25605, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 1.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T11:28:05Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712360435, 'price': 1.0, 'range': 'station', 'region_id': 10000002, 'type_id': 11578, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 1.01, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T11:28:27Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712360599, 'price': 1.01, 'range': 'station', 'region_id': 10000002, 'type_id': 20353, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 100.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T11:31:35Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712362107, 'price': 100.0, 'range': 'station', 'region_id': 10000002, 'type_id': 74386, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 350300.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T14:48:13Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712501237, 'price': 350300.0, 'range': 'station', 'region_id': 10000002, 'type_id': 9287, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 350400.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T14:58:26Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712508629, 'price': 350400.0, 'range': 'station', 'region_id': 10000002, 'type_id': 9287, 'volume_remain': 1, 'volume_total': 1}, {'duration': 90, 'escrow': 350500.0, 'is_buy_order': True, 'is_corporation': False, 'issued': '2024-02-10T15:04:45Z', 'location_id': 60003760, 'min_volume': 1, 'order_id': 6712513213, 'price': 350500.0, 'range': 'station', 'region_id': 10000002, 'type_id': 9287, 'volume_remain': 1, 'volume_total': 1}]
    
time.sleep(3)
#add_item_id_to_list()
#get_characters_buy_orders(access_token)
setup_buy_orders(active_buy_orders)