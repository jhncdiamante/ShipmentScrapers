from Driver.MaskedUserAgentDriver import MaskedUserAgentDriver
from Driver.NormalDriver import NormalDriver
from Maersk.MaerskSearchBar import MaerskSearchBar
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from CookiesManager.CookieHandler import CookieHandler
from Website.TrackingWebsite import TrackingWebsite
from Maersk.MaerskShipment import MaerskShipmentScraper
from Maersk.ContainerScraper import MaerskContainerScraper
from Maersk.MilestoneScraper import MaerskMilestoneScraper
from Database.CSVDatabase import CSVDatabase
from selenium.webdriver.common.by import By
from Date.ScrapeTime import ScrapeTime
from Helpers.logging_config import setup_logger
import pandas as pd
import time, random

import os
os.makedirs("Maersk/Errors", exist_ok=True)


# Setup logger for this module
logger = setup_logger()

MAERSK_TRACKING_URL = "https://www.maersk.com/tracking/"
INPUT_FILE_PATH = r"D:\vscode\Maersk\OUTPUT.csv"
OUTPUT_FILE_PATH = r"MAERSK_TEST_DRIVE(1).csv"


if INPUT_FILE_PATH.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx"):
    df = pd.read_excel(INPUT_FILE_PATH)


# Convert the first column to a list of BL numbers
BILL_OF_LADING_NUMBERS = df.iloc[:, 0].dropna().unique().tolist()
maersk_driver_handle = NormalDriver()
maersk_driver_handle.set_up_driver()
maersk_driver = maersk_driver_handle.driver
maersk_driver.maximize_window()

search_bar = MaerskSearchBar(maersk_driver, (By.CSS_SELECTOR, "mc-input#track-input"))
search_button = Button(
    (By.CLASS_NAME, "track__search__button"), maersk_driver
)
search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
allow_button = Button(
    (By.CSS_SELECTOR, "button[data-test='coi-allow-all-button']"),
    maersk_driver
)
cookie_handler = CookieHandler(maersk_driver, allow_cookies_button=allow_button)
scrape_time = ScrapeTime()

maersk = TrackingWebsite(
    MAERSK_TRACKING_URL,
    maersk_driver,
    search_feature,
    cookie_handler,
    shipment_scraper=MaerskShipmentScraper,
    container_scraper=MaerskContainerScraper,
    milestone_scraper=MaerskMilestoneScraper,
    scrape_time=scrape_time,
)
csv_observer = CSVDatabase(OUTPUT_FILE_PATH)
maersk.attach(csv_observer)

maersk.open()

to_track = BILL_OF_LADING_NUMBERS.copy()

while to_track:
    bl = to_track.pop(0)

    try:
        maersk.track_shipment(bl)
        time.sleep(random.randint(3, 5))
    except Exception as e:
        maersk_driver.save_screenshot(f"Errors/{bl}_error.png")
        to_track.append(bl)  # retry later
        time.sleep(3) 

maersk.close()
print("Successfully tracked all shipments.✔")
