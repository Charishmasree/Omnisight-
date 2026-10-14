import os
from PIL import Image, ImageDraw, ImageFont

def create_sample_images():
    """Generates a few basic test UI mockups to test the vision analyzer."""
    os.makedirs("sample_images", exist_ok=True)
    
    # Image 1: Normal UI
    img = Image.new('RGB', (500, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 400, 160], fill=(0, 122, 255), outline=(0, 0, 0))
    draw.text((210, 125), "Checkout Button", fill=(255, 255, 255))
    img.save("sample_images/1_normal_ui.png")
    
    # Image 2: Button Clipping (Text cut off)
    img = Image.new('RGB', (500, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 180, 130], fill=(0, 122, 255), outline=(0, 0, 0))
    draw.text((105, 110), "Confirm Purchase Button", fill=(255, 255, 255))
    img.save("sample_images/2_button_clipping.png")
    
    # Image 3: Overlapping Elements
    img = Image.new('RGB', (500, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    # Box 1
    draw.rectangle([100, 100, 300, 180], fill=(255, 255, 255), outline=(200, 200, 200))
    draw.text((120, 130), "Product Description Info", fill=(0, 0, 0))
    # Box 2 overlapping Box 1
    draw.rectangle([250, 150, 450, 230], fill=(0, 122, 255), outline=(0, 0, 0))
    draw.text((270, 180), "Buy Now Overlap", fill=(255, 255, 255))
    img.save("sample_images/3_overlapping_elements.png")
    
    # Image 4: Unreadable text (Poor contrast)
    img = Image.new('RGB', (500, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 400, 160], fill=(245, 245, 245), outline=(230, 230, 230))
    # Light gray text on light gray background
    draw.text((220, 125), "Hidden Text", fill=(235, 235, 235))
    img.save("sample_images/4_unreadable_text.png")

    print("Created sample UI images in the 'sample_images' directory:")
    print(" - 1_normal_ui.png")
    print(" - 2_button_clipping.png")
    print(" - 3_overlapping_elements.png")
    print(" - 4_unreadable_text.png")

if __name__ == "__main__":
    create_sample_images()
