"""OmniSight AI Module - Prompt Definitions and JSON Schema.

This module provides the system instructions, user prompt builder,
and structured output schemas for analyzing webpage screenshots using
Vision Language Models (VLMs) such as Google Gemini.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


SYSTEM_PROMPT = """You are an expert UI/UX QA engineer and senior frontend developer for the OmniSight multimodal testing platform.
Your task is to visually inspect the provided webpage screenshot, along with optional HTML/DOM snippets and page URL, to detect visual bugs, layout flaws, and responsiveness defects.

UI Issue Categories to detect:
1. overlapping_text: Text lines, labels, or containers colliding or rendering on top of each other unintentionally.
2. clipped_button: Buttons or badges where label text is truncated, cut off, or extending outside container boundaries.
3. misalignment: Form inputs, buttons, navigation items, or cards that are jagged, off-grid, or have inconsistent spacing/alignment.
4. missing_element: Broken image placeholders, empty data boxes, missing price tags, or failed asset loads.
5. responsiveness: Desktop layouts overflowing mobile viewports, horizontal scrollbars caused by fixed-width elements, unscaled containers.
6. unreadable_text: Text failing WCAG color contrast guidelines, illegible font sizes, or text blending into backgrounds.

Analysis Guidelines:
- If HTML content is provided, cross-reference visual elements with the DOM to identify exact CSS selectors, IDs, or classes (e.g., '#checkout-button', '.product-card h3', 'nav.primary-nav').
- If HTML is not provided, provide a descriptive element identifier (e.g., 'checkout_button', 'hero_heading').
- Provide actionable, production-ready CSS in 'suggested_css_fix' (and 'suggested_fix') that directly repairs the issue.
- If the UI is clean and has no issues, set 'issue_detected' to false, 'issue_type' to 'none', 'severity' to 'none', and 'element' to 'None'.
- Always return a valid JSON object matching the required schema.
"""


class IssueDetail(BaseModel):
    """Detailed description of an individual UI issue."""
    element: str = Field(
        ...,
        description="The CSS selector, ID, or descriptive name of the problematic element (e.g., '#checkout-button')."
    )
    issue_type: str = Field(
        ...,
        description="Category of visual bug: overlapping_text, clipped_button, misalignment, missing_element, responsiveness, unreadable_text, or other."
    )
    severity: str = Field(
        ...,
        description="Severity of the issue: low, medium, high, or critical."
    )
    description: str = Field(
        ...,
        description="Clear, diagnostic description of the visual defect."
    )
    suggested_css_fix: str = Field(
        ...,
        description="Proposed CSS rules to repair the visual defect (e.g., 'width: 100%; box-sizing: border-box; overflow: visible;')."
    )
    suggested_fix: str = Field(
        ...,
        description="Alias for suggested_css_fix to ensure compatibility across modules."
    )


class UIAnalysisReport(BaseModel):
    """Root structured response schema for UI screenshot analysis."""
    issue_detected: bool = Field(
        ...,
        description="True if one or more visual issues are found, False if the UI is clean."
    )
    element: str = Field(
        ...,
        description="The primary problematic element or CSS selector ('None' if no issues detected)."
    )
    issue_type: str = Field(
        ...,
        description="Primary issue category: overlapping_text, clipped_button, misalignment, missing_element, responsiveness, unreadable_text, or none."
    )
    severity: str = Field(
        ...,
        description="Overall severity: low, medium, high, critical, or none."
    )
    description: str = Field(
        ...,
        description="Comprehensive summary of the visual inspection."
    )
    suggested_css_fix: str = Field(
        ...,
        description="Primary suggested CSS fix (empty string if no issues detected)."
    )
    suggested_fix: str = Field(
        ...,
        description="Alias for suggested_css_fix."
    )
    issues: List[IssueDetail] = Field(
        default_factory=list,
        description="List of all detected UI issues. Empty if no issues detected."
    )


# Standard dictionary schema for direct use with GenAI APIs
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_detected": {"type": "boolean"},
        "element": {"type": "string"},
        "issue_type": {"type": "string"},
        "severity": {"type": "string"},
        "description": {"type": "string"},
        "suggested_css_fix": {"type": "string"},
        "suggested_fix": {"type": "string"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {"type": "string"},
                    "issue_type": {"type": "string"},
                    "severity": {"type": "string"},
                    "description": {"type": "string"},
                    "suggested_css_fix": {"type": "string"},
                    "suggested_fix": {"type": "string"}
                },
                "required": ["element", "issue_type", "severity", "description", "suggested_css_fix", "suggested_fix"]
            }
        }
    },
    "required": [
        "issue_detected",
        "element",
        "issue_type",
        "severity",
        "description",
        "suggested_css_fix",
        "suggested_fix",
        "issues"
    ]
}


def build_analysis_prompt(html_content: Optional[str] = None, page_url: Optional[str] = None) -> str:
    """
    Constructs the contextual user prompt for the VLM.

    Args:
        html_content: Optional HTML markup snippet of the page or component.
        page_url: Optional URL of the page being analyzed.

    Returns:
        Formatted prompt string incorporating the available context.
    """
    parts = [
        "Analyze this webpage screenshot for visual layout defects and UI bugs.",
        "Check for: clipped buttons, overlapping text, misalignment, missing elements, responsiveness issues, and low contrast."
    ]

    if page_url:
        parts.append(f"\nPage URL: {page_url}")

    if html_content:
        # Cap HTML snippet length to prevent exceeding token limits while preserving key DOM elements
        truncated_html = html_content.strip()
        if len(truncated_html) > 6000:
            truncated_html = truncated_html[:6000] + "\n...[truncated for length]..."
        parts.append(f"\nRelevant Page HTML/DOM Snippet:\n```html\n{truncated_html}\n```")
        parts.append("\nUse the provided HTML snippet to pinpoint the exact CSS selectors, element IDs, or class names for any detected issues.")

    parts.append("\nReturn your findings strictly in the requested JSON format.")
    return "\n".join(parts)
