from PIL import Image, ImageEnhance, ImageFilter
import os

def enhance_banner():
    # Previous best source
    source_path = "/Users/mathieu/.gemini/antigravity/brain/7b9cae0b-3fb0-4084-9ba1-11dabe944cf5/twitch_branding_wide_1764997501795.png"
    
    if not os.path.exists(source_path):
        print("Source file not found.")
        return

    img = Image.open(source_path)
    width, height = img.size
    
    # Crop logic for Banner (Wide)
    target_width = 1200
    target_height = 480
    target_ratio = target_width / target_height
    
    curr_ratio = width / height
    
    # We want to keep the center, but maybe zoom in slightly less than before to keep resolution?
    # Actually, to fill 1200px from 1024px source, we MUST upscale.
    
    if curr_ratio > target_ratio:
        new_width = height * target_ratio
        left = (width - new_width) / 2
        banner_crop = img.crop((left, 0, left + new_width, height))
    else:
        new_height = width / target_ratio
        top = (height - new_height) / 2
        banner_crop = img.crop((0, top, width, top + new_height))
    
    # High Quality Resize (Bicubic gives smoother results than Lanczos sometimes for art, but let's try Lanczos + Sharpen)
    banner = banner_crop.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Enhance Sharpness slightly to combat upscale blur
    enhancer = ImageEnhance.Sharpness(banner)
    banner_sharp = enhancer.enhance(1.3) # Boost sharpness by 30%
    
    # Enhance Contrast slightly for "Cyberpunk" pop
    contrast = ImageEnhance.Contrast(banner_sharp)
    banner_final = contrast.enhance(1.1)

    output_filename = "twitch_banner_hq.png"
    banner_final.save(output_filename, quality=100, optimize=True)
    print(f"Created high quality banner: {output_filename}")

if __name__ == "__main__":
    enhance_banner()
