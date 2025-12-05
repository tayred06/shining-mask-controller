from PIL import Image, ImageDraw
import os

def create_frame(eye_direction="center", mouth_state="neutral"):
    width = 42
    height = 56
    bg_color = (0, 0, 0)
    feature_color = (0, 255, 255) # Cyan/Blue
    white = (255, 255, 255)

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Tech Eyes (Friendly)
    # Draw a shape that looks digital but not angry. 
    # Let's do rectangles with cut corners (octagonal-ish)
    
    def draw_tech_eye(x, y):
        # Friendly Tech Eye: Large rectangle with cut corners (Octagon)
        # No angry diagonals.
        
        # Main body (Cross shape to make rounded rectangle)
        draw.rectangle([x+2, y, x+8, y+10], fill=feature_color)   # Vertical center
        draw.rectangle([x, y+2, x+10, y+8], fill=feature_color)   # Horizontal center
        
        # Fill in corners slightly to make it solid but soft
        draw.point([x+1, y+1], fill=feature_color)
        draw.point([x+9, y+1], fill=feature_color)
        draw.point([x+1, y+9], fill=feature_color)
        draw.point([x+9, y+9], fill=feature_color)

        # Pupil (Large and cute)
        pupil_offset_x = -2 if eye_direction == "left" else (2 if eye_direction == "right" else 0)
        draw.rectangle([x+3+pupil_offset_x, y+3, x+7+pupil_offset_x, y+7], fill=white)

    draw_tech_eye(5, 15)
    draw_tech_eye(27, 15)

    # Mouth (Waveform Smile)
    mouth_y = 40
    # A simple waveform pattern that curves up
    #   |   |   |
    # | | | | | | |
    if mouth_state == "neutral" or mouth_state == "happy":
        # Base waveform
        heights = [2, 3, 5, 3, 2] 
        center_x = 21
        spacing = 3
        
        # Draw left side
        for i, h in enumerate(heights):
            x_pos = center_x - (i * spacing)
            draw.line([x_pos, mouth_y - h, x_pos, mouth_y + h], fill=feature_color, width=2)
            
        # Draw right side (skipping center to avoid double draw if we wanted, but here we just mirror)
        for i, h in enumerate(heights):
            if i == 0: continue # Don't redraw center
            x_pos = center_x + (i * spacing)
            draw.line([x_pos, mouth_y - h, x_pos, mouth_y + h], fill=feature_color, width=2)
            
        # If happy, maybe add small pixels at the ends to simulate upward curve
        if mouth_state == "happy":
            draw.point([center_x - 12, mouth_y - 3], fill=feature_color)
            draw.point([center_x + 12, mouth_y - 3], fill=feature_color)

    return img

def create_animation():
    frames = []
    # Sequence: Center -> Right -> Center -> Left -> Center -> Happy
    sequence = [
        ("center", "neutral"),
        ("center", "neutral"),
        ("right", "neutral"),
        ("right", "neutral"),
        ("center", "neutral"),
        ("left", "neutral"),
        ("left", "neutral"),
        ("center", "neutral"),
        ("center", "happy"),
        ("center", "happy"),
    ]

    for direction, mouth in sequence:
        frames.append(create_frame(direction, mouth))

    # Save as GIF
    frames[0].save('mask_animation_preview.gif',
               save_all=True,
               append_images=frames[1:],
               optimize=False,
               duration=400,
               loop=0)
    print("Animation generated: mask_animation_preview.gif")

if __name__ == "__main__":
    create_animation()
