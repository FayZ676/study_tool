"""Web scraping utilities."""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

HTML = str


def extract_page_html(url: str) -> HTML:
    """Extract all the html for a given url, waiting for the page to fully load."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        logger.info("Fetching HTML from: %s", url)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        return driver.page_source
    finally:
        driver.quit()
