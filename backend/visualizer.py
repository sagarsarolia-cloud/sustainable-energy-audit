import cv2
import numpy as np
import os

def create_heatmap_overlay(image_path, detections):
    """
    Generates a heatmap overlay based on detection bounding boxes.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    # If no items or empty list, return original image
    if not detections:
        return image_path
        
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    height, width = img.shape[:2]
    
    for item in detections:
        # Support both 'box_2d' (new) and direct list (legacy)
        box = item.get("box_2d") 
        
        if box:
            ymin, xmin, ymax, xmax = box
            
            # Convert normalized coordinates to pixel coordinates
            # Gemini Vision usually returns 0-1000 scale
            scale_y = height / 1000 if ymax > 1 else height
            scale_x = width / 1000 if xmax > 1 else width
            
            abs_ymin = int(ymin * scale_y)
            abs_xmin = int(xmin * scale_x)
            abs_ymax = int(ymax * scale_y)
            abs_xmax = int(xmax * scale_x)
            
            center_x = (abs_xmin + abs_xmax) // 2
            center_y = (abs_ymin + abs_ymax) // 2
            
            # Radius proportional to the object size but tighter
            w_px = abs_xmax - abs_xmin
            h_px = abs_ymax - abs_ymin
            # Reduce radius to 1/3 of min dimension for tighter hotspots
            radius = max(min(w_px, h_px) // 3, 15) 
            
            # Draw a solid circle on mask
            cv2.circle(mask, (center_x, center_y), radius, 255, -1)
            
    # Apply Blur - Reduced kernel size for sharper thermal look
    heatmap_gray = cv2.GaussianBlur(mask, (61, 61), 0)
    
    # Apply Colormap
    heatmap_color = cv2.applyColorMap(heatmap_gray, cv2.COLORMAP_JET)
    
    # CRITICAL FIX: Create a mask from the grayscale heatmap
    # Only blend where the heat is > 0.
    # We want to keep the original image where heatmap_gray is low (background)
    
    # 1. Convert heatmap to float for blending
    heatmap_float = heatmap_color.astype(np.float32) / 255.0
    img_float = img.astype(np.float32) / 255.0
    
    # 2. Calculate alpha channel based on intensity
    # Normalize mask to 0-1
    alpha = heatmap_gray.astype(np.float32) / 255.0
    # Boost alpha to make it more visible but keep edges soft
    alpha = np.clip(alpha * 1.5, 0, 0.6) 
    
    # 3. Expand alpha to 3 channels
    alpha = cv2.merge([alpha, alpha, alpha])
    
    # 4. Blend: Result = Heatmap * Alpha + Original * (1 - Alpha)
    result = (heatmap_float * alpha + img_float * (1 - alpha))
    result = (result * 255).astype(np.uint8)
    
    output_path = image_path.replace(".jpg", "_heatmap.jpg").replace(".png", "_heatmap.png")
    # specific fix if extension matches
    if output_path == image_path:
        output_path = image_path + "_heatmap.jpg"
        
    cv2.imwrite(output_path, result)
    return output_path
