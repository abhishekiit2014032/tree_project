import cv2
import numpy as np
from PIL import Image

def calculate_tree_dimensions(image_path):
    """Calculate tree dimensions from image using image analysis and reference objects"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error reading image: {image_path}")
            return 0.0, 0.0

        # Get image dimensions
        img_height, img_width = img.shape[:2]
        print(f"Image size: {img_width}x{img_height}")
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define green color range for trees
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        
        # Create mask for green regions
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("No tree contour found, using reference-based method")
            return calculate_dimensions_with_reference(img)
        
        # Filter contours based on area and aspect ratio
        valid_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Filter criteria:
            # 1. Area should be at least 5% of image area
            # 2. Aspect ratio should be between 0.2 and 0.8 (typical tree proportions)
            # 3. Height should be at least 30% of image height
            if (area > 0.05 * img_width * img_height and 
                0.2 < aspect_ratio < 0.8 and 
                h > 0.3 * img_height):
                valid_contours.append((contour, area))
        
        if not valid_contours:
            print("No valid tree contour found, using reference-based method")
            return calculate_dimensions_with_reference(img)
        
        # Get the largest valid contour
        tree_contour = max(valid_contours, key=lambda x: x[1])[0]
        
        # Get tree dimensions in pixels
        x, y, w, h = cv2.boundingRect(tree_contour)
        print(f"Tree box (px): {w}x{h}")
        
        # Calculate tree dimensions based on image size
        # Assuming the tree takes up about 70% of the image height
        tree_height_ratio = 0.7
        reference_height_m = 15.0  # Typical tree height in meters
        
        # Calculate pixels per meter based on image height
        pixels_per_meter = (img_height * tree_height_ratio) / reference_height_m
        
        # Calculate actual dimensions
        height_m = h / pixels_per_meter
        width_m = w / pixels_per_meter
        
        # Adjust based on aspect ratio
        aspect_ratio = w / h
        if aspect_ratio > 0.5:  # If tree is wider than expected
            height_m *= 0.8  # Reduce height estimate
        elif aspect_ratio < 0.3:  # If tree is taller than expected
            height_m *= 1.2  # Increase height estimate
        
        # Ensure reasonable bounds based on typical tree sizes
        height_m = max(1.0, min(20.0, height_m))  # Between 1 and 20 meters
        width_m = max(0.5, min(10.0, width_m))    # Between 0.5 and 10 meters
        
        print(f"Calculated dimensions - Height: {height_m:.2f}m, Width: {width_m:.2f}m")
        
        return height_m, width_m
        
    except Exception as e:
        print(f"Error calculating tree dimensions: {str(e)}")
        return 0.0, 0.0

def calculate_dimensions_with_reference(img):
    """Calculate tree dimensions using reference objects and edge detection"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Apply morphological operations to clean up edges
        kernel = np.ones((5,5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("No edges found for reference-based calculation")
            return 0.0, 0.0
        
        # Find the largest contour (assumed to be the tree)
        tree_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(tree_contour)
        
        # Look for reference objects (cars or people)
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common reference objects
        # Cars (typically dark gray/black)
        lower_car = np.array([0, 0, 0])
        upper_car = np.array([180, 30, 100])
        
        # People (skin tones)
        lower_skin = np.array([0, 20, 70])
        upper_skin = np.array([20, 255, 255])
        
        # Create masks for reference objects
        car_mask = cv2.inRange(hsv, lower_car, upper_car)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find reference objects
        car_contours, _ = cv2.findContours(car_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        skin_contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate scale factor based on reference objects
        scale_factor = None
        
        # Try to find a car first (more reliable reference)
        if car_contours:
            car_contour = max(car_contours, key=cv2.contourArea)
            car_x, car_y, car_w, car_h = cv2.boundingRect(car_contour)
            # Average car width is about 1.8 meters
            scale_factor = 1.8 / car_w
            print(f"Using car as reference (width: {car_w}px)")
        
        # If no car found, try to find a person
        elif skin_contours:
            person_contour = max(skin_contours, key=cv2.contourArea)
            person_x, person_y, person_w, person_h = cv2.boundingRect(person_contour)
            # Average person height is about 1.7 meters
            scale_factor = 1.7 / person_h
            print(f"Using person as reference (height: {person_h}px)")
        
        # If no reference objects found, use image-based estimation
        if scale_factor is None:
            print("No reference objects found, using image-based estimation")
            # Assume tree takes up about 70% of image height
            tree_height_ratio = 0.7
            reference_height_m = 15.0  # Typical tree height in meters
            scale_factor = (img.shape[0] * tree_height_ratio) / reference_height_m
        
        # Calculate tree dimensions using scale factor
        height_m = h * scale_factor
        width_m = w * scale_factor
        
        # Adjust based on typical tree proportions
        aspect_ratio = w / h
        if aspect_ratio > 0.5:  # If tree is wider than expected
            height_m *= 0.8  # Reduce height estimate
        elif aspect_ratio < 0.3:  # If tree is taller than expected
            height_m *= 1.2  # Increase height estimate
        
        # Ensure reasonable bounds
        height_m = max(1.0, min(20.0, height_m))  # Between 1 and 20 meters
        width_m = max(0.5, min(10.0, width_m))    # Between 0.5 and 10 meters
        
        print(f"Reference-based dimensions - Height: {height_m:.2f}m, Width: {width_m:.2f}m")
        
        return height_m, width_m

    except Exception as e:
        print(f"Error in reference-based calculation: {str(e)}")
        return 0.0, 0.0