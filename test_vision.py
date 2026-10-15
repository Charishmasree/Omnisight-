"""OmniSight AI Module - Test Suite for Vision Analyzer.

Includes:
1. Automated unit and mock tests that run 100% offline without requiring an API key.
2. Mocking of Google Gemini GenAI Client to test the end-to-end VLM pipeline.
3. Interactive demo / live runner to analyze all images in sample_images/ and save analysis_results.json.

Can be run via:
- VS Code Test Explorer (natively discovers standard unittest test cases)
- Terminal: python -m unittest test_vision.py -v
- Terminal: python test_vision.py
- Live demo: python test_vision.py --demo
"""

import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch

# Ensure current directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from vision_analyzer import (
    analyze_screenshot,
    _clean_json_response,
    _generate_mock_analysis,
)
from prompts import (
    SYSTEM_PROMPT,
    UIAnalysisReport,
    JSON_SCHEMA,
    build_analysis_prompt,
)


class TestMockAnalysis(unittest.TestCase):
    """Offline unit tests verifying detection across each sample image category."""

    @classmethod
    def setUpClass(cls):
        cls.sample_dir = os.path.join(CURRENT_DIR, "sample_images")

    def test_mock_clipped_button(self):
        """Verifies clipped button detection and structured JSON output."""
        img_path = os.path.join(self.sample_dir, "2_clipped_button.png")
        result = analyze_screenshot(
            screenshot_path=img_path,
            html_content="<button id='checkout-button'>Proceed to Secure Checkout</button>",
            page_url="http://localhost:8000/cart",
            mock=True,
        )

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["element"], "#checkout-button")
        self.assertEqual(result["issue_type"], "clipped_button")
        self.assertEqual(result["severity"], "high")
        self.assertIn("clipped", result["description"].lower())
        self.assertTrue(len(result["suggested_css_fix"]) > 0)
        self.assertEqual(result["suggested_css_fix"], result["suggested_fix"])
        self.assertEqual(result["page_url"], "http://localhost:8000/cart")
        self.assertIsInstance(result["issues"], list)
        self.assertEqual(len(result["issues"]), 1)

    def test_mock_overlapping_elements(self):
        """Verifies overlapping text/container detection."""
        img_path = os.path.join(self.sample_dir, "3_overlapping_elements.png")
        result = analyze_screenshot(
            screenshot_path=img_path,
            html_content="<div class='promo-badge'>FLASH SALE</div><p>Description</p>",
            page_url="http://localhost:8000/deals",
            mock=True,
        )

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["issue_type"], "overlapping_text")
        self.assertEqual(result["severity"], "high")
        self.assertIn(".promo-badge", result["element"])
        self.assertTrue("suggested_css_fix" in result)

    def test_mock_misalignment(self):
        """Verifies misalignment detection."""
        img_path = os.path.join(self.sample_dir, "4_misalignment.png")
        result = analyze_screenshot(screenshot_path=img_path, mock=True)

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["issue_type"], "misalignment")
        self.assertIn("misaligned", result["description"].lower())

    def test_mock_missing_element(self):
        """Verifies missing element detection."""
        img_path = os.path.join(self.sample_dir, "5_missing_element.png")
        result = analyze_screenshot(screenshot_path=img_path, mock=True)

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["issue_type"], "missing_element")
        self.assertIn("missing", result["description"].lower())

    def test_mock_responsiveness_problem(self):
        """Verifies responsiveness overflow detection."""
        img_path = os.path.join(self.sample_dir, "6_responsiveness_problem.png")
        result = analyze_screenshot(screenshot_path=img_path, mock=True)

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["issue_type"], "responsiveness")
        self.assertEqual(result["severity"], "critical")
        self.assertIn("overflow", result["description"].lower())

    def test_mock_unreadable_contrast(self):
        """Verifies low contrast / unreadable text detection."""
        img_path = os.path.join(self.sample_dir, "7_unreadable_contrast.png")
        result = analyze_screenshot(screenshot_path=img_path, mock=True)

        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["issue_type"], "unreadable_text")
        self.assertIn("contrast", result["description"].lower())

    def test_mock_normal_ui(self):
        """Verifies clean UI returns issue_detected=False."""
        img_path = os.path.join(self.sample_dir, "1_normal_ui.png")
        result = analyze_screenshot(screenshot_path=img_path, mock=True)

        self.assertFalse(result["issue_detected"])
        self.assertEqual(result["issue_type"], "none")
        self.assertEqual(result["severity"], "none")
        self.assertEqual(result["suggested_css_fix"], "")
        self.assertEqual(len(result["issues"]), 0)


