# checkout_page

from utills.basepage import BasePage
from locators.checkout_locators import CheckoutPageLocators as Loc
import allure
import logging
import time


class CheckoutPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page)
        self.config = config
        self.timeout = config["timeouts"]["element_wait"]
        self.logger = logging.getLogger(__name__)

    @allure.step("Filling shipping address")
    def fill_shipping_address(self, email, first_name, last_name, street, city, zip_code, country, phone):
        try:
            self.page.select_option(Loc.COUNTRY_SELECT, label=country)
            self.logger.info(f"Country selected: {country}")
            self.page.wait_for_selector(Loc.POSTCODE_INPUT, timeout=self.timeout)
            self.page.wait_for_selector(Loc.TELEPHONE_INPUT, timeout=self.timeout)

            self.page.locator(Loc.EMAIL_INPUT).fill(email)
            self.page.locator(Loc.FIRST_NAME_INPUT).fill(first_name)
            self.page.locator(Loc.LAST_NAME_INPUT).fill(last_name)
            self.page.locator(Loc.STREET_INPUT).fill(street)
            self.page.locator(Loc.CITY_INPUT).fill(city)
            self.page.locator(Loc.POSTCODE_INPUT).fill(zip_code)
            self.page.locator(Loc.TELEPHONE_INPUT).fill(phone)

            self.logger.info("Shipping address filled successfully.")
            time.sleep(10)
        except Exception as e:
            self.logger.error(f"Failed to fill shipping address: {e}")
            raise

    @allure.step("Fetching and selecting available shipping methods")
    def get_shipping_methods(self):
        try:
            self.wait_for_loader_to_disappear()
            self.page.wait_for_selector(Loc.SHIPPING_METHOD_ROWS, timeout=self.timeout)

            methods = []
            rows = self.page.locator(Loc.SHIPPING_METHOD_ROWS)
            count = rows.count()

            if count == 0:
                self.logger.warning("No shipping methods found.")
                return []

            for i in range(count):
                row = rows.nth(i)
                method_title = row.locator(Loc.SHIPPING_METHOD_TITLE).inner_text().strip()
                method_price = row.locator(Loc.SHIPPING_METHOD_PRICE).nth(0).inner_text().strip()
                input_value = row.locator(Loc.SHIPPING_METHOD_RADIO).get_attribute("value")

                methods.append({
                    "title": method_title,
                    "price": method_price,
                    "value": input_value
                })

            self.logger.info(f"Found {len(methods)} shipping method(s).")

            if count > 1:
                first_radio = rows.nth(0).locator(Loc.SHIPPING_METHOD_RADIO)
                first_radio.click()
                self.logger.info("Selected the first available shipping method.")

            return methods

        except Exception as e:
            self.logger.error(f"Failed to get or select shipping methods: {e}")
            return []

    @allure.step("Clicking 'Next' button to proceed to payment")
    def click_next_button(self):
        try:
            self.wait_for_loader_to_disappear()
            next_button = self.page.locator(Loc.NEXT_BUTTON)
            next_button.wait_for(state="visible", timeout=self.timeout)
            next_button.click()
            self.logger.info("Next button clicked.")

            self.page.wait_for_selector(Loc.LOADER, state="visible", timeout=2000)
            self.wait_for_loader_to_disappear()

        except Exception as e:
            self.logger.error(f"Failed to click 'Next' button: {e}")
            raise

    @allure.step("Applying and verifying discount code: {coupon_code}")
    def apply_and_verify_discount(self, coupon_code: str):
        try:
            self.page.locator(Loc.DISCOUNT_TOGGLE).click()
            self.page.wait_for_selector(Loc.DISCOUNT_INPUT, timeout=self.timeout)
            self.page.fill(Loc.DISCOUNT_INPUT, coupon_code)
            self.page.click(Loc.APPLY_DISCOUNT_BUTTON)

            self.page.wait_for_selector(Loc.TOTALS_DISCOUNT_ROW, timeout=8000)
            self.wait_for_loader_to_disappear()

            subtotal_text = self.page.locator(Loc.SUBTOTAL_PRICE).inner_text()
            discount_text = self.page.locator(Loc.DISCOUNT_PRICE).inner_text()
            shipping_text = self.page.locator(Loc.SHIPPING_PRICE).inner_text()
            total_text = self.page.locator(Loc.GRAND_TOTAL_PRICE).inner_text()

            subtotal = float(subtotal_text.replace("$", "").strip())
            discount = float(discount_text.replace("-", "").replace("$", "").strip())
            shipping = float(shipping_text.replace("$", "").strip())
            total = float(total_text.replace("$", "").strip())

            expected_total = round(subtotal - discount + shipping, 2)

            assert abs(total - expected_total) < 0.01, (
                f"Expected: ${expected_total}, Got: ${total}"
            )

            self.logger.info(f"Discount Applied: -${discount}")
            self.logger.info(f"Final Total: ${total}")
            return {
                "subtotal": subtotal,
                "discount": discount,
                "shipping": shipping,
                "total": total,
                "expected_total": expected_total
            }

        except Exception as e:
            self.logger.error(f"Error verifying discount: {e}")
            allure.attach(str(e), name="Discount Error", attachment_type=allure.attachment_type.TEXT)
            raise
