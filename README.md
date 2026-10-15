# OmniSight – Member 2: AI Vision Integration (Week 2)

Automated visual and layout bug detection engine using Vision Language Models (VLM) such as **Google Gemini**.

This module accepts webpage screenshots, optional HTML/DOM snippets, and page URLs to detect visual anomalies—including **clipped buttons, overlapping text, misalignment, missing elements, responsiveness flaws, and low contrast**—and outputs structured JSON with actionable CSS repairs.

---

## Architecture & Integration

In the OmniSight multi-agent self-healing QA platform:
- **Member 1 (Automation)**: Playwright captures screenshots across desktop, tablet, and mobile viewports (`screenshots/before/`, `screenshots/responsive/`).
- **Member 2 (AI Vision - THIS MODULE)**: Analyzes screenshots with VLM and extracts structured diagnosis JSON with proposed CSS fixes.
- **Member 3 (Dashboard)**: Consumes the structured JSON to display visual bugs, comparison diffs, and proposed repairs in the QA Dashboard.

```
┌─────────────────────────────────┐
│ Member 1: Playwright Automation │ (Captures UI Screenshots & DOM)
└────────────────┬────────────────┘
                 │ screenshot.png, HTML, URL
                 ▼
┌─────────────────────────────────┐
│ Member 2: AI Vision Analyzer    │ (Analyzes with Google Gemini VLM)
└────────────────┬────────────────┘
                 │ Structured JSON (issue_type, severity, suggested_css_fix)
                 ▼
┌─────────────────────────────────┐
│ Member 3: QA React Dashboard    │ (Renders Issues, Diff Previews & Fixes)
└─────────────────────────────────┘
```

---

## File Structure

```
ai/
├── vision_analyzer.py       # Core analyze_screenshot() function & CLI interface
├── prompts.py               # VLM system prompt, Pydantic schemas, & prompt builder
├── test_vision.py           # Unit/mock test suite (19 tests) & batch demo runner
├── generate_test_images.py  # Image generator for 7 realistic UI defect mockups
├── sample_images/           # Pre-generated sample UI screenshots (PNG)
│   ├── 1_normal_ui.png              # Clean UI with proper alignment
│   ├── 2_clipped_button.png         # Button text truncated by boundary
│   ├── 3_overlapping_elements.png   # Promotional badge colliding with text
│   ├── 4_misalignment.png           # Form inputs with irregular offsets
│   ├── 5_missing_element.png        # Broken image placeholder & missing price
│   ├── 6_responsiveness_problem.png # 620px table overflowing 375px mobile screen
│   └── 7_unreadable_contrast.png    # Low contrast text failing WCAG AA
├── requirements.txt         # Module dependencies
├── .env.example             # Environment configuration template
├── .gitignore               # Excludes secrets (.env) and caches
└── README.md                # Documentation & execution guide
```

---

## Requirements & Prerequisites

- **Python**: Version 3.9 or higher (tested with Python 3.10 – 3.14)
- **Google Gemini API Key**: Free tier or paid key from [Google AI Studio](https://aistudio.google.com/app/apikey) (required for real VLM calls; mock tests run 100% offline without a key).

---

## Installation

1. Open your terminal in the `ai` directory:
   ```bash
   cd ai
   ```

2. (Optional but recommended) Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Or using `python -m pip install -r requirements.txt`)*

---

## Configuration & Secret Security

1. Copy the environment template:
   ```bash
   # Windows PowerShell / Command Prompt
   copy .env.example .env

   # macOS / Linux
   cp .env.example .env
   ```

2. Open `.env` and set your Gemini API key:
   ```env
   GEMINI_API_KEY=AIzaSy...YourActualKeyHere
   GEMINI_MODEL=gemini-2.5-flash
   ```

> [!IMPORTANT]
> **Security Notice**: Never commit `.env` or hardcode API keys into source files. The included `.gitignore` automatically prevents `.env` files from being committed to version control.

---

## How to Run Tests in VS Code

You can run the automated tests in VS Code using either the **Test Explorer GUI** or the **Integrated Terminal**.

### Method 1: VS Code Test Explorer GUI

1. Open the OmniSight project folder in VS Code.
2. Click the **Testing** icon (beaker icon) in the left activity bar.
3. If tests are not automatically configured, click **Configure Python Tests**:
   - Select **unittest** as the test framework.
   - Select the `ai` directory (or root).
   - Select pattern `test_*.py`.
4. VS Code will discover all 19 test cases in `test_vision.py`.
5. Click the **Play** button next to `test_vision.py` or any individual test case to execute.
6. Green checkmarks indicate passing tests.

### Method 2: VS Code Integrated Terminal (Recommended)

1. Open the integrated terminal in VS Code (`Ctrl + \`` or `Terminal` -> `New Terminal`).
2. Navigate to the `ai` directory:
   ```bash
   cd ai
   ```
3. Run the test suite:
   ```bash
   python -m unittest test_vision.py -v
   ```
   Or:
   ```bash
   python test_vision.py
   ```

All 19 tests will run and complete in under 1 second without requiring an API key.

---

## How to Run a Real VLM Analysis

### Option A: From Python Code

Import and call `analyze_screenshot()` in your automation script:

```python
from vision_analyzer import analyze_screenshot

# Full call with screenshot, HTML DOM context, and page URL
result = analyze_screenshot(
    screenshot_path="sample_images/2_clipped_button.png",
    html_content="<button id='checkout-button' class='btn-primary'>Proceed to Secure Checkout</button>",
    page_url="http://localhost:8000/cart"
)

print(result)
```

### Option B: From the Command Line Interface (CLI)

Run `vision_analyzer.py` directly on any screenshot:

