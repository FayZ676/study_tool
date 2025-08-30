"""HTML parsing utilities for AWS documentation."""

import logging
from datetime import datetime
from lxml import html as lxml_html
from models import Documentation, DocumentationSection
from web_scraper import HTML

logger = logging.getLogger(__name__)


def extract_link_info(li_element) -> tuple[str, str]:
    """Extract name and path from a link element within an <li> element."""
    link_elem = (
        li_element.xpath('.//a[contains(@class, "awsui_link")]')[0]
        if li_element.xpath('.//a[contains(@class, "awsui_link")]')
        else None
    )

    if link_elem is not None:
        name = link_elem.xpath('.//span[contains(@class, "awsui_link-text")]/text()')[
            0
        ].strip()
        href = link_elem.get("href", "")
        path = href if href else ""
        return name, path
    else:
        return "Unknown Section", ""


def parse_child_sections(li_element) -> list[DocumentationSection]:
    """Parse child sections from nested ul elements."""
    children = []
    nested_ul = li_element.xpath(
        './/ul[contains(@class, "awsui_list-variant-expandable-link-group")]'
    )
    if nested_ul:
        child_items = nested_ul[0].xpath("./li")
        for child_li in child_items:
            children.append(parse_documentation_section(child_li))
    return children


def parse_documentation_section(li_element) -> DocumentationSection:
    """Extract a documentation section from an <li> element."""
    name, path = extract_link_info(li_element)
    children = parse_child_sections(li_element)

    return DocumentationSection(
        name=name,
        text=name,
        path=path,
        children=children,
        last_updated=datetime.now(),
    )


def extract_top_level_items(html: HTML) -> list:
    """Extract top-level documentation items from HTML."""
    tree = lxml_html.fromstring(html)
    contents_xpath = "//ul[contains(@class, 'awsui_list_l0dv0_n545v_224') and contains(@class, 'awsui_list-variant-root_l0dv0_n545v_245')]//li[@class='awsui_list-item_l0dv0_n545v_260']"
    return tree.xpath(contents_xpath)


def is_expandable_item(li_element) -> bool:
    """Check if an item is part of an expandable link group."""
    parent_ul = li_element.getparent()
    return parent_ul is not None and "expandable-link-group" in parent_ul.get(
        "class", ""
    )


def parse_documentation(url: str, html: HTML) -> Documentation:
    """Parse the HTML into a Documentation instance."""
    top_level_items = extract_top_level_items(html)

    if not top_level_items:
        logger.warning("❌ No list items found.")
        return Documentation(sections=[], url=url, last_updated=datetime.now())

    logger.info("✅ Found %d list items.", len(top_level_items))

    sections = []
    for li in top_level_items:
        if is_expandable_item(li):
            continue
        sections.append(parse_documentation_section(li))

    return Documentation(
        sections=sections,
        url=url,
        last_updated=datetime.now(),
    )
