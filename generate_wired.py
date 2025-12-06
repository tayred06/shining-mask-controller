from PIL import Image, ImageDraw

def create_wired_text_mask():
    width = 42
    height = 56
    bg_color = (0, 0, 0)
    feature_color = (0, 255, 255) # Cyan
    white = (255, 255, 255)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # --- 1. THE TEXT "tayreddd" (Custom 3x5 pixel font) ---
    # Representation of 3x5 font
    font_chars = {
        't': [[1,1,1],[0,1,0],[0,1,0],[0,1,0],[0,1,0]],
        'a': [[0,1,0],[1,0,1],[1,1,1],[1,0,1],[1,0,1]],
        'y': [[1,0,1],[1,0,1],[0,1,0],[0,1,0],[0,1,0]],
        'r': [[1,1,0],[1,0,1],[1,1,0],[1,0,1],[1,0,1]],
        'e': [[1,1,1],[1,0,0],[1,1,1],[1,0,0],[1,1,1]],
        'd': [[1,1,0],[1,0,1],[1,0,1],[1,0,1],[1,1,0]],
    }
    
    text = "tayreddd"
    start_x = 2 # (42 - (8*4 - 1)) / 2 = (42 - 31) / 2 = 5.5 -> ~5 or center manually
    # Length of "tayreddd" is 8 chars.
    # Each char is 3px wide + 1px space. Total width = 8*4 - 1 = 31.
    # Center x: (42-31)//2 = 5.
    
    current_x = 5
    text_y = 4 # Forehead position
    
    for char in text:
        bitmap = font_chars[char]
        for r, row in enumerate(bitmap):
            for c, pixel in enumerate(row):
                if pixel:
                    draw.point((current_x + c, text_y + r), fill=feature_color)
        current_x += 4 # 3 width + 1 spacing

    # --- 2. TECH EYES (Slightly larger to balance text) ---
    def draw_tech_eye(x, y):
        # Frame
        draw.rectangle([x, y, x+10, y+8], outline=feature_color)
        # Pupil (looking at camera)
        draw.rectangle([x+3, y+3, x+6, y+5], fill=white)
        # Digital details (dots on corners)
        draw.point([x, y], fill=(0,0,0)) # cut corner
        draw.point([x+10, y], fill=(0,0,0)) # cut corner
        draw.point([x, y+8], fill=(0,0,0)) # cut corner
        draw.point([x+10, y+8], fill=(0,0,0)) # cut corner

    eye_y = 16
    draw_tech_eye(4, eye_y)
    draw_tech_eye(28, eye_y)

    # --- 3. WAVEFORM MOUTH ---
    mouth_y = 42
    # Waveform pattern
    heights = [1, 2, 4, 3, 5, 3, 4, 2, 1]
    center_x = 21
    spacing = 2
    
    # Draw from center outwards
    # We have 9 bars. Center is index 4 (value 5).
    start_bar_x = center_x - (len(heights)//2 * spacing)
    
    for i, h in enumerate(heights):
        x = start_bar_x + i*spacing
        draw.line([x, mouth_y - h, x, mouth_y + h], fill=feature_color)
        # Make the center brighter/white for effect
        if h == 5:
             draw.line([x, mouth_y - 2, x, mouth_y + 2], fill=white)

    img.save("mask_wired_text.png")
    print("Image generated: mask_wired_text.png")

if __name__ == "__main__":
    create_wired_text_mask()
