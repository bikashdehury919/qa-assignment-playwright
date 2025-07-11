# locators used for checkout page

class CheckoutPageLocators:
    COUNTRY_SELECT = "select[name='country_id']"
    POSTCODE_INPUT = "input[name='postcode']"
    TELEPHONE_INPUT = "input[name='telephone']"
    EMAIL_INPUT = "div.control._with-tooltip input#customer-email"
    FIRST_NAME_INPUT = "input[name='firstname']"
    LAST_NAME_INPUT = "input[name='lastname']"
    STREET_INPUT = "input[name='street[0]']"
    CITY_INPUT = "input[name='city']"

    SHIPPING_METHOD_ROWS = "table.table-checkout-shipping-method tbody tr"
    SHIPPING_METHOD_TITLE = "td.col.col-carrier"
    SHIPPING_METHOD_PRICE = "td.col.col-price >> span.price"
    SHIPPING_METHOD_RADIO = "input[type='radio']"

    NEXT_BUTTON = "button[data-role='opc-continue']"
    LOADER = ".loading-mask"

    DISCOUNT_TOGGLE = "span#block-discount-heading"
    DISCOUNT_INPUT = "input#discount-code"
    APPLY_DISCOUNT_BUTTON = "button.action.action-apply"

    TOTALS_DISCOUNT_ROW = "tr.totals.discount"
    SUBTOTAL_PRICE = "tr.totals.sub span.price"
    DISCOUNT_PRICE = "tr.totals.discount span.price"
    SHIPPING_PRICE = "tr.totals.shipping.excl span.price"
    GRAND_TOTAL_PRICE = "tr.grand.totals span.price"
