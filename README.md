# OmniSight - AI/VLM Module (Week 1)

This module handles the Vision Language Model (VLM) analysis for the OmniSight project. It takes UI screenshots and returns structured JSON highlighting visual bugs such as clipping, overlapping, or unreadable text.

## Requirements

- Python 3.9+
- A valid Google Gemini API Key

## Installation

1. Open a terminal in the `ai` directory.
2. Install the required dependencies:
   ```bash
   pip install google-genai python-dotenv pillow pydantic
   ```

## Configuration

1. Create a `.env` file by copying the example:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and replace `your_gemini_api_key_here` with your actual Gemini API key.

## Usage & Testing

### 1. Generate Sample UI Images
Run the following script to generate 4 sample UI mockups (one normal, three with intentionally broken layouts) inside the `sample_images` directory.
```bash
python generate_test_images.py
```

### 2. Run the Vision Analyzer Test
Run the test script to pass the sample images to the VLM and view the analysis results.
```bash
python test_vision.py
```

The script will output the structured JSON responses to the terminal and also save them to `analysis_results.json` for review.

## Output Example

When a clipped button is detected, the VLM will return a structured response like:

```json
{
  "issue_detected": true,
  "element": "Confirm Purchase Button",
  "issue_type": "clipping",
  "severity": "high",
  "description": "The text 'Confirm Purchase Button' extends beyond the boundaries of the blue button container, causing it to be clipped.",
  "suggested_fix": "Increase the width of the button container or use text-overflow properties. Ensure padding accommodates text length."
}
```

## Integration Note
This module is built to be strictly independent for Week 1. In future weeks, Member 1 will pass Playwright screenshots directly to `vision_analyzer.py:analyze_screenshot()`.
