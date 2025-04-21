# EVE Online Trading Bot

**Disclaimer:** This project was developed as a first venture into Python programming. The primary goal was learning, and as such, the code may not follow best practices, might contain inefficiencies, or could be considered "bad" by experienced developers. It's shared as a demonstration of the learning process. Use at your own risk.

## Overview

This Python script fully automates station trading within the game EVE Online. It interacts with the game's UI using GUI automation and OCR, and fetches market data using the EVE Swagger Interface (ESI) API.

The bot aims to:
*   Sell items from the player's inventory based on profitability.
*   Set up buy orders for desired items.
*   Update existing sell and buy orders to remain competitive.
*   Combine selling and setting up corresponding buy orders.

**Warning:** Using bots or automation tools in EVE Online might be against the game's Terms of Service and could lead to account suspension. Use this script responsibly and understand the risks involved.

## Features

*   **Inventory Management:** Reads item names and quantities directly from the game's inventory window using OCR.
*   **Profitability Checks:** Uses ESI API calls to compare sell and buy orders in specified regions/systems to determine if selling or buying an item is profitable based on predefined criteria (e.g., sell price > 1.3 * buy price).
*   **Automated Selling:** If an item is deemed profitable to sell, the bot automates the process of listing it on the market, underbidding the current cheapest sell order according to specific logic.
*   **Automated Buying:** Sets up buy orders for items from a list, checking profitability and overbidding the current highest buy order based on defined rules.
*   **Order Updates:** Periodically checks existing sell and buy orders, modifying prices to underbid/overbid competitors if necessary.
*   **Item Name Matching:** Uses fuzzy matching (`difflib`) to handle potential inaccuracies in OCR text recognition.
*   **Configuration:** Uses CSV files for item lists and stores configuration variables directly in the script.

## Prerequisites

*   **Python 3.x:** [Download Python](https://www.python.org/downloads/)
*   **Tesseract OCR:** Needs to be installed and accessible in your system's PATH. [Tesseract Installation Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
*   **EVE Online Client:** The game itself.

## Installation

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/Elwii04/EVE-Online-Trading-Bot.git
    cd EVE-Online-Trading-Bot
    ```
2.  **Install required Python libraries:**
    ```bash
    pip install pyautogui opencv-python pytesseract numpy requests pygetwindow difflib-python
    ```
    *(You might need `pip install Pillow` as well, as `pyautogui` often depends on it)*

## Configuration

### 1. In-Game Settings (Required)

*   **Resolution:** 1600 x 900
*   **Display Mode:** Fixed Window
*   **Language:** English

### 2. Window Layout (Required)

Arrange the EVE Online client windows (Inventory, Market Orders, Regional Market) precisely as shown in the `EVE Window Screenshot.png` file included in the repository. The bot relies heavily on specific screen coordinates.

![EVE Window Screenshot](EVE%20Window%20Screenshot.png) *(Assuming this file exists in the repo)*

### 3. Script Settings (`Bot Final.py`)

Open `Bot Final.py` and modify the following variables near the beginning:

*   `region`: The EVE Online region ID for market operations (e.g., `"10000002"` for The Forge).
*   `secondary_system_id`: The system ID for the secondary trade hub (e.g., `"30000144"` for Perimeter).
*   `primary_system_id`: The system ID for the main trade hub (e.g., `"30000142"` for Jita).
*   `access_token`: **Crucial:** You need to obtain an ESI access token with the scope `esi-markets.read_character_orders.v1`. Replace the placeholder token with your actual token. You can generate one using third-party ESI helper tools or by setting up your own ESI application. **Keep this token secure!**
*   `csv_path`: Ensure this points to your item list file (default is `"Item_List.csv"`).
*   **Tesseract Path (If needed):** If Tesseract isn't in your system PATH, you might need to specify its location within the script where `pytesseract` is called (e.g., `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`).

### 4. Item List (`Item_List.csv`)

*   Create or edit the `Item_List.csv` file.
*   Add the **exact in-game names** of the items you want the bot to trade, one item name per line in the first column.
*   The script will automatically attempt to find and add the corresponding `type_id` to the second column using the included `item_name_id.csv` file when it first runs the `add_item_id_to_list` function. Ensure `item_name_id.csv` is present and contains a comprehensive list of item names and their IDs.

Example `Item_List.csv`:
```csv
Tritanium
Pyerite
Mexallon
"Veldspar"
"Scordite"
```
*(Note: Use quotes if item names contain commas)*

## Usage

1.  Ensure all configuration steps are completed (In-Game Settings, Window Layout, Script Settings, Item List).
2.  Log into EVE Online and set up the windows as required.
3.  Run the Python script from your terminal:
    ```bash
    python "Bot Final.py"
    ```
4.  The bot will start executing its main loop:
    *   Initially, it processes items in your main inventory hangar.
    *   Then, it sets up initial buy orders.
    *   After that, it enters a loop to periodically update sell and buy orders, and potentially perform the sell-and-buy routine.
5.  **To stop the bot:** Press `Ctrl + C` in the terminal where the script is running.

## How It Works

1.  **GUI Automation (`pyautogui`):** Clicks buttons, types text, drags items, and moves the mouse based on locating predefined images (`Pictures/*.PNG`) on the screen.
2.  **OCR (`pytesseract`, `cv2`):** Takes screenshots of specific screen regions (e.g., inventory lines, market order details), preprocesses the image (`cv2`), and extracts text (`pytesseract`) to read item names, quantities, and prices.
3.  **ESI API (`requests`):** Fetches current market buy and sell orders for specific item `type_id`s in the configured region and systems. It uses the provided access token for character-specific order data.
4.  **Logic:** Combines OCR data and ESI data to make decisions about selling, buying, and updating orders based on the profitability logic defined in the `is_item_profitable_to_sell` and `is_item_profitable_to_buy` functions.
5.  **Data Handling (`csv`):** Reads the target item list and writes temporary data (like items just sold).

## Dependencies

*   [pyautogui](https://pyautogui.readthedocs.io/en/latest/)
*   [opencv-python](https://pypi.org/project/opencv-python/)
*   [pytesseract](https://pypi.org/project/pytesseract/)
*   [numpy](https://numpy.org/)
*   [requests](https://requests.readthedocs.io/en/latest/)
*   [pygetwindow](https://pypi.org/project/PyGetWindow/)
*   [difflib](https://docs.python.org/3/library/difflib.html) (Standard Library)
*   [Pillow](https://python-pillow.org/) (Often a dependency for pyautogui/screenshot functions)