class TestFunctionSignaturesAndValidation(unittest.TestCase):
    """Tests function signatures, argument validation, and error conditions."""

    @classmethod
    def setUpClass(cls):
        cls.sample_img = os.path.join(CURRENT_DIR, "sample_images", "1_normal_ui.png")

    def test_accepts_screenshot_html_and_url_keyword(self):
        """Requirement 1: accepts webpage screenshot, HTML content, and page URL."""
        result = analyze_screenshot(
            screenshot_path=self.sample_img,
            html_content="<main><h1>Products</h1></main>",
            page_url="http://localhost:3000",
            mock=True,
        )
        self.assertEqual(result["page_url"], "http://localhost:3000")

    def test_accepts_positional_arguments(self):
        """Requirement 1: accepts screenshot, html, and url positionally."""
        result = analyze_screenshot(
            self.sample_img,
            "<section id='hero'></section>",
            "http://example.com/demo",
            mock=True,
        )
        self.assertEqual(result["page_url"], "http://example.com/demo")

    def test_backwards_compatible_image_path(self):
        """Accepts image_path as alias for screenshot_path."""
        result = analyze_screenshot(image_path=self.sample_img, mock=True)
        self.assertIn("screenshot_path", result)

    def test_missing_screenshot_path_raises_error(self):
        """Calling without a screenshot path must raise ValueError."""
        with self.assertRaises(ValueError):
            analyze_screenshot(screenshot_path=None, mock=True)

    def test_nonexistent_file_raises_filenotfound(self):
        """Calling with a non-existent file must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            analyze_screenshot(screenshot_path="sample_images/does_not_exist.png", mock=True)

    def test_missing_api_key_raises_helpful_error(self):
        """Calling without an API key (and mock=False) must raise a helpful ValueError."""
        # Ensure GEMINI_API_KEY is not in env for this test
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                analyze_screenshot(screenshot_path=self.sample_img, mock=False)
            self.assertIn("GEMINI_API_KEY is not set", str(ctx.exception))


class TestPromptAndSchema(unittest.TestCase):
    """Tests prompt generation and schema integrity."""

    def test_build_analysis_prompt_with_context(self):
        """Prompt builder includes URL and HTML snippet when provided."""
        html = "<button class='btn-pay'>Pay Now</button>"
        url = "https://shop.omnisight.dev/pay"
        prompt = build_analysis_prompt(html_content=html, page_url=url)

        self.assertIn("Page URL: https://shop.omnisight.dev/pay", prompt)
        self.assertIn("<button class='btn-pay'>Pay Now</button>", prompt)
        self.assertIn("clipped buttons", prompt)

    def test_build_analysis_prompt_without_context(self):
        """Prompt builder generates valid default prompt when context is absent."""
        prompt = build_analysis_prompt()
        self.assertNotIn("Page URL:", prompt)
        self.assertNotIn("```html", prompt)
        self.assertIn("visual layout defects", prompt)

    def test_html_truncation_for_large_dom(self):
        """Prompt builder truncates very large HTML snippets safely."""
        large_html = "<div>" + ("<p>item</p>" * 2000) + "</div>"
        prompt = build_analysis_prompt(html_content=large_html)
        self.assertIn("...[truncated for length]...", prompt)

    def test_clean_json_response_with_code_fences(self):
        """Helper cleans markdown code fences from LLM responses."""
        raw = "```json\n{\"issue_detected\": false}\n```"
        cleaned = _clean_json_response(raw)
        self.assertEqual(cleaned, '{"issue_detected": false}')

    def test_pydantic_schema_structure(self):
        """Verifies UIAnalysisReport schema contains all required fields."""
        fields = UIAnalysisReport.model_fields
        required_keys = [
            "issue_detected",
            "element",
            "issue_type",
            "severity",
            "description",
            "suggested_css_fix",
            "suggested_fix",
            "issues",
        ]
        for key in required_keys:
            self.assertIn(key, fields, f"Missing required field: {key}")


class TestGeminiClientIntegrationMocked(unittest.TestCase):
    """Mocks Google Gemini GenAI Client to test the live generation and parsing pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.sample_img = os.path.join(CURRENT_DIR, "sample_images", "2_clipped_button.png")

    @patch("google.genai.Client")
    def test_end_to_end_vlm_pipeline_with_mocked_client(self, mock_client_cls):
        """Tests that analyze_screenshot invokes GenAI client and parses response accurately."""
        # Simulated LLM response
        fake_llm_json = json.dumps({
            "issue_detected": True,
            "element": "#checkout-button",
            "issue_type": "clipped_button",
            "severity": "high",
            "description": "Button label 'Proceed to Secure Checkout' is cut off horizontally.",
            "suggested_css_fix": "width: auto; min-width: 140px; overflow: visible;",
            "suggested_fix": "width: auto; min-width: 140px; overflow: visible;",
            "issues": [{
                "element": "#checkout-button",
                "issue_type": "clipped_button",
                "severity": "high",
                "description": "Button label 'Proceed to Secure Checkout' is cut off horizontally.",
                "suggested_css_fix": "width: auto; min-width: 140px; overflow: visible;",
                "suggested_fix": "width: auto; min-width: 140px; overflow: visible;",
            }]
        })

        # Setup mock client instance
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = fake_llm_json
        mock_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_instance

        result = analyze_screenshot(
            screenshot_path=self.sample_img,
            html_content="<button id='checkout-button'>Checkout</button>",
            page_url="http://localhost:8000/cart",
            api_key="mock_test_key_12345",
            mock=False,
        )

        # Assert client was created with provided API key
        mock_client_cls.assert_called_once_with(api_key="mock_test_key_12345")

        # Assert generate_content was called
        mock_instance.models.generate_content.assert_called_once()
        call_kwargs = mock_instance.models.generate_content.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gemini-2.5-flash")

        # Assert parsed result matches requirements
        self.assertTrue(result["issue_detected"])
        self.assertEqual(result["element"], "#checkout-button")
        self.assertEqual(result["issue_type"], "clipped_button")
        self.assertEqual(result["severity"], "high")
        self.assertEqual(result["suggested_css_fix"], "width: auto; min-width: 140px; overflow: visible;")
        self.assertEqual(result["page_url"], "http://localhost:8000/cart")


