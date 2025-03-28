import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import logging
from .tree_dimension_calculator import TreeDimensionCalculator

# Initialize the tree dimension calculator
tree_calculator = TreeDimensionCalculator()

def preprocess_image(image_path):
    """
    Preprocess image for model input.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        torch.Tensor: Preprocessed image tensor
    """
    try:
        # Read image
        image = Image.open(image_path).convert('RGB')
        
        # Apply transformations
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                              std=[0.229, 0.224, 0.225])
        ])
        
        # Transform image
        image_tensor = transform(image)
        return image_tensor.unsqueeze(0)
        
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {str(e)}")
        return None

def calculate_tree_dimensions(image_path):
    """
    Calculate tree dimensions using the improved calculator.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        tuple: (height_m, width_m) or (None, None) if calculation fails
    """
    try:
        return tree_calculator.calculate_tree_dimensions(image_path)
    except Exception as e:
        logging.error(f"Error calculating tree dimensions for {image_path}: {str(e)}")
        return None, None

def process_image(image_path, model, device):
    """
    Process a single image to identify tree type and calculate dimensions.
    
    Args:
        image_path (str): Path to the image file
        model: PyTorch model for tree type identification
        device: PyTorch device (CPU/GPU)
        
    Returns:
        dict: Dictionary containing tree type and dimensions, or None if processing fails
    """
    try:
        # Preprocess image
        image_tensor = preprocess_image(image_path)
        if image_tensor is None:
            return None
            
        # Move tensor to device
        image_tensor = image_tensor.to(device)
        
        # Get model prediction
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs, 1)
            confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
            
        # Get tree type from model's class mapping
        tree_type = model.class_names[predicted.item()]
        
        # Calculate tree dimensions
        height_m, width_m = calculate_tree_dimensions(image_path)
        if height_m is None or width_m is None:
            logging.warning(f"Failed to calculate dimensions for {image_path}")
            return None
            
        return {
            'tree_type': tree_type,
            'confidence': confidence,
            'height_m': height_m,
            'width_m': width_m
        }
        
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return None

def find_scale_factor(img):
    """Find scale factor using reference objects in the image"""
    try:
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for reference objects
        reference_ranges = {
            'car': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 30, 100])
            },
            'person': {
                'lower': np.array([0, 20, 70]),
                'upper': np.array([20, 255, 255])
            },
            'bicycle': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 30, 100])
            }
        }
        
        # Reference object dimensions in meters
        reference_sizes = {
            'car': {'width': 1.8, 'height': 1.5},
            'person': {'width': 0.6, 'height': 1.7},
            'bicycle': {'width': 0.6, 'height': 1.2}
        }
        
        for obj_type, ranges in reference_ranges.items():
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Calculate scale factor based on reference object
                if w > h:  # Use width for scale
                    scale = reference_sizes[obj_type]['width'] / w
                else:  # Use height for scale
                    scale = reference_sizes[obj_type]['height'] / h
                
                print(f"Found {obj_type} as reference object")
                return scale
        
        return None
        
    except Exception as e:
        print(f"Error finding scale factor: {str(e)}")
        return None

def estimate_camera_distance(img_height, tree_height_px):
    """Estimate camera distance based on image and tree dimensions"""
    # Assume typical camera field of view is 60 degrees
    fov_degrees = 60
    fov_radians = np.radians(fov_degrees)
    
    # Calculate distance based on tree height in pixels vs image height
    tree_ratio = tree_height_px / img_height
    distance = 1 / (2 * np.tan(fov_radians / 2) * tree_ratio)
    
    return distance

def calculate_scale_factor_from_camera(distance, img_height):
    """Calculate scale factor based on camera distance"""
    # Assume typical camera field of view is 60 degrees
    fov_degrees = 60
    fov_radians = np.radians(fov_degrees)
    
    # Calculate pixels per meter based on camera distance
    pixels_per_meter = 2 * distance * np.tan(fov_radians / 2) / img_height
    
    return 1 / pixels_per_meter

def apply_perspective_correction(height_m, width_m, aspect_ratio):
    """Apply perspective correction based on aspect ratio"""
    # Adjust dimensions based on typical perspective distortion
    if aspect_ratio > 0.7:  # Wide trees (likely closer to camera)
        height_m *= 1.1  # Increase height to compensate for perspective
    elif aspect_ratio < 0.3:  # Tall trees (likely further from camera)
        width_m *= 1.1  # Increase width to compensate for perspective
    
    return height_m, width_m

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