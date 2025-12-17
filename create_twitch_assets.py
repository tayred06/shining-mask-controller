from PIL import Image
import os

def create_twitch_assets(source_path):
    try:
        if not os.path.exists(source_path):
            print(f"Error: Source file not found at {source_path}")
            return

        img = Image.open(source_path)
        width, height = img.size
        print(f"Original size: {width}x{height}")

        # 1. Avatar (Profile Picture) - 256x256 minimum, let's do 512x512
        # Center crop square
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        
        avatar = img.crop((left, top, right, bottom))
        avatar = avatar.resize((512, 512), Image.Resampling.LANCZOS)
        avatar.save("twitch_avatar_tayreddd.png")
        print("Created: twitch_avatar_tayreddd.png")

        # 2. Banner - 1200x480
        # Twitch banner is wide. We crop the center strip.
        target_ratio = 1200 / 480
        curr_ratio = width / height
        
        if curr_ratio > target_ratio:
            # Too wide, crop width
            new_width = height * target_ratio
            left = (width - new_width) / 2
            banner_crop = img.crop((left, 0, left + new_width, height))
        else:
            # Too tall, crop height
            new_height = width / target_ratio
            top = (height - new_height) / 2
            banner_crop = img.crop((0, top, width, top + new_height))
            
        banner = banner_crop.resize((1200, 480), Image.Resampling.LANCZOS)
        banner.save("twitch_banner_tayreddd.png")
        print("Created: twitch_banner_tayreddd.png")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Using the path of the generated image
    source = "/Users/mathieu/.gemini/antigravity/brain/7b9cae0b-3fb0-4084-9ba1-11dabe944cf5/twitch_branding_anime_master_1765077387449.png"
    create_twitch_assets(source)
