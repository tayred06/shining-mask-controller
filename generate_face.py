from PIL import Image, ImageDraw

def create_mask_face():
    # Dimensions
    width = 42
    height = 56
    
    # Colors
    bg_color = (0, 0, 0)
    feature_color = (220, 240, 255) # Light blue/white
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Eyes (simple ovals)
    # Left eye
    draw.ellipse([8, 12, 16, 22], fill=feature_color)
    # Right eye
    draw.ellipse([26, 12, 34, 22], fill=feature_color)
    
    # Mouth (neutral)
    # Drawing a straight line
    draw.line([12, 38, 30, 38], fill=feature_color, width=2)
    
    # Save
    img.save("mask_face_neutral_pixel.png")
    print("Image generated: mask_face_neutral_pixel.png")

if __name__ == "__main__":
    create_mask_face()
