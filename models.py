"""Data models for documentation parsing."""

from datetime import datetime
from dataclasses import dataclass


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
