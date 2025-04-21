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
access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkpXVC1TaWduYXR1cmUtS2V5IiwidHlwIjoiSldUIn0.eyJzY3AiOiJlc2ktbWFya2V0cy5yZWFkX2NoYXJhY3Rlcl9vcmRlcnMudjEiLCJqdGkiOiI0NmQyZjQ3YS05ZGMzLTRlYWMtOTk5Yi1mY2UxZDY5MjU0OTciLCJraWQiOiJKV1QtU2lnbmF0dXJlLUtleSIsInN1YiI6IkNIQVJBQ1RFUjpFVkU6MjExNjUzNDAzMSIsImF6cCI6IjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwidGVuYW50IjoidHJhbnF1aWxpdHkiLCJ0aWVyIjoibGl2ZSIsInJlZ2lvbiI6IndvcmxkIiwiYXVkIjpbIjY4MzA4NGFiNWY4ODQ4ZDRiMTg3NDYyYWMzYjk3Njc3IiwiRVZFIE9ubGluZSJdLCJuYW1lIjoiTGVuYSBHYWxsZW50Iiwib3duZXIiOiIxNHVkNGVFOHFSNGxmazFTenJRR2t4bnRPS2s9IiwiZXhwIjoxNzA3Nzc1MzU4LCJpYXQiOjE3MDc3NzQxNTgsImlzcyI6Imh0dHBzOi8vbG9naW4uZXZlb25saW5lLmNvbSJ9.PBKt22SmWeUPQtghVJimKrTsXg3yvmqDPKkqcUC3pYZy8wcgd9-OpTsIzRNBTEgphWlZ6MnKg5qdnzFGK1UgIkO9ZfDpvFWd2zCBDNanRIuGmMn0s2gZeggqm1E7IXKNMrlmQ2T7y00CGHRzfqLXFe2g8_mn5WMTEZA1psE9gIedt5lriQKWEPpfP356BImMWdMdoDxsHwVkN3iLXHRkC2hvdRxbyzalMum3ZYaEb9GaZvEDcStThr21-7zOCgglUB6bnbIDWucLo0IoEcVXL19B9FaZHZS2PDJNK9_WCuwjrCd11Zy92ehyN-NqlBf0HWE73kbIRlUO7pxyFQnrZw"
csv_path = 'Item_List.csv'




def sell_and_buy():
    
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