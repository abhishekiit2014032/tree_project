import requests
import json
import base64
from PIL import Image, ImageEnhance
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def enhance_image(img):
    """
    Enhance image quality for better plant identification.
    """
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.3)
    
    return img

def resize_image(image_path, max_size=1024):
    """
    Resize image while maintaining aspect ratio if it exceeds max_size.
    Also improves image quality for better identification.
    """
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Calculate new size maintaining aspect ratio
        ratio = min(max_size/float(img.size[0]), max_size/float(img.size[1]))
        if ratio < 1:  # Only resize if image is larger than max_size
            new_size = tuple([int(x*ratio) for x in img.size])
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance image quality
        img = enhance_image(img)
        
        # Save to bytes with higher quality
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

def identify_tree_type(image_path, api_key=None):
    """
    Identify tree type using PlantNet API.
    Returns tuple of (tree_type, confidence) and prints all matches.
    """
    try:
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.getenv('PLANTNET_API_KEY', os.getenv('PLANT_ID_API_KEY'))  # Try both names
            if not api_key:
                print("Error: No API key found. Please set PLANTNET_API_KEY in your .env file")
                return "Error: No API Key", 0.0

        # PlantNet API endpoint
        url = "https://my-api.plantnet.org/v2/identify/all"
        
        # Read and resize image if necessary
        image_data = resize_image(image_path)
        
        # Prepare multipart form data
        files = {
            'images': ('image.jpg', image_data, 'image/jpeg')
        }
        
        # Add organ information (one organ type for each image)
        data = {
            'organs': ['auto']  # Use 'auto' to let the API detect the organ type
        }
        
        # Use only api-key parameter
        params = {
            'api-key': api_key
        }
        
        print(f"\nSending request to PlantNet API for image: {os.path.basename(image_path)}")
        
        # Make API request
        response = requests.post(url, files=files, data=data, params=params)
        
        if response.status_code == 200:
            result = response.json()
            
            # Debug: Print raw API response
            print("\nRaw API Response:")
            print(json.dumps(result, indent=2))
            
            # Extract results
            results = result.get("results", [])
            
            if results:
                print("\nAll matches from PlantNet API:")
                print("-" * 50)
                
                # Sort results by score
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                
                # Filter out low confidence matches (less than 5%)
                valid_results = [r for r in results if r.get("score", 0) * 100 >= 5]
                
                if not valid_results:
                    print("No matches found with confidence >= 5%")
                    return "Unknown Plant", 0.0
                
                # Print all matches
                for idx, result in enumerate(valid_results[:10], 1):  # Show top 10 matches
                    confidence = result.get("score", 0) * 100
                    species = result.get("species", {})
                    
                    print(f"\nMatch #{idx}:")
                    print(f"Scientific Name: {species.get('scientificName', 'Unknown')}")
                    if "commonNames" in species:
                        print(f"Common Names: {', '.join(species['commonNames'])}")
                    print(f"Confidence: {confidence:.2f}%")
                    
                    # Print additional information
                    if "family" in species:
                        print(f"Family: {species['family']}")
                    if "genus" in species:
                        print(f"Genus: {species['genus']}")
                    if "description" in species:
                        print(f"Description: {species['description'][:200]}...")
                    print("-" * 30)
                
                # Get the best match
                best_match = valid_results[0]
                best_species = best_match.get("species", {})
                best_confidence = best_match.get("score", 0) * 100
                
                # Get the best name (prefer common name if available)
                common_names = best_species.get("commonNames", [])
                best_name = common_names[0] if common_names else best_species.get("scientificName", "Unknown Plant")
                
                print(f"\nBest match: {best_name} (Confidence: {best_confidence:.2f}%)")
                return best_name, best_confidence
            else:
                print("No plant/tree matches found")
                return "Unknown Plant", 0.0
        elif response.status_code == 401:
            print("Error: Invalid API key. Please check your PLANTNET_API_KEY in your .env file")
            return "Error: Invalid API Key", 0.0
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return "Error", 0.0
            
    except Exception as e:
        print(f"Error in plant identification: {str(e)}")
        return "Error", 0.0