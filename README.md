# SauceDemo UI Automation Tests

A small Python + Selenium + pytest suite for https://www.saucedemo.com/.

## Coverage

1. **Two-item checkout and price checks** — signs in with the public demo account, adds Sauce Labs Backpack and Sauce Labs Bike Light, checks the cart contents, sums the item prices, compares the subtotal, verifies `subtotal + tax = total`, and completes the order.
2. **Z-to-A sorting** — selects the `Name (Z to A)` option and compares the displayed product-name sequence with an independently sorted sequence.
3. **Failed login** — submits an incorrect password and verifies the error message and that the inventory page is not opened.

## Project files

- `saucedemo_tests.py` — complete test suite, divided into three clearly marked parts.
- `requirements.txt` — Python dependencies.
- `SauceDemo_Automation_Code_and_Explanation.pdf` — code and explanation for each test.
- `SauceDemo_Test_Execution_Report.pdf` — test scope, expected results, execution instructions, and reporting notes.

## Requirements

- Python 3.10 or newer
- Google Chrome
- Internet access to reach SauceDemo

Selenium 4 includes Selenium Manager, which normally obtains a compatible ChromeDriver automatically.

## Setup

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the tests

Run all tests with console output:

```bash
python -m pytest -v
```

Create an HTML report:

```bash
python -m pytest -v --html=reports/test-report.html --self-contained-html
```

Run Chrome headlessly:

**Windows PowerShell**
```powershell
$env:HEADLESS="1"
python -m pytest -v
```

**macOS / Linux**
```bash
HEADLESS=1 python -m pytest -v
```

## Expected outcomes

| Test | Expected result |
|---|---|
| Two-item checkout | Exactly two selected items; subtotal equals the sum of item prices; total equals subtotal plus displayed tax; order confirmation appears |
| Z-to-A sort | Displayed product names match reverse alphabetical order |
| Failed login | Login error appears; inventory is not displayed |

The test suite does not hard-code product prices or tax values. It reads the values rendered by the application and validates the arithmetic. `Decimal` is used for currency calculations to avoid binary floating-point rounding errors.

## Test data and safety

The suite uses SauceDemo's publicly documented demo credentials (`standard_user` / `secret_sauce`) and placeholder checkout details. It places a demo order in the test application. Do not reuse this approach against a real store or production checkout without explicit authorization.

## Troubleshooting

- **ChromeDriver/browser mismatch:** update Chrome and Selenium; Selenium Manager should resolve the driver.
- **Browser not found:** install Google Chrome or adjust the webdriver setup for your browser.
- **Timeout or changed selectors:** check whether SauceDemo's UI has changed and update the selectors.
- **Headless issues:** run once without `HEADLESS=1` to inspect the browser behavior.

## Notes

This is a UI automation example, not a guarantee that the website will always be available. A successful local test run depends on the live demo site, browser, network, and current application behavior.
