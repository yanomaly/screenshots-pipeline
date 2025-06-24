from enum import StrEnum

from pydantic import BaseModel, Field


class SelectorType(StrEnum):
    text = "text"
    locator = "locator"
    complex = "complex"


class MatchMode(StrEnum):
    exact = "exact"
    partial = "partial"


class ElementSelector(BaseModel):
    type: SelectorType


class TextElementSelector(ElementSelector):
    text: str
    match: MatchMode = MatchMode.exact


class LocatorElementSelector(ElementSelector):
    expression: str = Field(
        ...,
        description="Selector (XPath expression) to pass it into the Playwright 'page.locator' function.",
    )


class ComplexElementSelector(ElementSelector):
    text_selector: TextElementSelector
    locator_selector: LocatorElementSelector
