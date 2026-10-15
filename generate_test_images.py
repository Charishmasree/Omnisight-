import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size=14, bold=False):
    """Attempt to load a clean system TrueType font, falling back to default."""
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()

def create_sample_images(output_dir="sample_images"):
    """
    Generates realistic UI test mockups demonstrating various UI/UX issues:
    1. Normal UI (no issues)
    2. Clipped Button (text truncated by button boundaries)
    3. Overlapping Elements (text/containers colliding)
    4. Misalignment (jagged, off-grid inputs & elements)
    5. Missing Element (broken image placeholder & missing content)
    6. Responsiveness Problem (fixed-width desktop card overflowing mobile viewport)
    7. Unreadable Contrast (light gray text on light gray background)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    font_title = get_font(20, bold=True)
    font_heading = get_font(16, bold=True)
    font_body = get_font(14, bold=False)
    font_small = get_font(11, bold=False)
    font_btn = get_font(13, bold=True)

    # -------------------------------------------------------------
    # 1. Normal UI (Clean, accessible, balanced)
    # -------------------------------------------------------------
    img = Image.new("RGB", (700, 420), color="#f8fafc")
    draw = ImageDraw.Draw(img)
    # Topbar
    draw.rectangle([0, 0, 700, 60], fill="#0f172a")
    draw.text((24, 18), "OmniSight E-Commerce", fill="#ffffff", font=font_title)
    draw.text((450, 22), "Home", fill="#94a3b8", font=font_body)
    draw.text((510, 22), "Products", fill="#38bdf8", font=font_body)
    draw.text((600, 22), "Cart (2)", fill="#94a3b8", font=font_body)
    # Page Heading
    draw.text((30, 85), "Featured Products", fill="#1e293b", font=font_heading)
    # Product Card 1
    draw.rectangle([30, 120, 330, 370], fill="#ffffff", outline="#cbd5e1", width=1)
    draw.rectangle([45, 135, 315, 240], fill="#e2e8f0")
    draw.text((120, 180), "[Product Image]", fill="#64748b", font=font_body)
    draw.text((45, 255), "Wireless Noise-Canceling Headphones", fill="#0f172a", font=font_heading)
    draw.text((45, 285), "Category: Audio  |  In Stock", fill="#64748b", font=font_small)
    draw.text((45, 320), "$149.99", fill="#0284c7", font=font_heading)
    draw.rectangle([210, 312, 315, 348], fill="#0284c7")
    draw.text((225, 322), "Add to Cart", fill="#ffffff", font=font_btn)
    # Product Card 2
    draw.rectangle([360, 120, 660, 370], fill="#ffffff", outline="#cbd5e1", width=1)
    draw.rectangle([375, 135, 645, 240], fill="#e2e8f0")
    draw.text((450, 180), "[Product Image]", fill="#64748b", font=font_body)
    draw.text((375, 255), "Smart Fitness Tracker Watch", fill="#0f172a", font=font_heading)
    draw.text((375, 285), "Category: Wearables  |  In Stock", fill="#64748b", font=font_small)
    draw.text((375, 320), "$89.99", fill="#0284c7", font=font_heading)
    draw.rectangle([540, 312, 645, 348], fill="#0284c7")
    draw.text((555, 322), "Add to Cart", fill="#ffffff", font=font_btn)
    
    path1 = os.path.join(output_dir, "1_normal_ui.png")
    img.save(path1)

    # -------------------------------------------------------------
    # 2. Clipped Button (Text cut off inside button)
    # -------------------------------------------------------------
    img = Image.new("RGB", (600, 360), color="#f8fafc")
    draw = ImageDraw.Draw(img)
    # Header
    draw.rectangle([0, 0, 600, 50], fill="#1e293b")
    draw.text((20, 15), "Shopping Cart Summary", fill="#ffffff", font=font_heading)
    # Content Box
    draw.rectangle([40, 80, 560, 320], fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((60, 105), "Subtotal (3 items):", fill="#475569", font=font_body)
    draw.text((450, 105), "$279.98", fill="#0f172a", font=font_heading)
    draw.text((60, 140), "Estimated Shipping:", fill="#475569", font=font_body)
    draw.text((475, 140), "FREE", fill="#16a34a", font=font_heading)
    draw.line([(60, 180), (540, 180)], fill="#e2e8f0", width=1)
    draw.text((60, 200), "Total Payable:", fill="#0f172a", font=font_heading)
    draw.text((440, 200), "$279.98", fill="#0284c7", font=font_heading)
    
    # Intentionally clipped button: container width is 110px but text is long!
    # Clip mask simulation
    draw.text((60, 245), "Checkout Action:", fill="#64748b", font=font_small)
    btn_box = [60, 265, 160, 305]  # Only 100px wide
    draw.rectangle(btn_box, fill="#2563eb")
    # Draw button text that overflows boundary
    button_img = Image.new("RGBA", (100, 40), (37, 99, 235, 255))
    b_draw = ImageDraw.Draw(button_img)
    b_draw.text((10, 10), "Proceed to Secure Checkout", fill="#ffffff", font=font_btn)
    img.paste(button_img, (60, 265))
    # Red visual marker highlighting the clipping
    draw.rectangle([158, 263, 162, 307], outline="#ef4444", width=2)
    
    path2 = os.path.join(output_dir, "2_clipped_button.png")
    img.save(path2)

    # -------------------------------------------------------------
    # 3. Overlapping Elements (Banner colliding with text)
    # -------------------------------------------------------------
    img = Image.new("RGB", (650, 380), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 620, 350], fill="#f8fafc", outline="#cbd5e1", width=1)
    draw.text((50, 50), "Special Holiday Offer Details", fill="#0f172a", font=font_heading)
    
    # Text block that gets overlapped
    draw.text((50, 95), "Get an extra 20% discount on all electronics this weekend only.", fill="#334155", font=font_body)
    draw.text((50, 125), "Use promo code HOLIDAY20 during checkout. Standard terms apply.", fill="#334155", font=font_body)
    draw.text((50, 155), "Eligible products include laptops, headphones, smartwatches and accessories.", fill="#334155", font=font_body)
    draw.text((50, 185), "Orders placed before 5 PM ship the same business day with tracking.", fill="#334155", font=font_body)

    # Overlapping Badge/Card intentionally positioned right over lines 2 and 3
    draw.rectangle([180, 130, 480, 220], fill="#dc2626", outline="#991b1b", width=2)
    draw.text((210, 145), "FLASH SALE: 50% OFF TODAY!", fill="#ffffff", font=font_heading)
    draw.text((230, 175), "LIMITED TIME PROMOTION", fill="#fef08a", font=font_btn)
    
    path3 = os.path.join(output_dir, "3_overlapping_elements.png")
    img.save(path3)

    # -------------------------------------------------------------
    # 4. Misalignment (Uneven form fields & broken layout)
    # -------------------------------------------------------------
    img = Image.new("RGB", (600, 420), color="#f1f5f9")
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 20, 570, 400], fill="#ffffff", outline="#cbd5e1")
    draw.text((50, 40), "Customer Checkout Details", fill="#0f172a", font=font_heading)

    # Form field 1: Full Name (aligned at x=60)
    draw.text((60, 85), "Full Name *", fill="#334155", font=font_body)
    draw.rectangle([60, 110, 320, 145], outline="#94a3b8")
    draw.text((70, 120), "Jane Doe", fill="#0f172a", font=font_body)

    # Form field 2: Email (severely misaligned at x=140 instead of x=60)
    draw.text((140, 160), "Email Address *", fill="#334155", font=font_body)
    draw.rectangle([140, 185, 450, 220], outline="#94a3b8")
    draw.text((150, 195), "jane.doe@example.com", fill="#0f172a", font=font_body)

    # Form field 3: Address (misaligned at x=40)
    draw.text((40, 235), "Shipping Address *", fill="#334155", font=font_body)
    draw.rectangle([40, 260, 520, 295], outline="#94a3b8")
    draw.text((50, 270), "123 Innovation Way, Suite 400", fill="#0f172a", font=font_body)

    # Submit button (skewed to the far left edge instead of aligned with form)
    draw.rectangle([40, 330, 180, 370], fill="#0284c7")
    draw.text((60, 342), "Save & Continue", fill="#ffffff", font=font_btn)

    path4 = os.path.join(output_dir, "4_misalignment.png")
    img.save(path4)

    # -------------------------------------------------------------
    # 5. Missing Element (Broken image & missing content block)
    # -------------------------------------------------------------
    img = Image.new("RGB", (600, 380), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 30, 560, 350], fill="#f8fafc", outline="#e2e8f0")
    draw.text((60, 50), "Product Specification Sheet", fill="#0f172a", font=font_heading)
    
    # Broken Image Placeholder
    draw.rectangle([60, 90, 240, 260], fill="#fef2f2", outline="#ef4444", width=2)
    draw.line([(60, 90), (240, 260)], fill="#ef4444", width=2)
    draw.line([(60, 260), (240, 90)], fill="#ef4444", width=2)
    draw.text((75, 275), "ERR: Image not found", fill="#dc2626", font=font_small)

    # Product details with missing price element
    draw.text((270, 95), "Ultra-Slim Wireless Keyboard", fill="#0f172a", font=font_heading)
    draw.text((270, 130), "Connectivity: Bluetooth 5.2 / 2.4GHz", fill="#64748b", font=font_body)
    draw.text((270, 160), "Battery Life: Up to 90 days", fill="#64748b", font=font_body)
    # Price is completely missing! Just empty box
    draw.rectangle([270, 200, 420, 240], fill="#f1f5f9", outline="#94a3b8", width=1)
    draw.text((280, 212), "[Missing Price Data]", fill="#94a3b8", font=font_small)

    draw.rectangle([270, 260, 400, 300], fill="#94a3b8")
    draw.text((295, 272), "Unavailable", fill="#ffffff", font=font_btn)

    path5 = os.path.join(output_dir, "5_missing_element.png")
    img.save(path5)

    # -------------------------------------------------------------
    # 6. Responsiveness Problem (Mobile Viewport Horizontal Overflow)
    # -------------------------------------------------------------
    # Canvas represents a 375px mobile device screen, with 80px margins
    img = Image.new("RGB", (500, 450), color="#0f172a")
    draw = ImageDraw.Draw(img)
    # Device frame: 375px wide (x=60 to x=435)
    draw.rectangle([60, 20, 435, 430], fill="#ffffff", outline="#64748b", width=2)
    draw.text((75, 30), "Mobile View (375px)", fill="#64748b", font=font_small)
    draw.rectangle([75, 55, 420, 90], fill="#1e293b")
    draw.text((90, 65), "Checkout Table", fill="#ffffff", font=font_heading)

    # Table that extends beyond the mobile viewport (overflows to x=600!)
    table_x1, table_x2 = 75, 620
    draw.rectangle([table_x1, 110, table_x2, 220], fill="#f8fafc", outline="#cbd5e1")
    draw.rectangle([table_x1, 110, table_x2, 140], fill="#e2e8f0")
    draw.text((85, 118), "Item ID", fill="#334155", font=font_small)
    draw.text((170, 118), "Description", fill="#334155", font=font_small)
    draw.text((320, 118), "Unit Price", fill="#334155", font=font_small)
    draw.text((420, 118), "Tax (10%)", fill="#334155", font=font_small)
    draw.text((520, 118), "Final Total", fill="#334155", font=font_small)

    draw.text((85, 155), "#1001", fill="#0f172a", font=font_small)
    draw.text((170, 155), "Noise Canceling Headphones", fill="#0f172a", font=font_small)
    draw.text((320, 155), "$149.99", fill="#0f172a", font=font_small)
    draw.text((420, 155), "$15.00", fill="#0f172a", font=font_small)
    draw.text((520, 155), "$164.99", fill="#0f172a", font=font_small)

    # Highlight viewport edge with a red dashed indicator
    draw.line([(435, 20), (435, 430)], fill="#ef4444", width=2)
    draw.text((440, 230), "<- Viewport Cutoff", fill="#ef4444", font=font_small)

    path6 = os.path.join(output_dir, "6_responsiveness_problem.png")
    img.save(path6)

    # -------------------------------------------------------------
    # 7. Unreadable Contrast (Low contrast text)
    # -------------------------------------------------------------
    img = Image.new("RGB", (600, 320), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 30, 560, 290], fill="#f5f5f5", outline="#e5e5e5")
    draw.text((60, 50), "Terms & Privacy Notice", fill="#1f2937", font=font_heading)

    # Illegible low-contrast text: #d4d4d4 on #f5f5f5
    draw.text((60, 100), "By clicking 'Agree & Submit', you acknowledge that you have read and agree", fill="#d4d4d4", font=font_body)
    draw.text((60, 125), "to our Terms of Service and Privacy Policy. All transactions are securely encrypted.", fill="#d4d4d4", font=font_body)
    draw.text((60, 150), "You may opt out of marketing communications at any time in your profile.", fill="#d4d4d4", font=font_body)
    
    # Button with faint text
    draw.rectangle([60, 190, 220, 230], fill="#e5e5e5")
    draw.text((80, 202), "Agree & Continue", fill="#d1d5db", font=font_btn)

    path7 = os.path.join(output_dir, "7_unreadable_contrast.png")
    img.save(path7)

    created = [path1, path2, path3, path4, path5, path6, path7]
    print(f"Generated {len(created)} sample UI images in '{output_dir}/':")
    for p in created:
        print(f" - {os.path.basename(p)}")
    return created

if __name__ == "__main__":
    create_sample_images()
