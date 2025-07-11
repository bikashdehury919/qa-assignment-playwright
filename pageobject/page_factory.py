# Centralized factory for page object instances.
from pageobject.home_page import HomePage
from pageobject.product_page import ProductPage
from utills.basepage import BasePage
from pageobject.checkout_page import CheckoutPage
from pageobject.place_order import PlaceOrderPage


class PageFactory:

    def __init__(self, page, config):
        self.page = page
        self.config = config

    @property
    def base(self) -> BasePage:
        return BasePage(self.page)

    @property
    def home(self) -> HomePage:
        return HomePage(self.page)

    @property
    def product(self) -> ProductPage:
        return ProductPage(self.page,self.config)

    @property
    def checkout(self) -> CheckoutPage:
        return CheckoutPage(self.page, self.config)

    @property
    def place_order(self) -> PlaceOrderPage:
        return PlaceOrderPage(self.page, self.config)

