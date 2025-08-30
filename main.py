"""Main script for scraping and parsing AWS Lambda documentation."""

import json
import logging
from dataclasses import asdict

from web_scraper import extract_page_html
from html_parser import parse_documentation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """Main function to orchestrate the documentation scraping and parsing."""
    BASE_URL = "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"
    html = extract_page_html(url=BASE_URL)
    documentation = parse_documentation(url=BASE_URL, html=html)
    with open("documentation.json", "w", encoding="utf-8") as f:
        json.dump(asdict(documentation), f, default=str, indent=2)

    logger.info("✅ Documentation saved to documentation.json")


if __name__ == "__main__":
    main()
