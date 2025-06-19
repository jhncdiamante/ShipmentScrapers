from Driver.MaskedUserAgentDriver import MaskedUserAgentDriver
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from selenium.webdriver.common.by import By
from Search.SearchBar import SearchBar
from CookiesManager.NoCookieHandler import NoCookieHandler
from Date.ScrapeTime import ScrapeTime
from OneEcomm.OneShipmentScraper import OneShipmentScraper
from OneEcomm.OneContainerScraper import OneContainerScraper
from OneEcomm.OneMilestoneScraper import OneMilestoneScraper
from Database.CSVDatabase import CSVDatabase
from OneEcomm.OneWebsite import OneWebsite
import pandas as pd

INPUT_FILE_PATH = r"D:\vscode\EcommOne\INPUT.csv"
OUTPUT_FILE_PATH = r"ONE_TEST_DRIVE(1).csv"
ONE_ECOMM_TRACKING_URL = "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking"

if INPUT_FILE_PATH.endswith(".csv"):
    df = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx"):
    df = pd.read_excel(INPUT_FILE_PATH)

# Convert the first column to a list of BL numbers
BILL_OF_LADING_NUMBERS = df.iloc[:, 0].dropna().unique().tolist()


one_driver_handle = MaskedUserAgentDriver()
one_driver_handle.set_up_driver()

one_driver = one_driver_handle.driver

search_bar = SearchBar(one_driver, (By.ID, "searchName"))
search_button = Button((By.ID, "btnSearch"), one_driver)
search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
cookie_handler = NoCookieHandler()
scrape_time = ScrapeTime()
one = OneWebsite(
    ONE_ECOMM_TRACKING_URL,
    one_driver,
    search_feature,
    cookie_handler,
    shipment_scraper_factory=OneShipmentScraper,
    container_scraper_factory=OneContainerScraper,
    milestone_scraper_factory=OneMilestoneScraper,
    scrape_time=scrape_time,
)
csv_observer = CSVDatabase(OUTPUT_FILE_PATH)
one.attach(csv_observer)

for bl in BILL_OF_LADING_NUMBERS:
    one.open()
    one.track_shipment(bl)
