import os
import sys
import time
from datetime import datetime
import shutil
from utils.database import Database
from utils.geolocation import extract_gps_data
from utils.image_processing import calculate_tree_dimensions
from utils.plant_id import identify_tree_type, resize_image
from utils.web_ui import start_web_interface
from dotenv import load_dotenv
import threading

def cleanup_analyzed_images():
    """Remove previously analyzed images to avoid reprocessing"""
    analyzed_images = [f for f in os.listdir('tree_images') if f.endswith('_analyzed.jpg')]
    for img in analyzed_images:
        try:
            os.remove(os.path.join('tree_images', img))
            print(f"Removed analyzed image: {img}")
        except Exception as e:
            print(f"Error removing {img}: {str(e)}")

def process_image(image_path, db):
    """Process a single image and save results to database"""
    try:
        print(f"Processing {os.path.basename(image_path)}...")
        
        # Extract location from image
        print("Extracting location from image...")
        gps_data = extract_gps_data(image_path)
        latitude = None
        longitude = None
        if gps_data:
            latitude, longitude = gps_data
            print(f"GPS coordinates: {latitude}, {longitude}")
        
        # Identify tree type
        print("Identifying tree type...")
        tree_type, confidence = identify_tree_type(image_path)
        print(f"Identified as: {tree_type} (confidence: {confidence:.2f}%)")
        
        # Calculate tree dimensions
        print("Calculating tree dimensions...")
        height_m, width_m = calculate_tree_dimensions(image_path)
        print(f"Tree dimensions: {height_m:.2f}m height, {width_m:.2f}m width")
        
        # Save results to database
        image_name = os.path.basename(image_path)
        if db.save_tree_data(image_path, image_name, tree_type, height_m, width_m, latitude, longitude):
            print("Data saved to database")
        else:
            print("Error saving data to database")
            
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    db = Database()
    
    # Clean up previously analyzed images
    cleanup_analyzed_images()
    
    # Process all images in tree_images directory
    image_files = [f for f in os.listdir('tree_images') 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) 
                  and not f.endswith('_analyzed.jpg')]
    
    if not image_files:
        print("No images found in tree_images directory")
        return
    
    for image_file in image_files:
        image_path = os.path.join('tree_images', image_file)
        process_image(image_path, db)
        time.sleep(1)  # Small delay between processing images
    
    # Start web interface
    print("\nStarting web interface...")
    start_web_interface()

if __name__ == "__main__":
    main()