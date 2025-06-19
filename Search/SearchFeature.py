from Search.ISearchFeature import ISearchFeature
from Search.ISearchBar import ISearchBar
from Button.IButton import IButton


class SearchFeature(ISearchFeature):
    _search_bar: ISearchBar
    _search_button: IButton
    def __init__(self, search_bar, search_button):
        self._search_bar = search_bar
        self._search_button = search_button

    def search(self, keyword: str) -> None:
        self._search_bar.type(keyword)
        self._search_button.click()
