#!/usr/bin/env python3
"""
Test script to verify logo file is readable for report generation
"""

import os
from PIL import Image
import io

def test_logo_file():
    """Test if the logo file is readable"""
    logo_path = "assets/logo.png"
    
    print(f"🔍 Testing logo file: {logo_path}")
    
    # Check if file exists
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(logo_path)
    print(f"📊 File size: {file_size} bytes")
    
    try:
        # Try to open with PIL
        with Image.open(logo_path) as img:
            print(f"✅ PIL can read the image")
            print(f"📊 Image format: {img.format}")
            print(f"📊 Image size: {img.size}")
            print(f"📊 Image mode: {img.mode}")
            
        # Try to read as bytes (like ReportLab does)
        with open(logo_path, 'rb') as f:
            image_data = f.read()
            print(f"✅ Can read as bytes: {len(image_data)} bytes")
            
        # Try to create BytesIO object (like ReportLab does)
        with open(logo_path, 'rb') as f:
            image_bytes = io.BytesIO(f.read())
            with Image.open(image_bytes) as img:
                print(f"✅ Can read from BytesIO")
                
        return True
        
    except Exception as e:
        print(f"❌ Error reading logo file: {str(e)}")
        return False

def create_simple_logo():
    """Create a simple logo if the current one is corrupted"""
    from PIL import Image, ImageDraw, ImageFont
    
    print("🔧 Creating a simple replacement logo...")
    
    # Create a simple logo
    width, height = 200, 100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple design
    draw.rectangle([10, 10, width-10, height-10], outline='blue', width=3)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.load_default()
        text = "HederaAuditAI"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill='blue', font=font)
    except:
        # Fallback without font
        draw.text((50, 40), "HederaAuditAI", fill='blue')
    
    # Save the logo
    logo_path = "assets/logo.png"
    img.save(logo_path, 'PNG')
    print(f"✅ Created new logo: {logo_path}")
    
    return True

if __name__ == "__main__":
    print("🚀 Testing logo file for report generation...")
    
    if test_logo_file():
        print("✅ Logo file is working correctly!")
    else:
        print("🔧 Logo file has issues, creating a replacement...")
        if create_simple_logo():
            print("✅ Replacement logo created successfully!")
            # Test the new logo
            if test_logo_file():
                print("✅ New logo is working correctly!")
            else:
                print("❌ Still having issues with logo file")
        else:
            print("❌ Failed to create replacement logo")
