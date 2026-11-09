import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_flawless_cat_sprites():
    """Generates studio-quality, pixel-perfect cat animation sprites and multi-res icons."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = os.path.join(base_dir, "cat_clean.png")
    
    if not os.path.exists(clean_path):
        from assets.extract_perfect_cat import extract_perfect_cat
        extract_perfect_cat()
        
    cat = cv2.imread(clean_path, cv2.IMREAD_UNCHANGED)
    h, w = cat.shape[:2]
    
    # 1. Neutral Sprite
    cv2.imwrite(os.path.join(base_dir, "cat_neutral.png"), cat)
    
    # 2. Left Ear Twitch (Seamless Continuous Mesh Warp - No Seams!)
    map_lx = np.tile(np.arange(w, dtype=np.float32), (h, 1))
    map_ly = np.tile(np.arange(h, dtype=np.float32).reshape(-1, 1), (1, w))
    for y in range(0, 135):
        for x in range(25, 165):
            weight = max(0.0, (135 - y) / 135.0) ** 1.3
            # Ear perks up and tilts slightly outward to the left
            map_lx[y, x] += 6.5 * weight
            map_ly[y, x] += 7.5 * weight
    ear_left = cv2.remap(cat, map_lx, map_ly, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    cv2.imwrite(os.path.join(base_dir, "cat_ear_left.png"), ear_left)
    
    # 3. Right Ear Twitch (Seamless Continuous Mesh Warp)
    map_rx = np.tile(np.arange(w, dtype=np.float32), (h, 1))
    map_ry = np.tile(np.arange(h, dtype=np.float32).reshape(-1, 1), (1, w))
    for y in range(0, 135):
        for x in range(215, 355):
            weight = max(0.0, (135 - y) / 135.0) ** 1.3
            # Ear perks up and tilts slightly outward to the right
            map_rx[y, x] -= 6.5 * weight
            map_ry[y, x] += 7.5 * weight
    ear_right = cv2.remap(cat, map_rx, map_ry, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    cv2.imwrite(os.path.join(base_dir, "cat_ear_right.png"), ear_right)
    
    # 4. Both Ears Alert & Perked (Listening Mode)
    map_bx = np.tile(np.arange(w, dtype=np.float32), (h, 1))
    map_by = np.tile(np.arange(h, dtype=np.float32).reshape(-1, 1), (1, w))
    for y in range(0, 135):
        # Left ear
        for x in range(25, 165):
            weight = max(0.0, (135 - y) / 135.0) ** 1.3
            map_bx[y, x] += 5.5 * weight
            map_by[y, x] += 7.0 * weight
        # Right ear
        for x in range(215, 355):
            weight = max(0.0, (135 - y) / 135.0) ** 1.3
            map_bx[y, x] -= 5.5 * weight
            map_by[y, x] += 7.0 * weight
    ear_both = cv2.remap(cat, map_bx, map_by, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    cv2.imwrite(os.path.join(base_dir, "cat_ear_both.png"), ear_both)

    # 5. Natural Blink (Correct Eye Coordinates: Left=(104, 209), Right=(242, 208))
    blink_bgr = cat[:, :, :3].copy()
    alpha = cat[:, :, 3].copy()
    
    eyes_info = [
        (104, 209, [39, 188, 248], [200, 173, 43]),
        (242, 208, [46, 159, 234], [191, 174, 49])
    ]
    for eye_x, eye_y, c_top, c_bot in eyes_info:
        for y in range(193, 226):
            t = (y - 193) / 33.0
            col = (np.array(c_top) * (1 - t) + np.array(c_bot) * t).astype(np.uint8)
            for x in range(eye_x - 22, eye_x + 23):
                dx = (x - eye_x) / 21.0
                dy = (y - eye_y) / 16.0
                if dx*dx + dy*dy <= 1.0:
                    blink_bgr[y, x] = col
                    
    pil_blink = Image.fromarray(cv2.cvtColor(np.dstack((blink_bgr, alpha)), cv2.COLOR_BGRA2RGBA))
    draw_b = ImageDraw.Draw(pil_blink)
    # Draw soft happy closed eyes
    eye_line_color = (24, 28, 48, 255)
    draw_b.arc([104 - 18, 209 - 8, 104 + 18, 209 + 10], start=180, end=0, fill=eye_line_color, width=4)
    draw_b.arc([242 - 18, 208 - 8, 242 + 18, 208 + 10], start=180, end=0, fill=eye_line_color, width=4)
    pil_blink.save(os.path.join(base_dir, "cat_blink.png"))

    # 6. Cute Happy / Success Sprite (Smiling arched eyes + soft pink blushing cheeks)
    pil_happy = Image.fromarray(cv2.cvtColor(np.dstack((blink_bgr, alpha)), cv2.COLOR_BGRA2RGBA))
    draw_h = ImageDraw.Draw(pil_happy)
    # Happy arched eyes (^_^)
    draw_h.arc([104 - 18, 209 - 9, 104 + 18, 209 + 11], start=180, end=0, fill=eye_line_color, width=5)
    draw_h.arc([242 - 18, 208 - 9, 242 + 18, 208 + 11], start=180, end=0, fill=eye_line_color, width=5)
    # Cute cheek blushes
    blush = (255, 120, 160, 130)
    draw_h.ellipse([70, 224, 96, 238], fill=blush)
    draw_h.ellipse([250, 224, 276, 238], fill=blush)
    pil_happy.save(os.path.join(base_dir, "cat_happy.png"))

    # 7. Pixel-Perfect Multi-Resolution Windows ICO & PNG
    icon_master_path = os.path.join(base_dir, "cat_icon_master.png")
    if os.path.exists(icon_master_path):
        cat_for_icon = Image.open(icon_master_path).convert("RGBA")
    else:
        cat_for_icon = Image.fromarray(cv2.cvtColor(cat, cv2.COLOR_BGRA2RGBA))
        
    # Standard square 256x256 canvas with clean margins
    icon_canvas_size = 256
    icon_base = Image.new("RGBA", (icon_canvas_size, icon_canvas_size), (0, 0, 0, 0))
    
    # Scale cat to 238px height (preserving aspect ratio, centered)
    cat_scaled = cat_for_icon.copy()
    cat_scaled.thumbnail((238, 238), Image.Resampling.LANCZOS)
    ox = (icon_canvas_size - cat_scaled.width) // 2
    oy = (icon_canvas_size - cat_scaled.height) // 2
    icon_base.paste(cat_scaled, (ox, oy), cat_scaled)
    
    # Save crisp PNG
    png_path = os.path.join(base_dir, "icon.png")
    icon_base.save(png_path, format="PNG")
    
    # Generate tailored mipmap sizes for Windows ICO with unsharp masking for small sizes
    sizes = [256, 128, 64, 48, 32, 24, 16]
    ico_images = []
    for sz in sizes:
        resized_img = icon_base.resize((sz, sz), Image.Resampling.LANCZOS)
        # Apply subtle sharpening for small icons so eyes & whiskers stay razor-sharp
        if sz <= 48:
            resized_img = resized_img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120, threshold=2))
        ico_images.append(resized_img)
        
    ico_path = os.path.join(base_dir, "icon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in ico_images],
        append_images=ico_images[1:]
    )
    
    print(f"Flawless cat animation sprites & multi-resolution icon generated successfully!")
    print(f" - ICO Path: {ico_path}")
    print(f" - PNG Path: {png_path}")

if __name__ == "__main__":
    create_flawless_cat_sprites()
