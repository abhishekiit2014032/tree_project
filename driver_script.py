import os
import sys
import glob
import argparse
from dotenv import load_dotenv
from utils.geolocation import get_location
from utils.plant_id import identify_tree_type
from utils.image_processing import calculate_tree_dimensions
from utils.database import TreeDatabase
from utils.web_ui import run_web_ui

# Load environment variables
load_dotenv()

# Configuration
IMAGE_DIR = "tree_images"  # Folder containing tree images
API_KEY = os.getenv('PLANTNET_API_KEY')  # Get API key from environment variables
REFERENCE_HEIGHT_CM = 180  # Height of the reference object in cm
REFERENCE_PIXEL_HEIGHT = 500  # Height of the reference object in the image (in pixels)

# Check if API key is set
if not API_KEY:
    print("Error: PLANTNET_API_KEY not found in environment variables!")
    print("Please create a .env file with your PlantNet API key.")
    sys.exit(1)

# Initialize database
db = TreeDatabase()

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif'}

def is_valid_image(image_path):
    """
    Validate if the file is a valid image that can be processed.
    """
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            return False
        return True
    except Exception:
        return False

def is_supported_image(filename):
    """
    Check if the file is a supported image format and not an analyzed image.
    """
    if '_analyzed.' in filename:
        return False
    return os.path.splitext(filename.lower())[1] in SUPPORTED_FORMATS

def get_all_images(image_dir):
    """
    Get all valid images from the directory and its subdirectories.
    """
    valid_images = []
    for root, _, files in os.walk(image_dir):
        for file in files:
            if is_supported_image(file):
                image_path = os.path.join(root, file)
                if is_valid_image(image_path):
                    valid_images.append(image_path)
                else:
                    print(f"Warning: Invalid image file: {file}")
    return valid_images

def cleanup_analyzed_images():
    """Remove any previously analyzed images"""
    try:
        # Remove analyzed images
        analyzed_images = glob.glob(os.path.join(IMAGE_DIR, "*_analyzed.*"))
        for img in analyzed_images:
            os.remove(img)
            print(f"Removed analyzed image: {os.path.basename(img)}")
        return True
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        return False

def process_tree_images(image_dir, api_key, use_cache=False):
    """
    Process all tree images in the given directory.
    """
    try:
        # Get all valid images from directory and subdirectories
        image_paths = get_all_images(image_dir)
        
        if not image_paths:
            print(f"No valid images found in '{image_dir}' directory!")
            print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            return

        for image_path in image_paths:
            image_name = os.path.basename(image_path)
            print(f"\nProcessing {image_name}...")

            # Check if image needs processing
            if not use_cache and not db.image_needs_processing(image_path, force_refresh=True):
                print(f"Using cached analysis for {image_name}...")
                continue

            # Step 1: Get location from image metadata
            print("Extracting location from image...")
            latitude, longitude = get_location("image", image_path=image_path)
            
            if latitude is None or longitude is None:
                print("No GPS data found in image. Storing as 'NO DATA'")
                latitude, longitude = "NO DATA", "NO DATA"

            # Step 2: Identify tree type
            print("Identifying tree type...")
            try:
                tree_type, confidence = identify_tree_type(image_path, api_key)
                print(f"Identified tree type: {tree_type} (Confidence: {confidence:.2f}%)")
            except Exception as e:
                print(f"Error identifying tree type: {str(e)}")
                tree_type, confidence = "NO DATA", 0.0

            # Step 3: Calculate tree dimensions
            print("Calculating tree dimensions...")
            try:
                height_m, width_m = calculate_tree_dimensions(image_path, REFERENCE_HEIGHT_CM, REFERENCE_PIXEL_HEIGHT)
                if isinstance(height_m, (int, float)) and isinstance(width_m, (int, float)):
                    print(f"Calculated dimensions: Height = {height_m:.2f}m, Width = {width_m:.2f}m")
                else:
                    print(f"Dimensions: {height_m}, {width_m}")
            except Exception as e:
                print(f"Error calculating tree dimensions: {str(e)}")
                height_m, width_m = "NO DATA", "NO DATA"

            # Store result in database
            db.add_result(image_path, image_name, tree_type, height_m, width_m, 
                        latitude, longitude, confidence)
            print(f"Data saved for {image_name}")

    except Exception as e:
        print(f"Error processing images: {str(e)}")
        sys.exit(1)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Tree Analysis Tool')
    parser.add_argument('--use-cache', action='store_true', 
                      help='Use cached analysis results if available')
    args = parser.parse_args()

    try:
        # Check if image directory exists
        if not os.path.exists(IMAGE_DIR):
            print(f"Error: Image directory '{IMAGE_DIR}' not found!")
            print("Creating directory...")
            os.makedirs(IMAGE_DIR)
            print(f"Created directory: {IMAGE_DIR}")
            print("\nPlease add your tree images to this directory and run the script again.")
            print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            sys.exit(0)

        # Only remove analyzed images, keep the database
        print("\nCleaning up analyzed images...")
        cleanup_analyzed_images()

        # Get all valid images
        image_paths = get_all_images(IMAGE_DIR)
        
        if not image_paths:
            print(f"\nNo valid images found in '{IMAGE_DIR}' directory!")
            print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            print("\nPlease add your tree images to the directory and run the script again.")
            sys.exit(0)

        print(f"\nFound {len(image_paths)} valid images to process.")
        print("Starting image processing...")

        # Process all tree images
        process_tree_images(IMAGE_DIR, API_KEY, use_cache=args.use_cache)

        # Start the web UI
        print("\nStarting web interface...")
        print("Open your browser and navigate to http://localhost:5000")
        run_web_ui()

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("Please check your images and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()