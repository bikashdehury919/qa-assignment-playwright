import allure
import logging
from locators.place_order_locators import PlaceOrderLocators as Loc


class PlaceOrderPage:
    def __init__(self, page, config):
        self.page = page
        self.timeout = config["timeouts"]["element_wait"]
        self.logger = logging.getLogger(__name__)

    @allure.step("Placing the order and capturing the confirmation number")
    def place_order_and_capture_number(self):
        try:
            with allure.step("Clicking the 'Place Order' button"):
                self.page.click(Loc.PLACE_ORDER_BUTTON, timeout=self.timeout)
                self.logger.info("🛒 Clicked on 'Place Order'.")

            with allure.step("Waiting for success page to load"):
                self.page.wait_for_url(Loc.SUCCESS_PAGE_URL, timeout=30000)
                self.logger.info("Redirected to order success page.")

            with allure.step("Verifying thank-you message"):
                self.page.wait_for_selector(Loc.THANK_YOU_MESSAGE, timeout=self.timeout)
                confirmation_msg = self.page.locator(Loc.THANK_YOU_MESSAGE).inner_text()
                assert "Thank you for your purchase!" in confirmation_msg
                self.logger.info(f"Confirmation message: {confirmation_msg}")

            with allure.step("Extracting order number"):
                self.page.wait_for_selector(Loc.ORDER_NUMBER, timeout=self.timeout)
                order_number = self.page.locator(Loc.ORDER_NUMBER).inner_text()
                self.logger.info(f"🧾 Order Number: {order_number}")
                allure.attach(order_number, name="Order Number", attachment_type=allure.attachment_type.TEXT)

            return order_number

        except Exception as e:
            self.logger.error(f"Failed to place order or retrieve confirmation: {e}")
            allure.attach(str(e), name="Order Placement Error", attachment_type=allure.attachment_type.TEXT)
            return None
