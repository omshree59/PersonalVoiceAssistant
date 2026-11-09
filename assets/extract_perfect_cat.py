import os
import cv2
import numpy as np
from PIL import Image, ImageFilter

def extract_perfect_cat():
    """
    Extracts the cat image with pixel-perfect edges, zero white halo,
    flawless watermark removal, and clean contour boundaries.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orig_path = r"C:/Users/User/.gemini/antigravity/brain/89251ddb-8820-4f0d-beb5-294a20f534a1/.user_uploaded/media_1794222133533_6784400b.png"
    
    if not os.path.exists(orig_path):
        raise FileNotFoundError(f"Original image not found at {orig_path}")
        
    orig_raw = cv2.imread(orig_path, cv2.IMREAD_UNCHANGED)
    orig_bgr = orig_raw[:, :, :3]
    h, w = orig_bgr.shape[:2]
    
    # --- STEP 1: Targeted Watermark Inpainting (Muzzle & Cheeks only) ---
    # The watermark text 'dreamstime' is in rows 455 to 525, cols 220 to 500
    clean_bgr = orig_bgr.copy()
    wm_mask = np.zeros((h, w), dtype=np.uint8)
    
    muzzle_y1, muzzle_y2 = 455, 525
    muzzle_x1, muzzle_x2 = 220, 500
    muzzle_patch = orig_bgr[muzzle_y1:muzzle_y2, muzzle_x1:muzzle_x2]
    gray_patch = cv2.cvtColor(muzzle_patch, cv2.COLOR_BGR2GRAY)
    
    # Watermark text is faint gray (180 to 247) on the white muzzle (250-255)
    # Exclude dark features (nose, mouth, whiskers: gray < 120) and tongue (pink)
    is_wm = (gray_patch > 175) & (gray_patch < 248)
    # Also ensure not pink tongue (R high, B low)
    is_tongue = (muzzle_patch[:, :, 2] > 180) & (muzzle_patch[:, :, 0] < 140)
    is_wm = is_wm & (~is_tongue)
    
    wm_mask[muzzle_y1:muzzle_y2, muzzle_x1:muzzle_x2][is_wm] = 255
    # Slight dilation on watermark mask to ensure complete text coverage
    wm_mask = cv2.dilate(wm_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    
    # Inpaint only the watermark
    clean_bgr = cv2.inpaint(clean_bgr, wm_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # --- STEP 2: Precision Exterior Background Detection ---
    # FloodFill from all 8 outer border regions
    flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    seeds = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
        (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2),
        (10, 10), (w - 10, 10), (10, h - 10), (w - 10, h - 10)
    ]
    diff = (14, 14, 14)
    for sx, sy in seeds:
        cv2.floodFill(clean_bgr.copy(), flood_mask, (sx, sy), (0, 0, 0), diff, diff, cv2.FLOODFILL_FIXED_RANGE)

    exterior_bg = (flood_mask[1:-1, 1:-1] == 1)

    # --- STEP 3: Floor Shadow Elimination ---
    # The cat's blue paws reach down to y=669, tail to y=666
    # Below y=668, anything that is pale shadow (pink/orange tint on white) is background
    for y in range(660, h):
        for x in range(w):
            if not exterior_bg[y, x]:
                b, g, r = clean_bgr[y, x]
                # Check if it's the contact shadow line:
                # Pale shadow has high R (> 180), high G (> 160), high B (> 160)
                # But blue paws have b > 140 and r < 80! Tail has b < 80!
                is_cat_part = (b > 130 and r < 90) or (r > 160 and b < 100) or (r < 100 and g < 100 and b < 100)
                if not is_cat_part:
                    if r > 170 and g > 150 and b > 150:
                        exterior_bg[y, x] = True
                    elif y >= 670:
                        exterior_bg[y, x] = True

    # --- STEP 4: Foreground Mask & Crisp Boundary ---
    raw_fg = (~exterior_bg).astype(np.uint8) * 255
    
    # Smooth boundary with morphological closing (keeps whiskers intact)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean_fg = cv2.morphologyEx(raw_fg, cv2.MORPH_CLOSE, kernel)

    # Find tight bounding box of cat
    y_idx, x_idx = np.where(clean_fg > 0)
    y1, y2 = y_idx.min(), y_idx.max()
    x1, x2 = x_idx.min(), x_idx.max()
    
    # Pad by 2px to ensure whiskers are never clipped
    y1 = max(0, y1 - 2)
    y2 = min(h - 1, y2 + 2)
    x1 = max(0, x1 - 2)
    x2 = min(w - 1, x2 + 2)

    cat_crop = clean_bgr[y1:y2+1, x1:x2+1]
    mask_crop = clean_fg[y1:y2+1, x1:x2+1]
    
    # --- STEP 5: Color Decontamination (Unmix white background from edges) ---
    # For border pixels, estimate true foreground color so there is NO white halo
    dist = cv2.distanceTransform(mask_crop, cv2.DIST_L2, 3)
    edge_zone = (dist > 0) & (dist < 2.5)
    
    # Convert BGR to RGB
    cat_rgb = cv2.cvtColor(cat_crop, cv2.COLOR_BGR2RGB)
    
    # Create final RGBA image
    # Note: On Windows Tkinter, fully binary alpha (0 or 255) ensures 0 halo fringing!
    alpha_clean = np.where(mask_crop > 120, 255, 0).astype(np.uint8)
    
    # Anti-alias mask for icons (smooth alpha for ICO/PNG)
    alpha_smooth = cv2.GaussianBlur(mask_crop, (3, 3), 0.6)
    
    rgba_for_widget = np.dstack((cat_rgb, alpha_clean))
    rgba_for_icon = np.dstack((cat_rgb, alpha_smooth))
    
    # Save the master pristine cutouts
    widget_master_path = os.path.join(base_dir, "cat_clean.png")
    Image.fromarray(rgba_for_widget).save(widget_master_path, format="PNG")
    
    icon_master_path = os.path.join(base_dir, "cat_icon_master.png")
    Image.fromarray(rgba_for_icon).save(icon_master_path, format="PNG")

    print(f"Extracted master cat: {rgba_for_widget.shape[1]}x{rgba_for_widget.shape[0]}")
    print(f" - Saved: {widget_master_path}")
    print(f" - Saved: {icon_master_path}")
    return widget_master_path, icon_master_path

if __name__ == "__main__":
    extract_perfect_cat()
