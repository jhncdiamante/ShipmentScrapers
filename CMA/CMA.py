from Driver.NormalDriver import NormalDriver
from Search.SearchBar import SearchBar
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from CookiesManager.NoCookieHandler import NoCookieHandler
from Website.TrackingWebsite import TrackingWebsite
from CMA.CMAContainerEvaluator import smart_container_scraper_factory
from CMA.CMAMilestoneScraper import CMAMilestoneScraper
from CMA.CMAShipmentScraper import CMAShipmentScraper
from Database.CSVDatabase import CSVDatabase
from selenium.webdriver.common.by import By
from Date.ScrapeTime import ScrapeTime
import pandas as pd
import random

INPUT_FILE_PATH = r"D:\VersionClient\ShipmentScrapers\2025-23 CMA Outputv2.csv" # First column must contain the Bill of Lading numbers
OUTPUT_FILE_PATH = r"CMA_TEST_DRIVE(2).csv" 

if INPUT_FILE_PATH.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx"):
    df = pd.read_excel(INPUT_FILE_PATH)

CMA_CGM_URL = "https://www.cma-cgm.com/ebusiness/tracking/search"

# Convert the first column to a list of BL numbers
BILL_OF_LADING_NUMBERS = df.iloc[:, 0].dropna().unique().tolist()

cma_driver_handle = NormalDriver() 
cma_driver_handle.set_up_driver() # WARNING: Do not mask, modify, or rotate driver's original headers, it will trigger the captcha of CMA website
cma_driver = cma_driver_handle.driver
cma_driver.maximize_window()

search_bar = SearchBar(cma_driver, (By.ID, "Reference"))
search_button = Button((By.ID, "btnTracking"), cma_driver)
search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
cookie_handler = NoCookieHandler() # No 'cookies permission' pop-up in website
scrape_time = ScrapeTime()

cma = TrackingWebsite(
    CMA_CGM_URL,
    driver=cma_driver,
    search_feature=search_feature,
    cookie_handler=cookie_handler,
    shipment_scraper_factory=CMAShipmentScraper,
    container_scraper_factory=smart_container_scraper_factory,
    milestone_scraper_factory=CMAMilestoneScraper,
    scrape_time=scrape_time,
)

csv_database = CSVDatabase(OUTPUT_FILE_PATH)
cma.attach(csv_database) # you can attach multiple databases, as long as in accordance on the subject's data format
cma.open()

random.shuffle(BILL_OF_LADING_NUMBERS)
for bl in ["GHC0311167A"
]: 
    cma.track_shipment(bl)
