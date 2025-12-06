from PIL import Image
import os

def create_banner_from_image():
    # Path to the generated image "Window View"
    # I found this path in my previous logs
    input_path = "/Users/mathieu/.gemini/antigravity/brain/7b9cae0b-3fb0-4084-9ba1-11dabe944cf5/edgerunners_mask_banner_hero_view_1764994128811.png"
    
    if not os.path.exists(input_path):
        print(f"Error: Could not find image at {input_path}")
        return

    img = Image.open(input_path)
    width, height = img.size
    print(f"Original size: {width}x{height}")

    # Twitch banner target: 1200x480 is a standard recommended size, or just a wide ratio (~2.5:1)
    # Since our image is likely 1024x1024, we want to crop a wide strip from the center (or slightly lower to catch the mask).
    
    # Let's aim for a 3:1 aspect ratio roughly, staying within the width 1024.
    # New width: 1024
    # New height: 1024 / 2.5 = ~410 px
    
    new_height = 410
    
    # Calculate crop area
    # We want to center it vertically around the mask. 
    # Usually the subject is centered or slightly below center in these gens.
    # For the hero shot, the mask is likely central.
    # We want a vertical center crop.
    
    top = (height - new_height) // 2
    
    left = 0
    right = width
    bottom = top + new_height
    
    banner = img.crop((left, top, right, bottom))
    
    output_path = "twitch_banner_hero_mask.png"
    banner.save(output_path)
    print(f"Banner generated: {output_path} ({width}x{new_height})")

if __name__ == "__main__":
    create_banner_from_image()
