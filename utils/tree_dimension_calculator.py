import cv2
import numpy as np
from PIL import Image, ExifTags
import math
import os
import logging

class TreeDimensionCalculator:
    def __init__(self):
        # Initialize reference object detectors
        self.car_cascade = self._load_cascade('haarcascade_car.xml')
        self.person_cascade = self._load_cascade('haarcascade_fullbody.xml')
    
    def _load_cascade(self, cascade_name):
        """Try to load Haar cascade from different possible locations"""
        paths = [
            os.path.join(cv2.data.haarcascades, cascade_name),
            cascade_name,
            os.path.join(os.path.dirname(__file__), cascade_name)
        ]
        
        for path in paths:
            if os.path.exists(path):
                return cv2.CascadeClassifier(path)
        return None
    
    def get_image_metadata(self, image_path):
        """Extract EXIF metadata from image"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    return {
                        ExifTags.TAGS[k]: v
                        for k, v in exif_data.items()
                        if k in ExifTags.TAGS
                    }
            return {}
        except Exception as e:
            logging.warning(f"Error reading metadata: {str(e)}")
            return {}

    def calculate_focal_length_pixels(self, metadata, image_width):
        """Calculate focal length in pixels using EXIF data"""
        try:
            # Get focal length in mm from EXIF
            focal_length_mm = float(metadata['FocalLength'])
            
            # Get sensor width (approximate if not available)
            sensor_width_mm = 36.0  # Default full-frame sensor width
            
            # Check for sensor information
            if 'FocalPlaneResolutionUnit' in metadata:
                if 'FocalPlaneXResolution' in metadata:
                    sensor_width_mm = (
                        image_width * 
                        float(metadata['FocalPlaneResolutionUnit']) / 
                        float(metadata['FocalPlaneXResolution'])
                    )
            
            # Calculate focal length in pixels
            return (image_width * focal_length_mm) / sensor_width_mm
            
        except KeyError:
            # Default to common smartphone parameters if no EXIF
            sensor_width_mm = 6.17  # Typical smartphone sensor width
            focal_length_mm = 4.2   # Typical smartphone focal length
            return (image_width * focal_length_mm) / sensor_width_mm

    def improved_tree_segmentation(self, image):
        """Better tree segmentation using color and morphology"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define range for green colors (trees/foliage)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create mask and refine it
        mask = cv2.inRange(hsv, lower_green, upper_green)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours and select the largest one
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return max(contours, key=cv2.contourArea) if contours else None

    def detect_reference_object(self, image):
        """Detect reference objects using cascade classifiers"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Try detecting cars
        if self.car_cascade:
            cars = self.car_cascade.detectMultiScale(gray, 1.1, 3)
            if len(cars) > 0:
                x,y,w,h = cars[0]  # Take first detected car
                return {
                    'type': 'car',
                    'width_px': w,
                    'height_px': h,
                    'real_width': 1.8,
                    'real_height': 1.5
                }
        
        # Try detecting people
        if self.person_cascade:
            people = self.person_cascade.detectMultiScale(gray, 1.1, 3)
            if len(people) > 0:
                x,y,w,h = people[0]  # Take first detected person
                return {
                    'type': 'person',
                    'width_px': w,
                    'height_px': h,
                    'real_width': 0.5,
                    'real_height': 1.7
                }
        
        return None

    def apply_perspective_correction(self, height_m, width_m, orientation):
        """Adjust dimensions based on camera orientation"""
        # Orientation values:
        # 1 = Normal (0°)
        # 3 = 180°
        # 6 = 90° CW
        # 8 = 90° CCW
        
        if orientation in [6, 8]:  # Portrait orientation
            height_m *= 1.1
            width_m *= 0.9
        elif orientation == 3:  # Upside down
            height_m *= 0.9
            width_m *= 1.1
        
        return height_m, width_m

    def calculate_tree_dimensions(self, image_path):
        """Main function to calculate tree dimensions"""
        try:
            # Read image and get metadata
            image = cv2.imread(image_path)
            if image is None:
                logging.error(f"Could not read image: {image_path}")
                return None, None

            metadata = self.get_image_metadata(image_path)
            img_height, img_width = image.shape[:2]
            
            # Get focal length in pixels
            focal_length_px = self.calculate_focal_length_pixels(metadata, img_width)
            
            # Segment tree
            tree_contour = self.improved_tree_segmentation(image)
            if tree_contour is None:
                logging.error("Could not detect tree in image")
                return None, None
            
            x, y, w, h = cv2.boundingRect(tree_contour)
            
            # Try to find reference object
            reference = self.detect_reference_object(image)
            
            if reference:
                # Method 1: Use reference object if available
                px_per_meter = reference['height_px'] / reference['real_height']
                method = f"Reference object ({reference['type']})"
            else:
                # Method 2: Use camera geometry if we have metadata
                if metadata and 'FocalLength' in metadata:
                    # Simplified distance estimation
                    distance_estimate = (h * focal_length_px) / (h * math.tan(math.radians(30)))
                    px_per_meter = focal_length_px / distance_estimate
                    method = "Camera geometry estimation"
                else:
                    # Method 3: Fallback estimation
                    px_per_meter = img_height / 15.0  # Assuming tree fills most of frame
                    method = "Fallback estimation"
            
            height_m = h / px_per_meter
            width_m = w / px_per_meter
            
            # Apply perspective correction if we have camera orientation
            if metadata and 'Orientation' in metadata:
                height_m, width_m = self.apply_perspective_correction(
                    height_m, width_m, metadata['Orientation']
                )
            
            # Apply sanity checks
            height_m = max(1.0, min(50.0, height_m))  # Reasonable tree height range
            width_m = max(0.5, min(15.0, width_m))    # Reasonable width range
            
            # Draw and save results
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"H: {height_m:.2f}m", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"W: {width_m:.2f}m", (x + w + 10, y + h//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Method: {method}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            output_path = os.path.splitext(image_path)[0] + '_analyzed.jpg'
            cv2.imwrite(output_path, image)
            
            logging.info(f"Results saved to {output_path}")
            logging.info(f"Calculation method: {method}")
            logging.info(f"Tree dimensions - Height: {height_m:.2f}m, Width: {width_m:.2f}m")
            
            return height_m, width_m
            
        except Exception as e:
            logging.error(f"Error calculating tree dimensions: {str(e)}")
            return None, None 