from PIL import Image, ImageDraw
import math

def draw_siri_style(draw, width, height, is_banner=False):
    center_x = width // 2
    center_y = height // 2
    
    # Scale factors based on width (approx)
    scale = width / 100 if not is_banner else height / 100
    
    # --- 1. Central Orb ---
    orb_radius = 20 * scale # Base radius scaled up
    
    # Outer Glow (Purple/Magenta)
    draw.ellipse([center_x - orb_radius - (10*scale), center_y - orb_radius - (10*scale),
                  center_x + orb_radius + (10*scale), center_y + orb_radius + (10*scale)],
                 outline=(180, 0, 255), width=int(3*scale)) 
    
    # Inner Glow (Cyan)
    draw.ellipse([center_x - orb_radius, center_y - orb_radius,
                  center_x + orb_radius, center_y + orb_radius],
                 outline=(0, 255, 255), width=int(4*scale))

    # Core (White)
    draw.ellipse([center_x - (8*scale), center_y - (8*scale),
                  center_x + (8*scale), center_y + (8*scale)],
                 fill=(255, 255, 255))
                 
    # --- 2. Curved Wave (The "Smile") ---
    points_top = []
    points_mid = []
    points_bot = []
    
    # For banner, we want the wave to go across the whole screen
    # For avatar, mostly the center part
    
    scan_width = width
    step = 5 # Optimize drawing
    
    dip_factor = 12 * scale # How deep the curve is
    if is_banner:
        dip_factor = 4 * scale # Flatter on banner
    
    for x in range(0, scan_width, step):
        # Normalized distance from center (0 to 1 at edges)
        dist = abs(x - center_x) / (width / 2) # Normalize by half-width to get 0..1 range
        
        # Curve calculation (Parabola)
        # y = center - (dist^2) * factor
        # This makes edges HIGHER than center (U shape)
        
        y_base = center_y + (10 * scale)
        
        # We want the line to be roughly at 'y_base' at the center, and curve UP outwards
        # So y = y_base - (dist^2) * dip
        y_curve = y_base - (dist ** 2) * dip_factor
        
        points_mid.append((x, y_curve))
        points_top.append((x, y_curve - (5*scale)))
        points_bot.append((x, y_curve + (5*scale)))

    # Draw the curves
    # Smooth line join not supported natively in simple PIL lines, but wide lines work okay
    draw.line(points_top, fill=(150, 0, 255), width=int(3*scale))
    draw.line(points_bot, fill=(150, 0, 255), width=int(3*scale))
    draw.line(points_mid, fill=(0, 200, 255), width=int(6*scale))


def generate_assets():
    # 1. Profile Picture (Square)
    p_size = 800
    img_profile = Image.new('RGB', (p_size, p_size), (0, 0, 0))
    draw_profile = ImageDraw.Draw(img_profile)
    
    draw_siri_style(draw_profile, p_size, p_size, is_banner=False)
    
    img_profile.save("twitch_profile_pic.png")
    print("Generated twitch_profile_pic.png")

    # 2. Banner (Rectangular)
    # Twitch banner recommended size ~1200x480
    b_w, b_h = 1920, 600
    img_banner = Image.new('RGB', (b_w, b_h), (0, 0, 0))
    draw_banner = ImageDraw.Draw(img_banner)
    
    draw_siri_style(draw_banner, b_w, b_h, is_banner=True)
    
    img_banner.save("twitch_banner.png")
    print("Generated twitch_banner.png")

if __name__ == "__main__":
    generate_assets()
