from utills.basepage import BasePage
import allure
import logging
import math
from locators.product_page_locators import ProductPageLocators as Loc


class ProductPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page)
        self.config = config
        self.timeout = config["timeouts"]["element_wait"]
        self.logger = logging.getLogger(__name__)
        self._product_name = None

    def _is_valid(self, value):
        return value is not None and str(value).strip() != "" and not (isinstance(value, float) and math.isnan(value))

    @allure.step("Applying multiple filters: {filters}")
    def apply_filters(self, filters: dict) -> None:
        try:
            self.wait_for_loader_to_disappear()
            for filter_name, option_text in filters.items():
                if not self._is_valid(option_text):
                    self.logger.warning(f"Skipping filter '{filter_name}' due to invalid value: {option_text}")
                    continue

                self.page.wait_for_timeout(500)
                self.logger.info(f"Applying filter: {filter_name} → {option_text}")

                filter_section = self.page.locator(Loc.FILTER_SECTION, has_text=filter_name).first
                filter_section.scroll_into_view_if_needed()
                filter_section.locator(Loc.FILTER_TITLE).click(timeout=self.timeout)

                filter_upper = filter_name.strip().upper()
                if filter_upper == "COLOR":
                    selector = f"a[aria-label='{option_text}'] div.swatch-option.color"
                elif filter_upper == "SIZE":
                    selector = f"a[aria-label='{option_text}'] div.swatch-option.text"
                else:
                    selector = f"div.filter-options-item:has-text('{filter_name}') a:has-text('{option_text}')"

                option = self.page.locator(selector).first
                option.wait_for(state="visible", timeout=self.timeout)
                option.scroll_into_view_if_needed()
                option.click()

                self.logger.info(f"Filter applied: {filter_name} → {option_text}")
                self.page.wait_for_timeout(1000)

        except Exception as e:
            self.logger.error(f"Failed to apply filters: {e}")
            raise

    @allure.step("Clicking first visible product after filters")
    def click_first_visible_product(self) -> None:
        try:
            self.page.wait_for_timeout(2000)
            products = self.page.locator(Loc.PRODUCT_LINKS)
            if products.count() == 0:
                self.logger.warning("No products found after applying filters.")
                return
            first_product = products.first
            first_product.wait_for(state="visible", timeout=self.timeout)
            first_product.scroll_into_view_if_needed()
            first_product.click()
            self.logger.info("Clicked first visible product.")
        except Exception as e:
            self.logger.error(f"Failed to click on first visible product: {e}")
            raise

    @allure.step("Selecting size: {size}")
    def select_size(self, size: str):
        selector = f'div.swatch-option.text[option-label="{size}"]'
        try:
            self.page.locator(selector).click(timeout=self.timeout)
            self.logger.info(f"Size selected: {size}")
        except Exception as e:
            self.logger.error(f"Failed to select size {size}: {e}")
            raise

    @allure.step("Selecting color: {color}")
    def select_color(self, color: str):
        selector = f'div.swatch-option.color[option-label="{color}"]'
        try:
            self.page.locator(selector).click(timeout=self.timeout)
            self.logger.info(f"Color selected: {color}")
        except Exception as e:
            self.logger.error(f"Failed to select color {color}: {e}")
            raise

    @allure.step("Setting quantity to {qty}")
    def set_quantity(self, qty: int):
        try:
            qty_input = self.page.locator(Loc.QUANTITY_INPUT)
            qty_input.fill(str(qty), timeout=self.timeout)
            self.logger.info(f"Quantity set to: {qty}")
        except Exception as e:
            self.logger.error(f"Failed to set quantity {qty}: {e}")
            raise

    @allure.step("Customize product: Size, Color, Quantity (if provided)")
    def customize_product_selection(self, size: str, color: str, quantity):
        if self._is_valid(size):
            with allure.step("Select product size"):
                self.select_size(size)

        if self._is_valid(color):
            with allure.step("Select product color"):
                self.select_color(color)

        if self._is_valid(quantity):
            with allure.step(f"Set product quantity to {quantity}"):
                self.set_quantity(int(quantity))

    @allure.step("Add product to cart and verify success message")
    def add_product_to_cart_and_verify(self):
        try:
            product_name_element = self.page.locator(Loc.PRODUCT_NAME)
            product_name_element.wait_for(state="visible", timeout=self.timeout)
            product_name = product_name_element.inner_text().strip()
            self.logger.info(f"Stored product name: {product_name}")

            self.page.locator(Loc.ADD_TO_CART_BUTTON).click(timeout=self.timeout)
            self.logger.info("'Add to Cart' button clicked.")

            expected_message = f"You added {product_name} to your shopping cart."
            success_message = self.page.locator(Loc.SUCCESS_MESSAGE)
            success_message.wait_for(state="visible", timeout=self.timeout)
            actual_message = success_message.inner_text().strip()

            self.logger.info(f"Expected success message: {expected_message}")
            self.logger.info(f"Actual success message: {actual_message}")

            if expected_message.lower() not in actual_message.lower():
                raise AssertionError("Expected success message not found in actual message.")

            self.logger.info("Success message verified.")

        except Exception as e:
            self.logger.error(f"Add to cart or verification failed: {e}")
            allure.attach(actual_message if 'actual_message' in locals() else '',
                          name="Actual Success Message",
                          attachment_type=allure.attachment_type.TEXT)
            raise

    @allure.step("Opening mini cart")
    def open_mini_cart(self):
        try:
            cart_icon = self.page.locator(Loc.MINI_CART_ICON)
            cart_icon.wait_for(state="visible", timeout=self.timeout)
            cart_icon.click(timeout=self.timeout)
            self.logger.info("Mini cart opened.")
        except Exception as e:
            self.logger.error(f"Failed to open mini cart: {e}")
            raise

    @allure.step("Clicking 'Proceed to Checkout'")
    def click_proceed_to_checkout(self):
        try:
            checkout_button = self.page.locator(Loc.CHECKOUT_BUTTON)
            checkout_button.wait_for(state="visible", timeout=self.timeout)
            checkout_button.click(timeout=self.timeout)
            self.logger.info("Proceeded to Checkout.")
        except Exception as e:
            self.logger.error(f"Failed to click 'Proceed to Checkout': {e}")
            raise
