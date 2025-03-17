import requests
import json
import base64

def identify_tree_type(image_path, api_key):
    """
    Identify tree type using Plant.id API.
    Returns tuple of (tree_type, confidence)
    """
    try:
        # API endpoint
        url = "https://api.plant.id/v2/identify"
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
        # Prepare request data
        payload = {
            "api_key": api_key,
            "images": [base64_data],
            "modifiers": ["crops_fast", "similar_images"],
            "plant_details": ["common_names", "taxonomy", "url"]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make API request
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract plant suggestions
            suggestions = result.get("suggestions", [])
            
            if suggestions:
                # Get the first suggestion (highest confidence)
                plant = suggestions[0]
                plant_name = plant.get("plant_name", "Unknown")
                confidence = plant.get("probability", 0.0) * 100  # Convert to percentage
                
                print(f"Plant identification confidence: {confidence:.2f}%")
                return plant_name, confidence
            else:
                print("No plant suggestions found")
                return "Unknown", 0.0
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return "Error", 0.0
            
    except Exception as e:
        print(f"Error in plant identification: {str(e)}")
        return "Error", 0.0

API_KEY = "your_plant_id_api_key"  # Replace this with your actual API key