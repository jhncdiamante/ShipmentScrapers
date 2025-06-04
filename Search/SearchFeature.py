from Search.ISearchFeature import ISearchFeature
from Search.ISearchBar import ISearchBar
from Button.IButton import IButton


class SearchFeature(ISearchFeature):
    def __init__(self, search_bar, search_button):
        self.search_bar: ISearchBar = search_bar
        self.search_button: IButton = search_button


    def search(self, keyword: str):
        self.search_bar.type(keyword)
        self.search_button.click()

