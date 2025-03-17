import os
import sys
import glob
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
API_KEY = os.getenv('PLANT_ID_API_KEY')  # Get API key from environment variables
REFERENCE_HEIGHT_CM = 180  # Height of the reference object in cm
REFERENCE_PIXEL_HEIGHT = 500  # Height of the reference object in the image (in pixels)

# Check if API key is set
if not API_KEY:
    print("Error: PLANT_ID_API_KEY not found in environment variables!")
    print("Please create a .env file with your Plant.id API key.")
    sys.exit(1)

# Initialize database
db = TreeDatabase()

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp'}

def is_supported_image(filename):
    """
    Check if the file is a supported image format and not an analyzed image.
    """
    if '_analyzed.' in filename:
        return False
    return os.path.splitext(filename.lower())[1] in SUPPORTED_FORMATS

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

def process_tree_images(image_dir, api_key):
    """
    Process all tree images in the given directory.
    """
    try:
        for image_name in os.listdir(image_dir):
            if not is_supported_image(image_name):
                continue
                
            image_path = os.path.join(image_dir, image_name)
            print(f"\nProcessing {image_name}...")

            # Check if image needs processing
            if not db.image_needs_processing(image_path):
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

if __name__ == "__main__":
    try:
        # Check if image directory exists
        if not os.path.exists(IMAGE_DIR):
            print(f"Error: Image directory '{IMAGE_DIR}' not found!")
            sys.exit(1)

        # Only remove analyzed images, keep the database
        print("\nCleaning up analyzed images...")
        cleanup_analyzed_images()

        # Check if there are any supported images in the directory
        supported_images = [f for f in os.listdir(IMAGE_DIR) if is_supported_image(f)]
        if not supported_images:
            print(f"Error: No supported images found in '{IMAGE_DIR}' directory!")
            print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            sys.exit(1)

        # Process all tree images
        process_tree_images(IMAGE_DIR, API_KEY)

        # Start the web UI
        print("\nStarting web interface...")
        print("Open your browser and navigate to http://localhost:5000")
        run_web_ui()

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)