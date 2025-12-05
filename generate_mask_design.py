from PIL import Image, ImageDraw, ImageFont

def create_mask_design(design_type="tech_friendly"):
    width = 84
    height = 103
    bg_color = (0, 0, 0)
    feature_color = (0, 255, 255) # Cyan
    white = (255, 255, 255)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    center_x = width // 2
    
    if design_type == "tech_friendly":
        # Eyes - Adjusted for 84x103
        # Eyes need to be positioned where they would be on a face
        eye_y = 30
        eye_width = 20
        eye_height = 24
        eye_spacing = 10
        
        left_eye_x = center_x - eye_spacing - eye_width
        right_eye_x = center_x + eye_spacing
        
        # Draw Tech Eyes (Octagonal/Rounded Rect)
        def draw_oct_eye(x, y, w, h):
            # Main body
            draw.rectangle([x+4, y, x+w-4, y+h], fill=feature_color)
            draw.rectangle([x, y+4, x+w, y+h-4], fill=feature_color)
            # Corners
            draw.rectangle([x+2, y+2, x+w-2, y+h-2], fill=feature_color)
            
            # Pupil
            pupil_size = 8
            px = x + (w - pupil_size) // 2
            py = y + (h - pupil_size) // 2
            draw.rectangle([px, py, px+pupil_size, py+pupil_size], fill=white)

        draw_oct_eye(left_eye_x, eye_y, eye_width, eye_height)
        draw_oct_eye(right_eye_x, eye_y, eye_width, eye_height)
        
        # Mouth - Waveform Style
        mouth_y = 75
        
        # Waveform pattern
        #   |   |   |   |   |
        heights = [4, 6, 10, 6, 4]
        spacing = 6
        
        # Center bar
        draw.line([center_x, mouth_y - 12, center_x, mouth_y + 12], fill=feature_color, width=4)
        
        for i, h in enumerate(heights):
            offset = (i + 1) * spacing
            # Left
            draw.line([center_x - offset, mouth_y - h, center_x - offset, mouth_y + h], fill=feature_color, width=3)
            # Right
            draw.line([center_x + offset, mouth_y - h, center_x + offset, mouth_y + h], fill=feature_color, width=3)

    elif design_type == "siri_abstract":
        # Simple & Elegant Colorful Style
        center_y = height // 2
        orb_radius = 16
        
        # 1. Central Orb (Clean & Bright)
        # Outer Glow (Purple/Magenta for warmth)
        draw.ellipse([center_x - orb_radius - 8, center_y - orb_radius - 8,
                      center_x + orb_radius + 8, center_y + orb_radius + 8],
                     outline=(180, 0, 255), width=2) 
        
        # Inner Glow (Cyan for tech feel)
        draw.ellipse([center_x - orb_radius, center_y - orb_radius,
                      center_x + orb_radius, center_y + orb_radius],
                     outline=(0, 255, 255), width=3)

        # Core (White)
        draw.ellipse([center_x - 6, center_y - 6,
                      center_x + 6, center_y + 6],
                     fill=(255, 255, 255))
                     
        # 2. Single Elegant Wave
        # A thick, smooth wave that flows through the center
        # We simulate a gradient by drawing a few lines close together
        
        y_wave = center_y
        
        # Draw a "thick" wave using multiple lines
        # Top part (Purple)
        draw.line([0, y_wave - 4, width, y_wave - 4], fill=(150, 0, 255), width=2)
        # Middle part (Cyan/Blue mix)
        draw.line([0, y_wave, width, y_wave], fill=(0, 200, 255), width=4)
        # Bottom part (Purple)
        draw.line([0, y_wave + 4, width, y_wave + 4], fill=(150, 0, 255), width=2)
        
        # No extra clutter at the bottom. Just pure energy.

    elif design_type == "siri_curved":
        # Curved Colorful Siri Style (U-shape)
        center_y = height // 2
        orb_radius = 16
        
        # 1. Central Orb (Same as before)
        draw.ellipse([center_x - orb_radius - 8, center_y - orb_radius - 8,
                      center_x + orb_radius + 8, center_y + orb_radius + 8],
                     outline=(180, 0, 255), width=2) 
        
        draw.ellipse([center_x - orb_radius, center_y - orb_radius,
                      center_x + orb_radius, center_y + orb_radius],
                     outline=(0, 255, 255), width=3)

        draw.ellipse([center_x - 6, center_y - 6,
                      center_x + 6, center_y + 6],
                     fill=(255, 255, 255))
                     
        # 2. Curved Wave (U-shape)
        # We calculate points for a parabola: y = a(x-h)^2 + k
        # Vertex (h, k) is at (center_x, center_y + dip)
        
        dip = 8 # How much it curves down
        k = center_y + dip
        h = center_x
        # We want it to hit roughly center_y at the edges (x=0)
        # center_y = a(0 - center_x)^2 + center_y + dip
        # 0 = a*center_x^2 + dip  => a = -dip / center_x^2  (Wait, this makes it frown (n shape))
        # We want U shape. So edges should be higher (smaller y) than center.
        # Let vertex be at center_y + dip (lowest point).
        # Edges at center_y - dip (higher point).
        # y_edge = a(edge_x - h)^2 + k
        # (center_y - dip) = a(0 - center_x)^2 + (center_y + dip)
        # -2*dip = a * center_x^2
        # a = -2*dip / center_x^2
        # Actually let's just do it manually with a simple loop
        
        points_top = []
        points_mid = []
        points_bot = []
        
        for x in range(width):
            # Normalized distance from center (0 to 1)
            dist = abs(x - center_x) / center_x
            # Curve function: x^2 shape
            # y_offset = dip * (1 - dist^2)  <- this is n shape
            # y_offset = dip * (dist^2)      <- this is U shape if we add it
            
            curve_y = (dist ** 2) * -15 + 10 # Edges higher (-15), Center lower (+10) relative to something?
            # Let's keep it simple:
            # Center is lowest point (highest Y value).
            # Edges are highest point (lowest Y value).
            
            y_base = center_y + 6 # Vertex Y
            y_curve = y_base - (dist ** 2) * 16 # Curves UP at edges
            
            points_mid.append((x, y_curve))
            points_top.append((x, y_curve - 4))
            points_bot.append((x, y_curve + 4))

        # Draw the curves
        draw.line(points_top, fill=(150, 0, 255), width=2)
        draw.line(points_bot, fill=(150, 0, 255), width=2)
        draw.line(points_mid, fill=(0, 200, 255), width=4)

    # Save
    filename = f"mask_design_{design_type}_84x103.png"
    img.save(filename)
    print(f"Generated: {filename}")

if __name__ == "__main__":
    create_mask_design("tech_friendly")
    create_mask_design("siri_abstract")
    create_mask_design("siri_curved")