def run_sample_analysis(use_live_api=False):
    """Analyzes all images in sample_images/ and saves output to analysis_results.json."""
    sample_dir = os.path.join(CURRENT_DIR, "sample_images")
    if not os.path.exists(sample_dir):
        print(f"Error: {sample_dir} directory not found.")
        return

    images = sorted([f for f in os.listdir(sample_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    if not images:
        print(f"No images found in {sample_dir}.")
        return

    api_key = os.getenv("GEMINI_API_KEY")
    is_live = use_live_api and bool(api_key)

    print("\n" + "=" * 65)
    print(" OmniSight - UI Screenshot Visual Analysis Runner")
    print(f" Mode: {'LIVE VLM (Google Gemini)' if is_live else 'MOCK / SIMULATION'}")
    if not is_live and use_live_api:
        print(" Note: GEMINI_API_KEY not found in environment. Falling back to mock mode.")
    print(f" Images Found: {len(images)}")
    print("=" * 65 + "\n")

    all_results = {}
    for filename in images:
        image_path = os.path.join(sample_dir, filename)
        print(f"--> Analyzing: {filename}")
        try:
            result = analyze_screenshot(
                screenshot_path=image_path,
                page_url=f"http://localhost:8000/{filename.split('.')[0]}",
                mock=not is_live,
            )
            all_results[filename] = result

            print(f"    Issue Detected: {result['issue_detected']}")
            print(f"    Element:        {result.get('element')}")
            print(f"    Issue Type:     {result.get('issue_type')}")
            print(f"    Severity:       {result.get('severity')}")
            print(f"    Description:    {result.get('description')[:75]}...")
            if result.get("suggested_css_fix"):
                print(f"    Suggested Fix:  {result.get('suggested_css_fix')[:75]}...")
            print("-" * 50)
        except Exception as e:
            print(f"    [ERROR] Failed to analyze {filename}: {e}")

    results_file = os.path.join(CURRENT_DIR, "analysis_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[DONE] Full analysis results successfully written to:")
    print(f"       {results_file}\n")


if __name__ == "__main__":
    # Check CLI flags
    if "--demo" in sys.argv or "--live" in sys.argv:
        live = "--live" in sys.argv
        run_sample_analysis(use_live_api=live)
    else:
        # Run test suite
        unittest.main(verbosity=2)
