from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def get_exif_data(image_path):
    """
    Extract EXIF data from an image file.
    """
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if not exif:
            print(f"No EXIF data found in {image_path}")
            return None
            
        exif_data = {}
        for tag_id in exif:
            tag = TAGS.get(tag_id, tag_id)
            data = exif.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode(errors='replace')
            exif_data[tag] = data
        return exif_data
    except Exception as e:
        print(f"Error reading EXIF data: {str(e)}")
        return None

def convert_to_degrees(value):
    """
    Convert GPS coordinates to decimal degrees.
    """
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception as e:
        print(f"Error converting to degrees: {str(e)}")
        return None

def get_gps_coordinates(exif_data):
    """
    Extract GPS coordinates from EXIF data.
    """
    if not exif_data:
        print("No EXIF data available")
        return None, None
        
    if 'GPSInfo' not in exif_data:
        print("No GPS info in EXIF data")
        return None, None
        
    gps_info = exif_data['GPSInfo']
    print(f"GPS Info found: {gps_info}")
    
    try:
        # Handle the specific format found in the images
        # GPSLatitude is stored in tag 2
        # GPSLatitudeRef is stored in tag 1
        # GPSLongitude is stored in tag 4
        # GPSLongitudeRef is stored in tag 3
        
        lat = gps_info.get(2)  # GPSLatitude
        lat_ref = gps_info.get(1)  # GPSLatitudeRef
        lon = gps_info.get(4)  # GPSLongitude
        lon_ref = gps_info.get(3)  # GPSLongitudeRef
        
        if lat and lon:
            # Convert to decimal degrees
            lat_deg = convert_to_degrees(lat)
            lon_deg = convert_to_degrees(lon)
            
            if lat_deg is not None and lon_deg is not None:
                # Apply hemisphere reference
                if lat_ref == 'S':
                    lat_deg = -lat_deg
                if lon_ref == 'W':
                    lon_deg = -lon_deg
                    
                print(f"Converted coordinates: {lat_deg}, {lon_deg}")
                return lat_deg, lon_deg
                
    except Exception as e:
        print(f"Error processing GPS coordinates: {str(e)}")
    
    return None, None

def get_location_from_image(image_path):
    """
    Extract location from image metadata.
    Returns (latitude, longitude) or (None, None) if not found.
    """
    print(f"\nExtracting GPS data from: {image_path}")
    exif_data = get_exif_data(image_path)
    if exif_data:
        lat, lon = get_gps_coordinates(exif_data)
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