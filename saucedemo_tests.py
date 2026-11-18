"""
SauceDemo UI automation tests
Stack: Python 3.10+, Selenium 4, pytest

Run:
    python -m pip install -r requirements.txt
    python -m pytest -v --html=reports/test-report.html --self-contained-html

The tests use SauceDemo's public demo credentials:
    standard_user / secret_sauce

Notes:
- Selenium Manager (included with Selenium 4) normally resolves the browser driver.
- Set HEADLESS=1 to run Chrome headlessly.
- The checkout test adds two products, validates the item subtotal, tax,
  and displayed total using Decimal to avoid floating-point comparisons.
"""

import os
from decimal import Decimal, ROUND_HALF_UP

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://www.saucedemo.com/"
USERNAME = "standard_user"
PASSWORD = "secret_sauce"
WAIT_SECONDS = 10


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(0)
    yield browser
    browser.quit()


def wait_for(driver, locator):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located(locator)
    )


def login(driver, username=USERNAME, password=PASSWORD):
    driver.get(BASE_URL)
    wait_for(driver, (By.ID, "user-name")).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def money(value: str) -> Decimal:
    """Convert '$9.99' to an exact Decimal('9.99')."""
    return Decimal(value.replace("$", "").strip()).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


# ---------------------------------------------------------------------------
# PART 1 - End-to-end checkout with two products and price validation
# ---------------------------------------------------------------------------

def test_checkout_two_items_and_validate_final_price(driver):
    login(driver)
    wait_for(driver, (By.CLASS_NAME, "inventory_list"))

    # Select two known products by their stable data-test attributes.
    driver.find_element(
        By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'
    ).click()
    driver.find_element(
        By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-bike-light"]'
    ).click()

    # Validate cart badge and both selected product names.
    assert driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text == "2"
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait_for(driver, (By.CLASS_NAME, "cart_list"))

    cart_names = [
        item.text for item in driver.find_elements(
            By.CSS_SELECTOR, ".cart_item .inventory_item_name"
        )
    ]
    assert set(cart_names) == {"Sauce Labs Backpack", "Sauce Labs Bike Light"}

    cart_prices = [
        money(item.text) for item in driver.find_elements(
            By.CSS_SELECTOR, ".cart_item .inventory_item_price"
        )
    ]
    expected_subtotal = sum(cart_prices, Decimal("0.00"))
    assert len(cart_prices) == 2

    driver.find_element(By.ID, "checkout").click()
    wait_for(driver, (By.ID, "first-name"))
    driver.find_element(By.ID, "first-name").send_keys("Test")
    driver.find_element(By.ID, "last-name").send_keys("Customer")
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    driver.find_element(By.ID, "continue").click()

    wait_for(driver, (By.CLASS_NAME, "summary_subtotal_label"))

    # Compare the UI subtotal to the sum of the two cart line prices.
    subtotal_text = driver.find_element(
        By.CLASS_NAME, "summary_subtotal_label"
    ).text
    displayed_subtotal = money(subtotal_text.split("$")[-1])
    assert displayed_subtotal == expected_subtotal

    # Validate tax and total arithmetic from the values shown by the site.
    tax_text = driver.find_element(
        By.CLASS_NAME, "summary_tax_label"
    ).text
    displayed_tax = money(tax_text.split("$")[-1])

    total_text = driver.find_element(
        By.CLASS_NAME, "summary_total_label"
    ).text
    displayed_total = money(total_text.split("$")[-1])

    expected_total = (expected_subtotal + displayed_tax).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert displayed_total == expected_total, (
        f"Total mismatch: expected {expected_total}, got {displayed_total}"
    )

    # Finish the checkout and validate the confirmation page.
    driver.find_element(By.ID, "finish").click()
    confirmation = wait_for(driver, (By.CLASS_NAME, "complete-header"))
    assert confirmation.text == "Thank you for your order!"


# ---------------------------------------------------------------------------
# PART 2 - Sort inventory from Z to A and validate the order
# ---------------------------------------------------------------------------

def test_sort_products_z_to_a(driver):
    login(driver)
    wait_for(driver, (By.CLASS_NAME, "inventory_list"))

    sort_dropdown = Select(wait_for(driver, (By.CLASS_NAME, "product_sort_container")))
    sort_dropdown.select_by_value("za")

    # Read the names in the order rendered by the page.
    displayed_names = [
        element.text for element in driver.find_elements(
            By.CLASS_NAME, "inventory_item_name"
        )
    ]

    # Independently calculate the expected reverse alphabetical order.
    expected_names = sorted(displayed_names, key=str.casefold, reverse=True)

    assert displayed_names == expected_names, (
        "Products are not sorted Z-A.\n"
        f"Displayed: {displayed_names}\n"
        f"Expected:  {expected_names}"
    )


# ---------------------------------------------------------------------------
# PART 3 - Failed login validation
# ---------------------------------------------------------------------------

def test_failed_login_shows_error_message(driver):
    login(driver, username="standard_user", password="wrong_password")

    error = wait_for(driver, (By.CSS_SELECTOR, '[data-test="error"]'))
    assert "Username and password do not match" in error.text
    assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")
    assert driver.find_elements(By.CLASS_NAME, "inventory_list") == []
