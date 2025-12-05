from PIL import Image, ImageOps

def create_preview_with_layout():
    try:
        # Load the layout
        layout_path = "masque_layout.png"
        layout = Image.open(layout_path).convert("RGBA")
        
        # Load the design we generated earlier
        design_path = "mask_design_tech_friendly_84x103.png"
        design = Image.open(design_path).convert("RGBA")
        
        # Ensure design is same size as layout (resize if necessary, though they should match 84x103)
        if design.size != layout.size:
            print(f"Resizing design from {design.size} to {layout.size}")
            design = design.resize(layout.size)
        
        # Create a composite image
        # We want to see the design ON TOP of the layout, but maybe with some transparency 
        # to see if it fits the mask boundaries.
        # Or better: Put the design BEHIND the layout if the layout has transparency for the mask holes?
        # Assuming the layout shows the mask shape. Let's try blending them.
        
        # Create a background (black)
        bg = Image.new("RGBA", layout.size, (0, 0, 0, 255))
        
        # Paste design
        bg.paste(design, (0, 0), design)
        
        # Paste layout on top with 50% opacity to check alignment
        # Or if layout is just outlines, paste it directly.
        # Let's assume layout is opaque where the mask is.
        # We'll blend them 50/50
        
        preview = Image.blend(bg.convert("RGB"), layout.convert("RGB"), 0.3)
        
        preview.save("preview_on_mask.png")
        print("Generated preview_on_mask.png. Check this image to verify alignment.")
        
    except Exception as e:
        print(f"Error creating preview: {e}")

if __name__ == "__main__":
    create_preview_with_layout()
