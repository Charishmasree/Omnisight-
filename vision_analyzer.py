"""OmniSight AI Module - Vision Language Model (VLM) Analyzer.

Analyzes webpage screenshots using Google Gemini to detect UI issues
such as overlapping text, clipped buttons, misalignment, missing elements,
and responsiveness problems, returning structured JSON with suggested CSS fixes.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
import PIL.Image

# Load environment variables from .env file (if present)
load_dotenv()

from prompts import (
    SYSTEM_PROMPT,
    UIAnalysisReport,
    JSON_SCHEMA,
    build_analysis_prompt,
)

# Default model configuration
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _clean_json_response(raw_text: str) -> str:
    """Strips markdown code blocks or wrapper markers from raw LLM text."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening ```json or ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Drop closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _generate_mock_analysis(
    screenshot_path: str,
    html_content: Optional[str] = None,
    page_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates a realistic deterministic analysis without requiring an API key.

    Used for mock testing, offline demonstrations, and test suites.
    """
    path_lower = str(screenshot_path).lower()
    url = page_url or "http://localhost:8000"

    # 1. Clipped Button
    if "clipped" in path_lower or "2_clipped_button" in path_lower:
        issue = {
            "element": "#checkout-button",
            "issue_type": "clipped_button",
            "severity": "high",
            "description": "The button label text 'Proceed to Secure Checkout' exceeds container width (100px) and is horizontally clipped.",
            "suggested_css_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;",
            "suggested_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 2. Overlapping Elements
    elif "overlap" in path_lower or "3_overlapping_elements" in path_lower:
        issue = {
            "element": ".promo-badge",
            "issue_type": "overlapping_text",
            "severity": "high",
            "description": "The promotional badge container (.promo-badge) has absolute positioning that directly collides with and obscures product description text.",
            "suggested_css_fix": "position: relative; margin-bottom: 16px; top: auto; z-index: 1;",
            "suggested_fix": "position: relative; margin-bottom: 16px; top: auto; z-index: 1;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 3. Misalignment
    elif "misalign" in path_lower or "4_misalignment" in path_lower:
        issue = {
            "element": "#checkout-form .form-group",
            "issue_type": "misalignment",
            "severity": "medium",
            "description": "Form inputs (Email, Shipping Address) are misaligned with irregular horizontal offsets (x=140px vs x=60px), breaking grid alignment.",
            "suggested_css_fix": "display: flex; flex-direction: column; width: 100%; margin-left: 0; box-sizing: border-box;",
            "suggested_fix": "display: flex; flex-direction: column; width: 100%; margin-left: 0; box-sizing: border-box;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 4. Missing Element
    elif "missing" in path_lower or "5_missing_element" in path_lower:
        issue = {
            "element": ".product-image-container",
            "issue_type": "missing_element",
            "severity": "medium",
            "description": "Product hero image failed to render, displaying an empty broken placeholder. Additionally, the price element is missing from the card.",
            "suggested_css_fix": "display: flex; align-items: center; justify-content: center; min-height: 200px; background: #f8fafc;",
            "suggested_fix": "display: flex; align-items: center; justify-content: center; min-height: 200px; background: #f8fafc;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 5. Responsiveness Problem
    elif "responsive" in path_lower or "6_responsiveness_problem" in path_lower:
        issue = {
            "element": ".order-summary-table",
            "issue_type": "responsiveness",
            "severity": "critical",
            "description": "The order summary table has a fixed width (620px) that exceeds the 375px mobile viewport width, causing severe horizontal overflow.",
            "suggested_css_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;",
            "suggested_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 6. Unreadable Contrast
    elif "unreadable" in path_lower or "contrast" in path_lower or "7_unreadable_contrast" in path_lower:
        issue = {
            "element": ".terms-notice p",
            "issue_type": "unreadable_text",
            "severity": "medium",
            "description": "Text color (#d4d4d4) against light gray background (#f5f5f5) provides a contrast ratio below 1.5:1, severely failing WCAG AA (4.5:1).",
            "suggested_css_fix": "color: #1f2937; font-size: 14px; line-height: 1.5;",
            "suggested_fix": "color: #1f2937; font-size: 14px; line-height: 1.5;",
        }
        report = {
            "issue_detected": True,
            **issue,
            "issues": [issue],
        }

    # 7. Normal UI (Clean, no issues)
    else:
        report = {
            "issue_detected": False,
            "element": "None",
            "issue_type": "none",
            "severity": "none",
            "description": "No visual layout issues or responsiveness defects detected. The page layout, contrast, and element alignment conform to standards.",
            "suggested_css_fix": "",
            "suggested_fix": "",
            "issues": [],
        }

    report["page_url"] = url
    report["screenshot_path"] = str(screenshot_path)
    report["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    report["mode"] = "mock_simulation"
    return report


def analyze_screenshot(
    screenshot_path: Optional[str] = None,
    html_content: Optional[str] = None,
    page_url: Optional[str] = None,
    *,
    image_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    mock: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Analyzes a webpage screenshot using a Vision Language Model (VLM).

    Detects UI issues such as overlapping text, clipped buttons,
    misalignment, missing elements, and responsiveness problems.

    Args:
        screenshot_path: Path to the screenshot image file (.png, .jpg, etc.).
        html_content: Optional HTML markup snippet or full page HTML to provide DOM context.
        page_url: Optional URL of the tested webpage.
        image_path: Backwards-compatible alias for screenshot_path.
        api_key: Optional Gemini API key. Defaults to GEMINI_API_KEY env variable.
        model_name: Optional model identifier (defaults to 'gemini-2.5-flash').
        mock: If True, uses the offline mock analyzer without calling Google Gemini.

    Returns:
        Structured JSON dictionary containing:
        - issue_detected (bool): True if issues found, False otherwise.
        - element (str): Name or CSS selector of the problematic element.
        - issue_type (str): Category (clipped_button, overlapping_text, misalignment, etc.).
        - severity (str): 'low', 'medium', 'high', 'critical', or 'none'.
        - description (str): Detailed diagnosis of the visual bug.
        - suggested_css_fix (str): Actionable CSS fix.
        - suggested_fix (str): Alias for suggested_css_fix.
        - issues (list): Array of all detected issues.
        - page_url (str): Page URL analyzed.
        - screenshot_path (str): File path of analyzed image.
        - analyzed_at (str): ISO 8601 UTC timestamp.

    Raises:
        ValueError: If neither screenshot_path nor image_path is provided, or if GEMINI_API_KEY is missing.
        FileNotFoundError: If the screenshot file does not exist on disk.
    """
    resolved_path = screenshot_path or image_path
    if not resolved_path:
        raise ValueError("A screenshot_path (or image_path) must be provided.")

    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Screenshot file not found at: {resolved_path}")

    # Validate image format using PIL
    try:
        with PIL.Image.open(resolved_path) as img:
            image = img.copy()
    except Exception as e:
        raise ValueError(f"Failed to open image at {resolved_path}: {e}")

    # Offline / Mock mode branch
    if mock:
        return _generate_mock_analysis(resolved_path, html_content=html_content, page_url=page_url)

    # Resolve API Key
    resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable "
            "(e.g., in a .env file or system environment) or pass api_key to analyze_screenshot(). "
            "To test without an API key, use mock=True or run mock tests in test_vision.py."
        )

    # Initialize Gemini client
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=resolved_api_key)
    resolved_model = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    user_prompt = build_analysis_prompt(html_content=html_content, page_url=page_url)

    try:
        response = client.models.generate_content(
            model=resolved_model,
            contents=[user_prompt, image],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=UIAnalysisReport,
                temperature=0.1,
            ),
        )

        cleaned_json = _clean_json_response(response.text)
        result_json = json.loads(cleaned_json)

        # Normalize and ensure all required fields are present
        if "suggested_css_fix" not in result_json and "suggested_fix" in result_json:
            result_json["suggested_css_fix"] = result_json["suggested_fix"]
        elif "suggested_fix" not in result_json and "suggested_css_fix" in result_json:
            result_json["suggested_fix"] = result_json["suggested_css_fix"]

        # Ensure issues array is populated
        if "issues" not in result_json or not isinstance(result_json["issues"], list):
            if result_json.get("issue_detected"):
                result_json["issues"] = [{
                    "element": result_json.get("element", "unknown"),
                    "issue_type": result_json.get("issue_type", "unknown"),
                    "severity": result_json.get("severity", "medium"),
                    "description": result_json.get("description", ""),
                    "suggested_css_fix": result_json.get("suggested_css_fix", ""),
                    "suggested_fix": result_json.get("suggested_fix", ""),
                }]
            else:
                result_json["issues"] = []

        result_json["page_url"] = page_url or ""
        result_json["screenshot_path"] = str(resolved_path)
        result_json["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        result_json["model"] = resolved_model

        return result_json

    except Exception as e:
        print(f"[OmniSight VLM] Error during vision analysis: {e}", file=sys.stderr)
        return {
            "issue_detected": False,
            "element": "error",
            "issue_type": "error",
            "severity": "high",
            "description": f"Failed to analyze image with VLM: {str(e)}",
            "suggested_css_fix": "",
            "suggested_fix": "",
            "issues": [],
            "page_url": page_url or "",
            "screenshot_path": str(resolved_path),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }


def main():
    """CLI Entry point for direct screenshot analysis."""
    parser = argparse.ArgumentParser(
        description="OmniSight VLM Analyzer - Detect visual and responsiveness UI bugs in screenshots."
    )
    parser.add_argument("screenshot", help="Path to the screenshot image file to analyze.")
    parser.add_argument("--url", default="http://localhost:8000", help="Webpage URL associated with the screenshot.")
    parser.add_argument("--html", default=None, help="Path to an optional HTML snippet file.")
    parser.add_argument("--mock", action="store_true", help="Run in mock/offline mode without calling Google Gemini.")
    parser.add_argument("--model", default=None, help="Gemini model name (e.g., gemini-2.5-flash).")
    parser.add_argument("--out", default=None, help="Path to save output JSON (optional).")

    args = parser.parse_args()

    html_content = None
    if args.html and os.path.exists(args.html):
        with open(args.html, "r", encoding="utf-8") as f:
            html_content = f.read()

    print(f"Analyzing screenshot: {args.screenshot} (mock={args.mock})...")
    result = analyze_screenshot(
        screenshot_path=args.screenshot,
        html_content=html_content,
        page_url=args.url,
        model_name=args.model,
        mock=args.mock,
    )

    formatted = json.dumps(result, indent=2)
    print("\n--- Structured VLM Analysis Output ---")
    print(formatted)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"\nResult saved to: {args.out}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("OmniSight Vision Analyzer Module.")
        print("Usage: python vision_analyzer.py <path_to_screenshot> [--url URL] [--html HTML_FILE] [--mock]")
        print("To run automated test suite: python test_vision.py")
