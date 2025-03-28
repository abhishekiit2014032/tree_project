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
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tree_analysis.log'),
        logging.StreamHandler()
    ]
)

def cleanup_analyzed_images():
    """Remove previously analyzed images to avoid reprocessing"""
    # Remove analyzed images
    analyzed_images = [f for f in os.listdir('tree_images') if f.endswith('_analyzed.jpg')]
    for img in analyzed_images:
        try:
            os.remove(os.path.join('tree_images', img))
            logging.info(f"Removed analyzed image: {img}")
        except Exception as e:
            logging.error(f"Error removing {img}: {str(e)}")
    
    # Remove any temporary files
    temp_files = [f for f in os.listdir('tree_images') if f.endswith('.tmp')]
    for temp_file in temp_files:
        try:
            os.remove(os.path.join('tree_images', temp_file))
            logging.info(f"Removed temporary file: {temp_file}")
        except Exception as e:
            logging.error(f"Error removing {temp_file}: {str(e)}")

def process_image(image_path, db, force_refresh=False):
    """Process a single image and save results to database"""
    try:
        logging.info(f"Processing {os.path.basename(image_path)}...")
        
        # Check if image has already been processed
        image_name = os.path.basename(image_path)
        existing_tree = db.get_tree_by_image_path(image_path)
        
        if existing_tree and not force_refresh:
            logging.info(f"Image {image_name} has already been processed, skipping...")
            return True
        
        # Extract location from image
        logging.info("Extracting location from image...")
        gps_data = extract_gps_data(image_path)
        latitude = None
        longitude = None
        if gps_data:
            latitude, longitude = gps_data
            logging.info(f"GPS coordinates: {latitude}, {longitude}")
        
        # Identify tree type
        logging.info("Identifying tree type...")
        tree_type, confidence = identify_tree_type(image_path)
        logging.info(f"Identified as: {tree_type} (confidence: {confidence:.2f}%)")
        
        # Calculate tree dimensions
        logging.info("Calculating tree dimensions...")
        height_m, width_m = calculate_tree_dimensions(image_path)
        logging.info(f"Tree dimensions: {height_m:.2f}m height, {width_m:.2f}m width")
        
        # Save results to database
        try:
            if existing_tree and force_refresh:
                # Update existing record
                db.update_tree(existing_tree[0], tree_type, height_m, width_m, latitude, longitude)
                logging.info("Data updated in database")
            else:
                # Add new record
                db.add_tree(image_path, tree_type, height_m, width_m, latitude, longitude)
                logging.info("Data saved to database")
            return True
        except Exception as e:
            logging.error(f"Error saving data to database: {str(e)}")
            return False
            
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return False

def process_images_in_batches(image_files, db, force_refresh=False, batch_size=10):
    """Process images in batches with progress tracking"""
    total_images = len(image_files)
    processed_count = 0
    successful_count = 0
    failed_count = 0
    skipped_count = 0
    
    logging.info(f"Starting to process {total_images} images in batches of {batch_size}")
    
    for i in range(0, total_images, batch_size):
        batch = image_files[i:i + batch_size]
        for image_file in batch:
            try:
                image_path = os.path.join('tree_images', image_file)
                if process_image(image_path, db, force_refresh):
                    successful_count += 1
                else:
                    failed_count += 1
                processed_count += 1
                
                # Log progress
                progress = (processed_count / total_images) * 100
                logging.info(f"Progress: {progress:.1f}% ({processed_count}/{total_images})")
                
                # Add a small delay between processing images
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error processing batch: {str(e)}")
                failed_count += 1
                processed_count += 1
                continue
    
    return successful_count, failed_count, skipped_count

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tree Analysis Application')
    parser.add_argument('--force-refresh', action='store_true', 
                      help='Force refresh of all images, even if previously processed')
    args = parser.parse_args()
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize database
        db = Database()
        
        # Clean up previously analyzed images
        cleanup_analyzed_images()
        
        # Process all images in tree_images directory
        image_files = [f for f in os.listdir('tree_images') 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) 
                      and not f.endswith('_analyzed.jpg')
                      and not f.endswith('.tmp')]
        
        if not image_files:
            logging.warning("No images found in tree_images directory")
            return
        
        logging.info(f"Found {len(image_files)} images to process")
        
        # Process images in batches
        successful, failed, skipped = process_images_in_batches(
            image_files, db, force_refresh=args.force_refresh
        )
        
        # Log final statistics
        logging.info(f"Processing completed:")
        logging.info(f"- Total images: {len(image_files)}")
        logging.info(f"- Successfully processed: {successful}")
        logging.info(f"- Failed: {failed}")
        logging.info(f"- Skipped (already processed): {skipped}")
        
        # Start web interface
        logging.info("\nStarting web interface...")
        start_web_interface()
        
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()