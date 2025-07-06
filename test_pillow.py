#!/usr/bin/env python3
"""
Test if Pillow is working correctly in the virtual environment
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import io
    from datetime import datetime

    print("✅ PIL import successful")

    # Create a simple test image
    width, height = 640, 480
    img = Image.new('RGB', (width, height), color='#27ae60')
    draw = ImageDraw.Draw(img)

    print("✅ Image creation successful")

    # Try to get default font
    try:
        font = ImageFont.load_default()
        print("✅ Default font loaded")
    except Exception as e:
        print(f"⚠️ Font loading failed: {e}")
        font = None

    # Draw some text
    text = "Test Image"
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    else:
        text_width = len(text) * 8

    x = (width - text_width) // 2
    y = height // 2

    draw.text((x, y), text, fill='white', font=font)
    print("✅ Text drawing successful")

    # Convert to JPEG bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)

    print(f"✅ JPEG conversion successful - {len(img_byte_arr.getvalue())} bytes")
    print("✅ Pillow is working correctly!")

except ImportError as e:
    print(f"❌ PIL import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