```bash
# Real analysis using Google Gemini (requires GEMINI_API_KEY in .env)
python vision_analyzer.py sample_images/2_clipped_button.png --url "http://localhost:8000/cart"

# Real analysis with optional HTML snippet
python vision_analyzer.py sample_images/2_clipped_button.png --url "http://localhost:8000/cart" --html snippet.html

# Save output directly to a JSON file
python vision_analyzer.py sample_images/2_clipped_button.png --out result.json

# Offline / Mock mode (does not call API)
python vision_analyzer.py sample_images/2_clipped_button.png --mock
```

### Option C: Batch Sample Runner

Analyze all 7 mockups in `sample_images/` in one command:

```bash
# Run with live Gemini VLM (requires GEMINI_API_KEY)
python test_vision.py --live

# Run in simulation/mock mode (no API key needed)
python test_vision.py --demo
```

---

## How to View the JSON Output

1. **In the Terminal**: Output is formatted with 2-space indentation and printed to stdout.
2. **In `analysis_results.json`**: When running `python test_vision.py --demo` or `--live`, all results are aggregated into `ai/analysis_results.json`. Open this file in VS Code (`Ctrl + P` -> `analysis_results.json`) and format with `Shift + Alt + F`.

---

## Sample JSON Outputs

### 1. Clipped Button Detected (`sample_images/2_clipped_button.png`)

```json
{
  "issue_detected": true,
  "element": "#checkout-button",
  "issue_type": "clipped_button",
  "severity": "high",
  "description": "The button label text 'Proceed to Secure Checkout' exceeds container width (100px) and is horizontally clipped.",
  "suggested_css_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;",
  "suggested_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;",
  "issues": [
    {
      "element": "#checkout-button",
      "issue_type": "clipped_button",
      "severity": "high",
      "description": "The button label text 'Proceed to Secure Checkout' exceeds container width (100px) and is horizontally clipped.",
      "suggested_css_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;",
      "suggested_fix": "width: auto; min-width: 140px; padding: 10px 18px; white-space: normal; overflow: visible;"
    }
  ],
  "page_url": "http://localhost:8000/cart",
  "screenshot_path": "sample_images/2_clipped_button.png",
  "analyzed_at": "2026-10-15T01:49:03.983347+00:00"
}
```

### 2. Responsiveness Horizontal Overflow (`sample_images/6_responsiveness_problem.png`)

```json
{
  "issue_detected": true,
  "element": ".order-summary-table",
  "issue_type": "responsiveness",
  "severity": "critical",
  "description": "The order summary table has a fixed width (620px) that exceeds the 375px mobile viewport width, causing severe horizontal overflow.",
  "suggested_css_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;",
  "suggested_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;",
  "issues": [
    {
      "element": ".order-summary-table",
      "issue_type": "responsiveness",
      "severity": "critical",
      "description": "The order summary table has a fixed width (620px) that exceeds the 375px mobile viewport width, causing severe horizontal overflow.",
      "suggested_css_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;",
      "suggested_fix": "width: 100%; max-width: 100%; overflow-x: auto; display: block;"
    }
  ],
  "page_url": "http://localhost:8000/checkout",
  "screenshot_path": "sample_images/6_responsiveness_problem.png",
  "analyzed_at": "2026-10-15T01:49:03.987740+00:00"
}
```

### 3. Normal UI – No Issues Detected (`sample_images/1_normal_ui.png`)

```json
{
  "issue_detected": false,
  "element": "None",
  "issue_type": "none",
  "severity": "none",
  "description": "No visual layout issues or responsiveness defects detected. The page layout, contrast, and element alignment conform to standards.",
  "suggested_css_fix": "",
  "suggested_fix": "",
  "issues": [],
  "page_url": "http://localhost:8000/shop",
  "screenshot_path": "sample_images/1_normal_ui.png",
  "analyzed_at": "2026-10-15T01:49:03.981334+00:00"
}
```

---

## Output Schema Field Reference

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `issue_detected` | `boolean` | `true` if one or more UI bugs were detected; `false` if the layout is clean. | `true` |
| `element` | `string` | CSS selector or identifier of the problematic UI element (`"None"` if clean). | `"#checkout-button"` |
| `issue_type` | `string` | Defect category: `clipped_button`, `overlapping_text`, `misalignment`, `missing_element`, `responsiveness`, `unreadable_text`, or `none`. | `"clipped_button"` |
| `severity` | `string` | Impact level: `low`, `medium`, `high`, `critical`, or `none`. | `"high"` |
| `description` | `string` | Diagnostic explanation of the defect and why it degrades user experience. | `"Button label exceeds container..."` |
| `suggested_css_fix` | `string` | Proposed CSS declarations/rules to repair the visual defect. | `"width: auto; overflow: visible;"` |
| `suggested_fix` | `string` | Direct alias for `suggested_css_fix` ensuring compatibility with Member 3 dashboard. | `"width: auto; overflow: visible;"` |
| `issues` | `array` | List of all individual issues identified in the screenshot. | `[{ "element": ... }]` |
| `page_url` | `string` | URL of the page analyzed. | `"http://localhost:8000/cart"` |
| `screenshot_path` | `string` | File system path to the screenshot image analyzed. | `"sample_images/2_clipped_button.png"` |
| `analyzed_at` | `string` | ISO 8601 UTC timestamp of the analysis execution. | `"2026-10-15T01:49:03Z"` |

---

## Regenerating Sample Images

To generate or regenerate the sample UI mockup screenshots:
```bash
python generate_test_images.py
```
This script creates 7 high-resolution PNG mockups inside the `sample_images/` folder representing all supported issue categories.
