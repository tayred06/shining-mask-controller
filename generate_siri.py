from PIL import Image, ImageDraw
import math

def create_siri_frame(frame_idx, total_frames):
    width = 84   # Doubled from 42
    height = 112 # Doubled from 56
    bg_color = (0, 0, 0)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    center_y = height // 2
    center_x = width // 2 # 42
    
    # Animation variables
    t = (frame_idx / total_frames) * 2 * math.pi
    
    # 1. Central Orb (Pulsing)
    pulse = (math.sin(t * 2) + 1) / 2 # 0 to 1
    orb_radius = 8 + (pulse * 6) # Doubled: 8 to 14
    orb_color = (200, 255, 255) # Bright white-cyan
    
    # Draw orb glow (fading circles)
    # Doubled offsets: 4 -> 8
    draw.ellipse([center_x - orb_radius - 8, center_y - orb_radius - 8, 
                  center_x + orb_radius + 8, center_y + orb_radius + 8], 
                 outline=(0, 50, 100), width=2)
    
    draw.ellipse([center_x - orb_radius, center_y - orb_radius, 
                  center_x + orb_radius, center_y + orb_radius], 
                 fill=orb_color)

    # 2. Waveforms (Siri style)
    # We draw lines across the width
    points_cyan = []
    points_blue = []
    points_purple = []
    
    for x in range(width):
        # Normalized x (-1 to 1)
        nx = (x - center_x) / center_x
        
        # Envelope to taper ends (so it fades at edges)
        envelope = 1 - (nx * nx)
        
        # Wave 1 (Cyan - Fast)
        # Amplitudes doubled: 10->20, 12->24, 8->16
        y1 = math.sin(x * 0.15 + t * 3) * 20 * envelope # Frequency halved for x to maintain shape
        points_cyan.append((x, center_y + y1))
        
        # Wave 2 (Blue - Slower)
        y2 = math.cos(x * 0.1 + t * 2) * 24 * envelope
        points_blue.append((x, center_y + y2))
        
        # Wave 3 (Purple/Pinkish - Offset)
        y3 = math.sin(x * 0.125 - t * 2) * 16 * envelope
        points_purple.append((x, center_y + y3))

    # Draw waves - Widths doubled
    draw.line(points_blue, fill=(0, 0, 255), width=2)
    draw.line(points_purple, fill=(100, 0, 200), width=2)
    draw.line(points_cyan, fill=(0, 255, 255), width=4) # Main wave thicker

    return img

def create_siri_animation():
    frames = []
    total_frames = 7 # As requested, 7 frames for the loop
    
    print(f"Generating {total_frames} frames...")
    
    for i in range(total_frames):
        img = create_siri_frame(i, total_frames)
        # Save individual frame
        filename = f"siri_frames/siri_frame_{i+1:02d}.png"
        img.save(filename)
        print(f"Saved {filename}")

    print("Done! 10 images generated in 'siri_frames/' folder.")

if __name__ == "__main__":
    create_siri_animation()
