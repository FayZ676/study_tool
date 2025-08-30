import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from lxml import html as lxml_html


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class DocumentationSection:
    name: str
    text: str
    path: str
    children: list["DocumentationSection"]
    last_updated: datetime


@dataclass
class Documentation:
    sections: list[DocumentationSection]
    url: str
    last_updated: datetime


HTML = str


def extract_page_html(url: str) -> HTML:
    """Extract all the html for a given url, waiting for the page to fully load."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        return driver.page_source
    finally:
        driver.quit()


def parse_documentation(url: str, html: HTML) -> Documentation:
    """Parse the HTML into a Documentation instance."""

    def parse_documentation_section(li_element) -> DocumentationSection:
        """Extract a documentation section from an <li> element."""
        link_elem = (
            li_element.xpath('.//a[contains(@class, "awsui_link")]')[0]
            if li_element.xpath('.//a[contains(@class, "awsui_link")]')
            else None
        )

        if link_elem is not None:
            name = link_elem.xpath(
                './/span[contains(@class, "awsui_link-text")]/text()'
            )[0].strip()
            href = link_elem.get("href", "")
            path = href if href else ""
        else:
            name = "Unknown Section"
            path = ""

        children = []
        nested_ul = li_element.xpath(
            './/ul[contains(@class, "awsui_list-variant-expandable-link-group")]'
        )
        if nested_ul:
            child_items = nested_ul[0].xpath("./li")
            for child_li in child_items:
                children.append(parse_documentation_section(child_li))

        return DocumentationSection(
            name=name,
            text=name,
            path=path,
            children=children,
            last_updated=datetime.now(),
        )

    tree = lxml_html.fromstring(html)
    contents_xpath = "//ul[contains(@class, 'awsui_list_l0dv0_n545v_224') and contains(@class, 'awsui_list-variant-root_l0dv0_n545v_245')]//li[@class='awsui_list-item_l0dv0_n545v_260']"
    top_level_items = tree.xpath(contents_xpath)

    if not top_level_items:
        logger.warning("❌ No list items found.")
        return Documentation(sections=[], url=url, last_updated=datetime.now())

    logger.info("✅ Found %d list items.", len(top_level_items))

    sections = []
    for li in top_level_items:
        parent_ul = li.getparent()
        if parent_ul is not None and "expandable-link-group" in parent_ul.get(
            "class", ""
        ):
            continue
        sections.append(parse_documentation_section(li))

    return Documentation(
        sections=sections,
        url=url,
        last_updated=datetime.now(),
    )


if __name__ == "__main__":
    BASE_URL = "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"
    full_html = extract_page_html(url=BASE_URL)
    documentation = parse_documentation(url=BASE_URL, html=full_html)
    with open("documentation.json", "w", encoding="utf-8") as f:
        json.dump(asdict(documentation), f, default=str, indent=2)
