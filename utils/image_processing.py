import cv2
import numpy as np

def calculate_tree_dimensions(image_path, reference_height_cm, reference_pixel_height):
    """
    Calculate tree dimensions using reference object and computer vision.
    Returns height and width in meters.
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use Otsu's method for thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            raise ValueError("No contours found in the image")
            
        # Find the largest contour (assuming it's the tree)
        tree_contour = max(contours, key=cv2.contourArea)
        
        # Get the bounding rectangle
        x, y, w, h = cv2.boundingRect(tree_contour)
        
        # Calculate pixels per centimeter using reference object
        pixels_per_cm = reference_pixel_height / reference_height_cm
        
        # Calculate dimensions in centimeters
        height_cm = h / pixels_per_cm
        width_cm = w / pixels_per_cm
        
        # Convert to meters
        height_m = height_cm / 100.0
        width_m = width_cm / 100.0
        
        # Draw the measurements on the image (for visualization)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, f"H: {height_m:.2f}m", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"W: {width_m:.2f}m", (x + w + 10, y + h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Save the annotated image
        output_path = image_path.replace('.', '_analyzed.')
        cv2.imwrite(output_path, image)
        
        return height_m, width_m

    except Exception as e:
        print(f"Error calculating dimensions: {str(e)}")
        return "NO DATA", "NO DATA"