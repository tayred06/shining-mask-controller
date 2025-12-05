from PIL import Image, ImageDraw
import math
import os

def create_siri_curved_frame(frame_idx, total_frames):
    width = 84
    height = 103
    bg_color = (0, 0, 0)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    center_x = width // 2
    center_y = height // 2
    
    # Animation variable t (0 to 2pi)
    t = (frame_idx / total_frames) * 2 * math.pi
    
    # --- 1. Central Orb (Pulsing) ---
    # Pulse factor (-1 to 1)
    pulse = math.sin(t)
    
    # Radius varies between 14 and 18
    orb_radius = 16 + (pulse * 2) 
    
    # Outer Glow (Purple/Magenta)
    draw.ellipse([center_x - orb_radius - 8, center_y - orb_radius - 8,
                  center_x + orb_radius + 8, center_y + orb_radius + 8],
                 outline=(180, 0, 255), width=2) 
    
    # Inner Glow (Cyan)
    draw.ellipse([center_x - orb_radius, center_y - orb_radius,
                  center_x + orb_radius, center_y + orb_radius],
                 outline=(0, 255, 255), width=3)

    # Core (White)
    draw.ellipse([center_x - 6, center_y - 6,
                  center_x + 6, center_y + 6],
                 fill=(255, 255, 255))
                 
    # --- 2. Curved Wave (Floating) ---
    # The wave floats up and down slightly with the orb
    float_offset = pulse * 2 # Moves up/down by 2 pixels
    
    points_top = []
    points_mid = []
    points_bot = []
    
    for x in range(width):
        # Normalized distance from center (0 to 1)
        dist = abs(x - center_x) / center_x
        
        # Curve calculation
        y_base = center_y + 6 + float_offset
        # Reduced curve factor from 16 to 8 for a flatter line
        y_curve = y_base - (dist ** 2) * 8 
        
        points_mid.append((x, y_curve))
        points_top.append((x, y_curve - 4))
        points_bot.append((x, y_curve + 4))

    # Draw the curves
    draw.line(points_top, fill=(150, 0, 255), width=2)
    draw.line(points_bot, fill=(150, 0, 255), width=2)
    draw.line(points_mid, fill=(0, 200, 255), width=4)

    return img

def generate_animation():
    output_dir = "siri_curved_frames"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    total_frames = 7
    frames = []
    print(f"Generating {total_frames} frames in '{output_dir}'...")
    
    for i in range(total_frames):
        img = create_siri_curved_frame(i, total_frames)
        frames.append(img)
        
        filename = f"{output_dir}/frame_{i+1:02d}.png"
        img.save(filename)
        print(f"Saved {filename}")
    
    # Save GIF preview
    frames[0].save('siri_curved_preview.gif',
               save_all=True,
               append_images=frames[1:],
               optimize=False,
               duration=100, # 100ms per frame = 10fps
               loop=0)
    print("Generated GIF preview: siri_curved_preview.gif")
        
    print("Done!")

if __name__ == "__main__":
    generate_animation()
