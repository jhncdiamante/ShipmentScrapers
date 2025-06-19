from CMA.CMAContainerScraper import (
    CMAContainerWithSiblingsScraper,
    CMAContainerWithNoSiblingsScraper,
)


CONTAINER_WS_CLASS_NAME = "cardelem"
SINGLE_CONTAINER_ID = "trackingsearchsection"

# There are two types of container in CMA-CGM website, each has its unique format/structure
# this method will classify them base on their identifiers
def smart_container_scraper_factory(container_element, driver):
    if container_element.get_attribute("class").strip() == CONTAINER_WS_CLASS_NAME:
        return CMAContainerWithSiblingsScraper(container_element, driver)
    elif container_element.get_attribute("id").strip() == SINGLE_CONTAINER_ID:
        return CMAContainerWithNoSiblingsScraper(container_element, driver)
    raise ValueError("Invalid Container Element.")
