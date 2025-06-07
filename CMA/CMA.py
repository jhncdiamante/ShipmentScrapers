from Driver.NormalDriver import NormalDriver
from Search.SearchBar import SearchBar
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from CookiesManager.NoCookieHandler import NoCookieHandler
from Website.TrackingWebsite import TrackingWebsite
from CMA.CMAContainerEvaluator import smart_container_scraper_factory
from CMA.CMAMilestoneScraper import CMAMilestoneScraper
from CMA.CMAShipmentScraper import CMAShipmentScraper
from Database.CSVDatabase import CsvObserver
from selenium.webdriver.common.by import By
from Date.ScrapeTime import ScrapeTime
import pandas as pd
import time, random

INPUT_FILE_PATH = r"CMA_OUTPUT.csv"
OUTPUT_FILE_PATH = r"CMA_OUTPUT.csv"
if INPUT_FILE_PATH.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx"):
    df = pd.read_excel(INPUT_FILE_PATH)
    
# Convert the first column to a list of BL numbers
first_col_list = df.iloc[:, 0].dropna().unique().tolist()

cma_driver_handle = NormalDriver()
cma_driver_handle.set_up_driver()
cma_driver = cma_driver_handle.driver 

search_bar = SearchBar(cma_driver, (By.ID, "Reference")) 
search_button = Button((By.ID, "btnTracking"), cma_driver)
search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
cookie_handler = NoCookieHandler()
scrape_time = ScrapeTime()
maersk = TrackingWebsite("https://www.cma-cgm.com/ebusiness/tracking/search", cma_driver, search_feature, cookie_handler,
                            shipment_scraper_factory=CMAShipmentScraper,
                            container_scraper_factory=smart_container_scraper_factory,
                            milestone_scraper_factory=CMAMilestoneScraper,
                            scrape_time=scrape_time)
csv_observer = CsvObserver(OUTPUT_FILE_PATH)
maersk.attach(csv_observer)
maersk.open()

for i in ["SGN2621243"]:
    maersk.track_shipment(i)
    time.sleep(3, 8)