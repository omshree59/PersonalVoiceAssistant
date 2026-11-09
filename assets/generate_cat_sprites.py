import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

def create_cat_assets():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = os.path.join(base_dir, "cat_clean.png")
    
    if not os.path.exists(clean_path):
        clean_path = os.path.join(base_dir, "cat_idle.png")
        
    base_img = cv2.imread(clean_path, cv2.IMREAD_UNCHANGED)
    h, w = base_img.shape[:2]
    
    # --- 1. Neutral / Base Sprite ---
    cv2.imwrite(os.path.join(base_dir, "cat_neutral.png"), base_img)
    
    # --- 2. Left Ear Twitch ---
    # Left ear bounding box: x: 30..150, y: 0..140, pivot at (100, 130)
    img_left = base_img.copy()
    left_ear_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(left_ear_mask, (88, 75), (55, 65), -15, 0, 360, 255, -1)
    
    M_left = cv2.getRotationMatrix2D((95, 130), -6, 1.04) # Perk up and out
    warped_left = cv2.warpAffine(base_img, M_left, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_TRANSPARENT)
    
    # Blend warped left ear onto base
    mask_indices = (left_ear_mask > 0) & (warped_left[:, :, 3] > 0)
    # Clear old left ear in target region
    img_left[left_ear_mask > 0] = [0, 0, 0, 0]
    # Put back head base if cleared
    img_left = np.where(warped_left[:, :, 3:4] > 0, warped_left, base_img)
    # Ensure seamless composite
    ear_crop = cv2.warpAffine(base_img * (left_ear_mask[:, :, None] / 255.0), M_left, (w, h), flags=cv2.INTER_LANCZOS4)
    img_left_ear = base_img.copy()
    img_left_ear[left_ear_mask > 0] = [0, 0, 0, 0]
    # Composite
    alpha_ear = ear_crop[:, :, 3] / 255.0
    for c in range(3):
        img_left_ear[:, :, c] = (ear_crop[:, :, c] * alpha_ear + img_left_ear[:, :, c] * (1 - alpha_ear)).astype(np.uint8)
    img_left_ear[:, :, 3] = np.maximum(img_left_ear[:, :, 3], ear_crop[:, :, 3])
    cv2.imwrite(os.path.join(base_dir, "cat_ear_left.png"), img_left_ear)
    
    # --- 3. Right Ear Twitch ---
    right_ear_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(right_ear_mask, (287, 75), (55, 65), 15, 0, 360, 255, -1)
    
    M_right = cv2.getRotationMatrix2D((280, 130), 6, 1.04) # Perk up and out
    ear_right_crop = cv2.warpAffine(base_img * (right_ear_mask[:, :, None] / 255.0), M_right, (w, h), flags=cv2.INTER_LANCZOS4)
    img_right_ear = base_img.copy()
    img_right_ear[right_ear_mask > 0] = [0, 0, 0, 0]
    
    alpha_r = ear_right_crop[:, :, 3] / 255.0
    for c in range(3):
        img_right_ear[:, :, c] = (ear_right_crop[:, :, c] * alpha_r + img_right_ear[:, :, c] * (1 - alpha_r)).astype(np.uint8)
    img_right_ear[:, :, 3] = np.maximum(img_right_ear[:, :, 3], ear_right_crop[:, :, 3])
    cv2.imwrite(os.path.join(base_dir, "cat_ear_right.png"), img_right_ear)
    
    # --- 4. Both Ears Perked (Listening Alert) ---
    img_both = base_img.copy()
    img_both[left_ear_mask > 0] = [0, 0, 0, 0]
    img_both[right_ear_mask > 0] = [0, 0, 0, 0]
    for c in range(3):
        img_both[:, :, c] = (ear_crop[:, :, c] * alpha_ear + img_both[:, :, c] * (1 - alpha_ear)).astype(np.uint8)
        img_both[:, :, c] = (ear_right_crop[:, :, c] * alpha_r + img_both[:, :, c] * (1 - alpha_r)).astype(np.uint8)
    img_both[:, :, 3] = np.maximum(img_both[:, :, 3], np.maximum(ear_crop[:, :, 3], ear_right_crop[:, :, 3]))
    cv2.imwrite(os.path.join(base_dir, "cat_ear_both.png"), img_both)
    
    # --- 5. Cute Blink Sprite ---
    pil_blink = Image.fromarray(cv2.cvtColor(base_img, cv2.COLOR_BGRA2RGBA))
    draw = ImageDraw.Draw(pil_blink)
    # Eyes centers: left ~(154, 195), right ~(243, 195), radius ~22
    # Cover eyes with matching face gradient color
    face_color = (255, 179, 38, 255) # Warm cat orange
    draw.ellipse([132, 173, 176, 217], fill=face_color)
    draw.ellipse([221, 173, 265, 217], fill=face_color)
    # Draw happy closed eye curves (^_^)
    eye_line_color = (20, 24, 40, 255)
    draw.arc([136, 185, 172, 205], start=180, end=0, fill=eye_line_color, width=4)
    draw.arc([225, 185, 261, 205], start=180, end=0, fill=eye_line_color, width=4)
    
    pil_blink.save(os.path.join(base_dir, "cat_blink.png"))
    
    # --- 6. Cute Happy / Success Sprite ---
    pil_happy = Image.fromarray(cv2.cvtColor(base_img, cv2.COLOR_BGRA2RGBA))
    draw_h = ImageDraw.Draw(pil_happy)
    # Happy arched eyes
    draw_h.ellipse([132, 173, 176, 217], fill=face_color)
    draw_h.ellipse([221, 173, 265, 217], fill=face_color)
    draw_h.arc([135, 180, 173, 210], start=180, end=0, fill=eye_line_color, width=5)
    draw_h.arc([224, 180, 262, 210], start=180, end=0, fill=eye_line_color, width=5)
    # Pink blush on cheeks
    blush_color = (255, 130, 160, 120)
    draw_h.ellipse([110, 210, 135, 225], fill=blush_color)
    draw_h.ellipse([262, 210, 287, 225], fill=blush_color)
    pil_happy.save(os.path.join(base_dir, "cat_happy.png"))

    # --- 7. Generate ICO and PNG icons from the Cat ---
    # Create a square 256x256 image with cat centered and no background
    square_icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    cat_pil = Image.fromarray(cv2.cvtColor(base_img, cv2.COLOR_BGRA2RGBA))
    # Resize preserving aspect ratio
    cat_pil.thumbnail((240, 240), Image.Resampling.LANCZOS)
    offset_x = (256 - cat_pil.width) // 2
    offset_y = (256 - cat_pil.height) // 2
    square_icon.paste(cat_pil, (offset_x, offset_y), cat_pil)
    
    ico_path = os.path.join(base_dir, "icon.ico")
    png_path = os.path.join(base_dir, "icon.png")
    square_icon.save(png_path, format="PNG")
    square_icon.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print("Cat animation sprites & icon generated successfully in assets/!")

if __name__ == "__main__":
    create_cat_assets()
