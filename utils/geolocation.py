from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def get_exif_data(image_path):
    """Extract EXIF data from image"""
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if exif is None:
            return None
        return {TAGS.get(tag, tag): value for tag, value in exif.items()}
    except Exception as e:
        print(f"Error extracting EXIF data: {str(e)}")
        return None

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def extract_gps_data(image_path):
    """Extract GPS coordinates from image EXIF data"""
    try:
        print(f"\nExtracting GPS data from: {image_path}")
        exif = get_exif_data(image_path)
        if not exif:
            return None

        gps_info = {}
        for key, value in exif.items():
            decoded = TAGS.get(key, key)
            if decoded == "GPSInfo":
                print(f"GPS Info found: {value}")
                for t in value.keys():
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_info[sub_decoded] = value[t]

        if not gps_info:
            return None

        lat = None
        lon = None

        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
            lat = convert_to_degrees(gps_info["GPSLatitude"])
            if gps_info["GPSLatitudeRef"] != "N":
                lat = -lat

        if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lon = convert_to_degrees(gps_info["GPSLongitude"])
            if gps_info["GPSLongitudeRef"] != "E":
                lon = -lon

        if lat is not None and lon is not None:
            print(f"Converted coordinates: {lat}, {lon}")
            return lat, lon  # Return tuple of coordinates
        return None

    except Exception as e:
        print(f"Error extracting GPS data: {str(e)}")
        return None

def get_location_from_image(image_path):
    """
    Extract location from image metadata.
    Returns (latitude, longitude) or (None, None) if not found.
    """
    print(f"\nExtracting GPS data from: {image_path}")
    exif_data = get_exif_data(image_path)
    if exif_data:
        lat, lon = extract_gps_data(image_path)
        if lat is not None and lon is not None:
            return lat, lon
        else:
            print("No valid GPS coordinates found in EXIF data")
    else:
        print("No EXIF data found in image")
    
    return None, None

def get_location(input_type="coordinates", **kwargs):
    """
    Get latitude and longitude based on input type.
    
    Args:
        input_type (str): Type of input - "coordinates", "address", "gps", or "image"
        **kwargs: Additional arguments based on input_type:
            - For "coordinates": lat, lon
            - For "address": address
            - For "gps": gps_data (dictionary with lat, lon)
            - For "image": image_path
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    try:
        if input_type == "image":
            image_path = kwargs.get('image_path')
            if image_path and os.path.exists(image_path):
                return get_location_from_image(image_path)
            print(f"Image file not found: {image_path}")
            return (None, None)
            
        elif input_type == "coordinates":
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
            return (None, None)
            
        elif input_type == "address":
            address = kwargs.get('address')
            if not address:
                return (None, None)
            geolocator = Nominatim(user_agent="tree_locator")
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return (None, None)
            
        elif input_type == "gps":
            gps_data = kwargs.get('gps_data', {})
            lat = gps_data.get('latitude')
            lon = gps_data.get('longitude')
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
            return (None, None)
            
        else:
            print(f"Unsupported input type: {input_type}")
            return (None, None)
            
    except (GeocoderTimedOut, ValueError) as e:
        print(f"Error getting location: {str(e)}")
        return (None, None)