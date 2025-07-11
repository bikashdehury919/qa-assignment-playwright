from utills.basepage import BasePage
from locators.home_locators import HomePageLocators as Loc
import allure
import math


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def _is_valid(self, cat):
        return cat and not (isinstance(cat, float) and math.isnan(cat)) and str(cat).strip() != ""

    @allure.step("Navigating through menu path: {menu_path}")
    def navigate_to_category(self, menu_path: list) -> None:
        if not menu_path:
            raise ValueError("Menu path cannot be empty.")

        cleaned_menu_path = [str(cat).strip() for cat in menu_path if self._is_valid(cat)]

        if not cleaned_menu_path:
            raise ValueError("After cleaning, menu path is empty.")

        if cleaned_menu_path[0].lower() == "men":
            self.select_MEN_menu_path(cleaned_menu_path)
            return

        for index, label in enumerate(cleaned_menu_path):
            selector = Loc.nav_menu_item(label)
            try:
                self.page.wait_for_selector(selector, timeout=5000, state="visible")
                if index < len(cleaned_menu_path) - 1:
                    self.page.hover(selector)
                    self.logger.info(f"Hovered on menu: {label}")
                else:
                    self.page.click(selector)
                    self.logger.info(f"Clicked on menu item: {label}")
            except Exception as e:
                self.logger.error(f"Navigation failed at '{label}': {e}")
                raise

    @allure.step("Clicking Men category and filter if subcategory exists")
    def select_MEN_menu_path(self, menu_labels: list):
        if not menu_labels or not self._is_valid(menu_labels[0]):
            raise ValueError("Menu path must start with a valid 'Men' category.")

        try:
            men_label = menu_labels[0].strip()
            men_locator = self.page.locator(Loc.NAVIGATION_MENU).get_by_text(men_label, exact=True).first
            men_locator.wait_for(timeout=5000)
            men_locator.click()
            self.logger.info(f"Clicked on top nav menu item: {men_label}")
        except Exception as e:
            self.logger.error(f"Failed to click 'Men' top nav: {e}")
            raise

        if len(menu_labels) > 1 and self._is_valid(menu_labels[1]):
            sub_label = menu_labels[1].strip()
            try:
                sub_locator = self.page.locator(Loc.subcategory_xpath(sub_label))
                sub_locator.wait_for(timeout=5000)
                sub_locator.click()
                self.logger.info(f"Clicked subcategory link: {sub_label}")
            except Exception as e:
                self.logger.error(f"Failed to click subcategory '{sub_label}': {e}")
                raise

        if len(menu_labels) > 2 and self._is_valid(menu_labels[2]):
            filter_label = menu_labels[2].strip()
            with allure.step(f"Clicking sidebar filter category: {filter_label}"):
                try:
                    sidebar_selector = Loc.SIDEBAR_FILTER.format(filter_label=filter_label)
                    sidebar_locator = self.page.locator(sidebar_selector)
                    sidebar_locator.wait_for(timeout=5000)
                    sidebar_locator.click()
                    self.logger.info(f"Clicked sidebar filter category: {filter_label}")
                except Exception as e:
                    self.logger.error(f"Sidebar filter click failed for '{filter_label}': {e}")
                    raise
