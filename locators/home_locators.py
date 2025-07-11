# locators/home_locators.py

class HomePageLocators:
    NAVIGATION_MENU = "nav.navigation"
    SIDEBAR_FILTER = "#narrow-by-list2 a:has-text('{filter_label}')"

    @staticmethod
    def nav_menu_item(label: str) -> str:
        return f"text={label}"

    @staticmethod
    def subcategory_xpath(label: str) -> str:
        return f"//a[contains(text(),'{label}')]"
