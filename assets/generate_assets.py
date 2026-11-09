import os
from PIL import Image, ImageDraw

def generate_app_icon():
    """Generates a modern, high-resolution application icon (ICO & PNG)."""
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(assets_dir, exist_ok=True)
    
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer glow / background circle
    center = size // 2
    r_outer = 118
    r_inner = 106
    
    # Glow rings
    draw.ellipse([center - r_outer - 4, center - r_outer - 4, center + r_outer + 4, center + r_outer + 4], 
                 outline=(99, 102, 241, 60), width=6)
    draw.ellipse([center - r_outer, center - r_outer, center + r_outer, center + r_outer], 
                 fill=(15, 23, 42, 245), outline=(56, 189, 248, 220), width=5)
    
    # Inner subtle rim
    draw.ellipse([center - r_inner, center - r_inner, center + r_inner, center + r_inner], 
                 outline=(30, 41, 59, 180), width=2)
    
    # Draw Microphone Silhouette
    # 1. Mic capsule (rounded rectangle)
    mic_w = 40
    mic_h = 70
    mic_top = center - 48
    draw.rounded_rectangle(
        [center - mic_w // 2, mic_top, center + mic_w // 2, mic_top + mic_h],
        radius=20,
        fill=(248, 250, 252, 250)
    )
    
    # 2. Mic grid detail lines
    draw.line([center - mic_w // 2 + 6, mic_top + 22, center + mic_w // 2 - 6, mic_top + 22], fill=(148, 163, 184, 200), width=3)
    draw.line([center - mic_w // 2 + 6, mic_top + 34, center + mic_w // 2 - 6, mic_top + 34], fill=(148, 163, 184, 200), width=3)
    
    # 3. Mic cradle arc (U-shape)
    arc_box = [center - 32, center - 18, center + 32, center + 46]
    draw.arc(arc_box, start=0, end=180, fill=(56, 189, 248, 255), width=6)
    
    # 4. Mic stand vertical stem
    draw.line([center, center + 46, center, center + 68], fill=(56, 189, 248, 255), width=6)
    
    # 5. Mic stand base
    draw.line([center - 24, center + 68, center + 24, center + 68], fill=(56, 189, 248, 255), width=6)
    
    # Save PNG
    png_path = os.path.join(assets_dir, "icon.png")
    img.save(png_path, format="PNG")
    
    # Save multi-size ICO
    ico_path = os.path.join(assets_dir, "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print(f"Generated icon assets successfully:\n - {png_path}\n - {ico_path}")
    return ico_path, png_path

if __name__ == "__main__":
    generate_app_icon()
