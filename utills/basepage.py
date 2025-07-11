from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
import logging
from typing import Optional
import allure


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    def navigate(self, url: str, timeout: int = 30000) -> None:
        with allure.step(f"Navigating to {url}"):
            try:
                self.page.goto(url, timeout=timeout)
                self.logger.info(f"Navigated to {url}")
                self.setup_page()
            except PlaywrightTimeout:
                self.logger.error(f"Navigation timeout to {url}")
                raise
            except Exception as e:
                self.logger.error(f"Navigation failed: {e}")
                raise

    def click(self, selector: str, timeout: int = 10000, force: bool = False) -> None:
        with allure.step(f"Clicking element: {selector}"):
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.click(selector, force=force)
                self.logger.info(f"Clicked {selector}")
            except Exception as e:
                self.logger.error(f"Click failed on {selector}: {e}")
                raise

    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        with allure.step(f"Filling {selector} with '{value}'"):
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.fill(selector, value)
                self.logger.info(f"Filled {selector} with {value}")
            except Exception as e:
                self.logger.error(f"Fill failed on {selector}: {e}")
                raise

    def get_text(self, selector: str, timeout: int = 10000) -> Optional[str]:
        with allure.step(f"Getting text from {selector}"):
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                text = self.page.text_content(selector)
                self.logger.info(f"Text from {selector}: {text}")
                return text
            except Exception as e:
                self.logger.error(f"Get text failed for {selector}: {e}")
                raise

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        with allure.step(f"Checking visibility of {selector}"):
            try:
                return self.page.is_visible(selector, timeout=timeout)
            except Exception as e:
                self.logger.warning(f"Element {selector} not visible: {e}")
                return False

    def wait_for_element(self, selector: str, timeout: int = 10000, state: str = "visible") -> None:
        with allure.step(f"Waiting for element: {selector} to be {state}"):
            try:
                self.page.wait_for_selector(selector, state=state, timeout=timeout)
                self.logger.info(f"Element {selector} is now {state}")
            except Exception as e:
                self.logger.error(f"Wait for {selector} ({state}) failed: {e}")
                raise

    def hover(self, selector: str, timeout: int = 10000) -> None:
        with allure.step(f"Hovering over element: {selector}"):
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.hover(selector)
                self.logger.info(f"Hovered over {selector}")
            except Exception as e:
                self.logger.error(f"Hover failed on {selector}: {e}")
                raise

    def press_key(self, selector: str, key: str, timeout: int = 5000) -> None:
        with allure.step(f"Pressing '{key}' on {selector}"):
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                self.page.press(selector, key)
                self.logger.info(f"Pressed '{key}' on {selector}")
            except Exception as e:
                self.logger.error(f"Failed to press '{key}' on {selector}: {e}")
                raise

    def take_screenshot(self, name: str = "screenshot.png", full_page: bool = True) -> None:
        with allure.step(f"Taking screenshot: {name}"):
            try:
                self.page.screenshot(path=name, full_page=full_page)
                self.logger.info(f"Screenshot saved: {name}")
                allure.attach.file(name, name=name, attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                self.logger.error(f"Screenshot failed: {e}")
                raise

    def scroll_into_view(self, selector: str, timeout: int = 10000) -> None:
        with allure.step(f"Scrolling {selector} into view"):
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                self.page.locator(selector).scroll_into_view_if_needed()
                self.logger.info(f"Scrolled into view: {selector}")
            except Exception as e:
                self.logger.error(f"Scroll into view failed: {e}")
                raise

    def get_element_count(self, selector: str) -> int:
        """Return number of elements matching a selector."""
        try:
            count = self.page.locator(selector).count()
            self.logger.info(f"{count} elements found for selector: {selector}")
            return count
        except Exception as e:
            self.logger.error(f"Failed to count elements for {selector}: {e}")
            raise

    def wait_for_url_contains(self, partial_url: str, timeout: int = 10000) -> None:
        """Wait for URL to contain a substring (e.g., 'success')"""
        with allure.step(f"Waiting for URL to contain '{partial_url}'"):
            try:
                self.page.wait_for_url(f"**{partial_url}**", timeout=timeout)
                self.logger.info(f"URL now contains '{partial_url}'")
            except Exception as e:
                self.logger.error(f"URL wait failed for '{partial_url}': {e}")
                raise

    def handle_consent_popup(self) -> None:
        """Handle cookie or consent popups."""
        try:
            self.page.get_by_role("button", name="Consent", exact=True).click(timeout=3000)
            self.logger.info("Consent popup dismissed.")
        except Exception as e:
            self.logger.debug(f"No consent popup appeared: {e}")

    def dismiss_ads_or_modals(self) -> None:
        """Dismiss modal ads or popups."""
        try:
            close_btn = self.page.get_by_role("button", name="Close", exact=True)
            close_btn.wait_for(timeout=3000)
            close_btn.click()
            self.logger.info("Ad/modal dismissed.")
        except Exception as e:
            self.logger.debug(f"No ad/modal to dismiss: {e}")

    def setup_page(self) -> None:
        """Handle popups and modals immediately after navigation."""
        self.handle_consent_popup()
        self.dismiss_ads_or_modals()

    @allure.step("Waiting for Magento loading spinner to disappear")
    def wait_for_loader_to_disappear(self, timeout: int = 10000) -> None:
        """Wait for the Magento loading mask (spinner) to disappear."""
        try:
            self.logger.info("Waiting for Magento loader to disappear...")
            self.page.wait_for_selector(".loading-mask", state="hidden", timeout=timeout)
            self.logger.info("Loading spinner disappeared.")
        except Exception as e:
            self.logger.warning(f"Loader may not have disappeared in time: {e}")
