import os
import urllib.request
import logging

def download_cascade(url, filename):
    """Download a Haar cascade file if it doesn't exist."""
    try:
        if not os.path.exists(filename):
            logging.info(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            logging.info(f"Successfully downloaded {filename}")
        else:
            logging.info(f"{filename} already exists")
    except Exception as e:
        logging.error(f"Error downloading {filename}: {str(e)}")

def main():
    """Download required Haar cascade files."""
    # Create utils directory if it doesn't exist
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # URLs for Haar cascade files
    cascades = {
        'haarcascade_car.xml': 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_cars.xml',
        'haarcascade_fullbody.xml': 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_fullbody.xml'
    }
    
    # Download each cascade file
    for filename, url in cascades.items():
        filepath = os.path.join(os.path.dirname(__file__), filename)
        download_cascade(url, filepath)

if __name__ == '__main__':
    main() 