import os
import sys
import time
from datetime import datetime
import shutil
from utils.database import Database
from utils.geolocation import extract_gps_data
from utils.image_processing import calculate_tree_dimensions, process_image
from utils.plant_id import identify_tree_type, resize_image
from utils.web_ui import start_web_interface
from dotenv import load_dotenv
import threading
import logging
import argparse
import torch
from utils.model_loader import load_model
from utils.download_cascades import main as download_cascades

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

def clean_database():
    """Clean the database by removing all records"""
    try:
        if os.path.exists('tree_analysis.db'):
            os.remove('tree_analysis.db')
            logging.info("Database cleaned successfully")
        else:
            logging.info("Database file does not exist")
    except Exception as e:
        logging.error(f"Error cleaning database: {str(e)}")
        return False
    return True

def process_images(image_dir, model, device, force_refresh=False):
    """Process all images in the directory."""
    try:
        # Initialize database
        db = Database()
        
        # Get list of images
        image_files = [f for f in os.listdir(image_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        logging.info(f"Found {len(image_files)} images to process")
        
        # Process each image
        for i, image_file in enumerate(image_files, 1):
            image_path = os.path.join(image_dir, image_file)
            
            # Check if image needs processing
            if not force_refresh and db.get_tree_by_image_path(image_file):
                logging.info(f"Skipping {image_file} - already processed")
                continue
                
            logging.info(f"Processing image {i}/{len(image_files)}: {image_file}")
            
            # Process image
            result = process_image(image_path, model, device)
            
            if result:
                # Add to database
                db.add_tree(
                    image_path=image_file,
                    tree_type=result['tree_type'],
                    height_m=result['height_m'],
                    width_m=result['width_m']
                )
                logging.info(f"Successfully processed {image_file}")
            else:
                logging.error(f"Failed to process {image_file}")
                
    except Exception as e:
        logging.error(f"Error processing images: {str(e)}")
    finally:
        if 'db' in locals():
            del db

def main():
    """Main function to run the tree analysis application."""
    try:
        # Download required cascade files
        logging.info("Downloading required cascade files...")
        download_cascades()
        
        # Set image directory
        image_dir = 'tree_images'
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            logging.info(f"Created image directory: {image_dir}")
            
        # Load model
        logging.info("Loading DenseNet model...")
        model, device = load_model()
        
        # Process images
        process_images(image_dir, model, device)
        
        # Start web interface
        logging.info("Starting web interface...")
        start_web_interface()
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if 'model' in locals():
            del model

if __name__ == '__main__':
    main()