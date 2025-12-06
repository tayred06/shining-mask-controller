from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def add_text_to_banner():
    # Path to the "Wired" image generated previously
    input_path = "/Users/mathieu/.gemini/antigravity/brain/7b9cae0b-3fb0-4084-9ba1-11dabe944cf5/edgerunners_banner_wired_connection_1764994250820.png"
    
    if not os.path.exists(input_path):
        print(f"Error: Could not find image at {input_path}")
        return

    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Create a separate layer for the text to apply glow
    text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    text = "tayreddd"
    
    # Try to load a pixel font or monospaced font if available, otherwise default
    # MacOS usually has some fonts. Let's try to find a bold one.
    try:
        # A standard bold font
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 80)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        except:
            font = ImageFont.load_default() # Fallback, might be small
            print("Using default font (might be small)")

    # Calculate text position to center it on the mask
    # In the "Wired" image, the mask is roughly central.
    # We'll estimate the position.
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (width - text_w) // 2
    y = (height - text_h) // 2 - 20 # Slightly up
    
    # Draw "Glow" layers
    # Green neon glow
    glow_color = (0, 255, 128, 100) # Semi-transparent distinctive green
    core_color = (200, 255, 230, 255) # Almost white core
    
    # 1. Broad outer glow (blurred text)
    draw.text((x, y), text, font=font, fill=glow_color)
    glow_layer = text_layer.filter(ImageFilter.GaussianBlur(radius=15))
    
    # 2. Stronger inner glow
    text_layer_2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(text_layer_2)
    draw2.text((x, y), text, font=font, fill=(0, 255, 0, 200)) # Pure green
    glow_layer_2 = text_layer_2.filter(ImageFilter.GaussianBlur(radius=5))
    
    # 3. Solid Core
    text_layer_3 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw3 = ImageDraw.Draw(text_layer_3)
    draw3.text((x, y), text, font=font, fill=core_color)
    
    # Composite all layers
    # Original Image + Broad Glow + Tight Glow + Core
    final = Image.alpha_composite(img, glow_layer)
    final = Image.alpha_composite(final, glow_layer_2)
    final = Image.alpha_composite(final, text_layer_3)
    
    # Crop to banner format while we are at it
    banner_h = 410
    crop_top = (height - banner_h) // 2
    final_banner = final.crop((0, crop_top, width, crop_top + banner_h))
    
    output_path = "twitch_banner_wired_tayreddd.png"
    final_banner.save(output_path)
    print(f"Generated banner with text: {output_path}")

if __name__ == "__main__":
    add_text_to_banner()
