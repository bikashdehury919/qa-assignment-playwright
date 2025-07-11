import time
import pytest
import allure
from utills.excel_reader import ExcelReader
from pageobject.page_factory import PageFactory

EXCEL_PATH = "data/test_data.xlsx"


@allure.tag("regression", "checkout")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.order(1)
def test_complete_checkout_flow(config, page, order_test_data):
    factory = PageFactory(page, config)
    customer_data = ExcelReader(EXCEL_PATH).get_customer()

    base_url = config['urls']['base_url']
    timeouts = config['timeouts']

    with allure.step("Open Magento Homepage"):
        factory.base.navigate(base_url, timeout=timeouts['page_load'])

    with allure.step("Navigate to Category from Excel"):
        category_path = [
            order_test_data.get("Category"),
            order_test_data.get("SubCategory1"),
            order_test_data.get("SubCategory2")
        ]

        factory.home.navigate_to_category(category_path)

    with allure.step("Apply Product Filters"):
        filters = {
            "SIZE": order_test_data["Size"],
            "COLOR": order_test_data["Color"],
            "Pattern": order_test_data["Pattern"],
            "Climate": order_test_data["Climate"],
            "Style": order_test_data["Style"]
        }
        factory.product.apply_filters(filters)

    with allure.step("Click first visible product"):
        factory.product.click_first_visible_product()

    with allure.step("Select product size"):
        factory.product.customize_product_selection(
            size=order_test_data["Size"],
            color=order_test_data["Color"],
            quantity=order_test_data["Quantity"]
        )

    with allure.step("Add product to cart and verify"):
        factory.product.add_product_to_cart_and_verify()

    with allure.step("Open mini cart"):
        factory.product.open_mini_cart()

    with allure.step("Proceed to checkout"):
        factory.product.click_proceed_to_checkout()

    with allure.step("Fill shipping address"):
        factory.checkout.fill_shipping_address(
            email=customer_data["email"],
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            street=customer_data["street"],
            city=customer_data["city"],
            zip_code=customer_data["zip_code"],
            country=customer_data["country"],
            phone=str(customer_data["phone"])
        )

    with allure.step("Get available shipping methods"):
        shipping_methods = factory.checkout.get_shipping_methods()
        assert shipping_methods, "No shipping methods available"

    with allure.step("Click Next"):
        factory.checkout.click_next_button()

    with allure.step(f"Apply discount code: {order_test_data['DiscountCode']}"):
        discount_result = factory.checkout.apply_and_verify_discount(order_test_data["DiscountCode"])
        assert discount_result is not None, "Discount application failed"
        allure.attach(
            f"""
            Subtotal: ${discount_result['subtotal']}
            Discount: -${discount_result['discount']}
            Shipping: ${discount_result['shipping']}
            Total: ${discount_result['total']}
            """.strip(),
            name="Discount Summary",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Place order and capture number"):
        order_number = factory.place_order.place_order_and_capture_number()
        assert order_number is not None, "Order number was not captured."
