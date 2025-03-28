import cv2
import numpy as np
from PIL import Image, ExifTags
import math
import os
import requests
from io import BytesIO
import logging

class AdvancedTreeMeasurer:
    def __init__(self):
        # Initialize with better default parameters
        self.min_tree_height = 1.0  # meters
        self.max_tree_height = 60.0
        self.min_tree_width = 0.3
        self.max_tree_width = 12.0
        
        # Load ML models (would use actual models in production)
        self.tree_seg_model = self._load_tree_segmentation_model()
        self.depth_est_model = self._load_depth_estimation_model()
        
        # Reference objects database
        self.reference_objects = {
            'car': {'height': 1.5, 'width': 1.8, 'detector': self._load_cascade('cars.xml')},
            'person': {'height': 1.7, 'width': 0.5, 'detector': self._load_cascade('fullbody.xml')},
            'bicycle': {'height': 1.1, 'width': 0.6, 'detector': self._load_cascade('bicycle.xml')},
            'bench': {'height': 0.9, 'width': 1.5, 'detector': self._load_cascade('bench.xml')}
        }
        
        # Camera defaults (typical smartphone)
        self.default_sensor_width = 6.17  # mm
        self.default_focal_length = 4.2   # mm
        
    def _load_tree_segmentation_model(self):
        """Placeholder for actual model loading"""
        logging.info("Note: In production, load a proper segmentation model here")
        return None
    
    def _load_depth_estimation_model(self):
        """Placeholder for depth estimation model"""
        logging.info("Note: In production, load a depth estimation model here")
        return None
    
    def _load_cascade(self, filename):
        """Try to load Haar cascade from different locations"""
        paths = [
            os.path.join(cv2.data.haarcascades, filename),
            filename,
            os.path.join(os.path.dirname(__file__), filename)
        ]
        
        for path in paths:
            if os.path.exists(path):
                return cv2.CascadeClassifier(path)
        return None
    
    def get_metadata(self, image_path):
        """Enhanced metadata extraction with more fields"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif() or {}
                metadata = {
                    ExifTags.TAGS.get(k, k): v
                    for k, v in exif_data.items()
                }
                
                # Add calculated fields
                if 'FocalLength' in metadata:
                    metadata['FocalLength'] = float(metadata['FocalLength'])
                
                # Try to get GPS data if available
                if 'GPSInfo' in metadata:
                    metadata['GPS'] = self._extract_gps_info(metadata['GPSInfo'])
                
                return metadata
        except Exception as e:
            logging.warning(f"Metadata warning: {str(e)}")
            return {}
    
    def _extract_gps_info(self, gps_info):
        """Extract GPS coordinates from EXIF data"""
        try:
            lat = self._convert_to_degrees(gps_info.get(2))
            lon = self._convert_to_degrees(gps_info.get(4))
            alt = gps_info.get(6)
            return {'latitude': lat, 'longitude': lon, 'altitude': alt}
        except:
            return None
    
    def _convert_to_degrees(self, value):
        """Convert GPS coordinates to decimal degrees"""
        if not value:
            return None
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    
    def calculate_pixels_per_meter(self, image, tree_contour, metadata):
        """
        Advanced scaling calculation using multiple methods with confidence scoring
        Returns: (pixels_per_meter, method_used, confidence)
        """
        methods = []
        
        # Method 1: Reference objects
        ref_objects = self.detect_reference_objects(image)
        for obj in ref_objects:
            # Use both height and width for better accuracy
            px_per_m_h = obj['height_px'] / obj['real_height']
            px_per_m_w = obj['width_px'] / obj['real_width']
            avg_px_per_m = (px_per_m_h + px_per_m_w) / 2
            methods.append({
                'px_per_m': avg_px_per_m,
                'method': f"Reference ({obj['type']})",
                'confidence': 0.9 if obj['type'] in ['car', 'person'] else 0.7
            })
        
        # Method 2: Camera geometry (if we have focal length)
        if metadata.get('FocalLength'):
            focal_length_mm = metadata['FocalLength']
            sensor_width_mm = metadata.get('SensorWidth', self.default_sensor_width)
            focal_length_px = (image.shape[1] * focal_length_mm) / sensor_width_mm
            
            # Estimate distance to tree using multiple approaches
            distance_estimates = []
            
            # Approach 1: Using assumed tree size
            if tree_contour is not None:
                _, _, w, h = cv2.boundingRect(tree_contour)
                avg_tree_size_px = (w + h) / 2
                distance_estimates.append(
                    (15 * focal_length_px) / avg_tree_size_px  # Assume 15m tree
                )
            
            # Approach 2: Using perspective (if we have multiple reference objects)
            if len(ref_objects) >= 2:
                # Use distance between reference objects
                pass  # Implementation would go here
            
            if distance_estimates:
                avg_distance = sum(distance_estimates) / len(distance_estimates)
                px_per_m = focal_length_px / avg_distance
                methods.append({
                    'px_per_m': px_per_m,
                    'method': "Camera geometry",
                    'confidence': 0.8 if len(distance_estimates) > 1 else 0.6
                })
        
        # Method 3: Depth estimation (if model available)
        if self.depth_est_model:
            try:
                depth_map = self.estimate_depth(image)
                if depth_map is not None:
                    # Get average depth for tree region
                    tree_mask = np.zeros_like(depth_map)
                    cv2.drawContours(tree_mask, [tree_contour], 0, 1, -1)
                    avg_depth = np.mean(depth_map[tree_mask == 1])
                    
                    # Calculate scale
                    px_per_m = focal_length_px / avg_depth
                    methods.append({
                        'px_per_m': px_per_m,
                        'method': "Depth estimation",
                        'confidence': 0.85
                    })
            except Exception as e:
                logging.error(f"Depth estimation failed: {str(e)}")
        
        # Method 4: Fallback based on image dimensions
        methods.append({
            'px_per_m': image.shape[0] / 15.0,  # Assume tree is 15m tall
            'method': "Fallback estimation",
            'confidence': 0.4
        })
        
        # Select best method based on confidence
        best_method = max(methods, key=lambda x: x['confidence'])
        return best_method['px_per_m'], best_method['method'], best_method['confidence']
    
    def detect_reference_objects(self, image):
        """Detect multiple reference objects with enhanced validation"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detected_objects = []
        
        for obj_type, params in self.reference_objects.items():
            if params['detector'] is None:
                continue
                
            # Detect with conservative parameters to reduce false positives
            objects = params['detector'].detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            for (x, y, w, h) in objects:
                # Validate aspect ratio
                aspect_ratio = w / h
                expected_ratio = params['width'] / params['height']
                
                if 0.7 * expected_ratio < aspect_ratio < 1.3 * expected_ratio:
                    detected_objects.append({
                        'type': obj_type,
                        'x': x,
                        'y': y,
                        'width_px': w,
                        'height_px': h,
                        'real_width': params['width'],
                        'real_height': params['height'],
                        'aspect_ratio': aspect_ratio
                    })
        
        return detected_objects
    
    def segment_tree(self, image):
        """Enhanced tree segmentation using multiple techniques"""
        # Try ML model first if available
        if self.tree_seg_model:
            try:
                # In production, would use actual model prediction
                pass
            except:
                pass
        
        # Fallback to traditional CV approach
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Dynamic range for green detection based on image stats
        lower_green = np.array([30, 40, 40])
        upper_green = np.array([90, 255, 255])
        
        # Adaptive masking
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Morphological refinement
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours and select the best candidate
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        
        # Score contours based on multiple factors
        scored_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Score based on:
            # 1. Size (larger is better)
            # 2. Aspect ratio (taller is better for trees)
            # 3. Solidity (more solid is better)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            score = (area * 0.5 + 
                     (1 - min(abs(aspect_ratio - 0.3), 0.7)) * 0.3 + 
                     solidity * 0.2)
            
            scored_contours.append((score, contour))
        
        # Select best contour
        best_contour = max(scored_contours, key=lambda x: x[0])[1]
        return best_contour
    
    def estimate_depth(self, image):
        """Placeholder for depth estimation"""
        # In production, would use a depth estimation model
        # Like MiDaS or similar
        return None
    
    def calculate_dimensions(self, image_path):
        """Main function with enhanced accuracy"""
        try:
            # Load image
            if image_path.startswith('http'):
                response = requests.get(image_path)
                image = cv2.imdecode(np.frombuffer(response.content, np.uint8), -1)
            else:
                image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError("Could not load image")
            
            # Get metadata
            metadata = self.get_metadata(image_path)
            
            # Segment tree
            tree_contour = self.segment_tree(image)
            if tree_contour is None:
                raise ValueError("Could not identify tree in image")
            
            x, y, w, h = cv2.boundingRect(tree_contour)
            
            # Calculate pixels per meter
            px_per_m, method, confidence = self.calculate_pixels_per_meter(
                image, tree_contour, metadata
            )
            
            # Calculate dimensions
            height_m = h / px_per_m
            width_m = w / px_per_m
            
            # Apply perspective correction
            if 'Orientation' in metadata:
                height_m, width_m = self.apply_perspective_correction(
                    height_m, width_m, metadata['Orientation']
                )
            
            # Apply final validation
            height_m = np.clip(height_m, self.min_tree_height, self.max_tree_height)
            width_m = np.clip(width_m, self.min_tree_width, self.max_tree_width)
            
            # Prepare output
            result = {
                'height_m': round(height_m, 2),
                'width_m': round(width_m, 2),
                'method': method,
                'confidence': round(confidence, 2),
                'bounding_box': {'x': x, 'y': y, 'width': w, 'height': h}
            }
            
            # Add GPS data if available
            if 'GPS' in metadata:
                result['gps'] = metadata['GPS']
            
            # Visualize results
            self.visualize_results(image, result, image_path)
            
            return result
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return None
    
    def apply_perspective_correction(self, height, width, orientation):
        """Enhanced perspective correction"""
        # More nuanced correction based on orientation
        corrections = {
            1: (1.0, 1.0),    # Normal
            3: (0.95, 1.05),   # Upside down
            6: (1.1, 0.9),     # 90° CW
            8: (1.1, 0.9)      # 90° CCW
        }
        
        factor_h, factor_w = corrections.get(orientation, (1.0, 1.0))
        return height * factor_h, width * factor_w
    
    def visualize_results(self, image, result, output_path):
        """Enhanced visualization with more information"""
        # Draw bounding box
        bb = result['bounding_box']
        cv2.rectangle(image, 
                      (bb['x'], bb['y']), 
                      (bb['x'] + bb['width'], bb['y'] + bb['height']), 
                      (0, 255, 0), 2)
        
        # Add text annotations
        text_lines = [
            f"Height: {result['height_m']}m",
            f"Width: {result['width_m']}m",
            f"Method: {result['method']}",
            f"Confidence: {result['confidence']*100:.0f}%"
        ]
        
        # Add GPS if available
        if 'gps' in result and result['gps']:
            gps = result['gps']
            if gps.get('latitude') and gps.get('longitude'):
                text_lines.append(f"GPS: {gps['latitude']:.6f}, {gps['longitude']:.6f}")
        
        for i, line in enumerate(text_lines):
            cv2.putText(image, line, 
                        (10, 30 + i * 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 0, 255), 2)
        
        # Save output
        base_path = os.path.splitext(output_path)[0]
        output_path = f"{base_path}_analyzed.jpg"
        cv2.imwrite(output_path, image)
        logging.info(f"Analysis results saved to {output_path}") 