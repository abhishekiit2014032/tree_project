"""
Model Management Module for Tree Analysis Application

This module handles the loading and management of the DenseNet model used for tree species identification.
It provides functionality for loading the model, preprocessing images, and making predictions.

Dependencies:
    - torch: Deep learning framework
    - torchvision: Computer vision utilities
    - PIL: Image processing
"""

import os
import torch
import torchvision.transforms as transforms
from PIL import Image
import random
from typing import Tuple, List, Dict

class ModelManager:
    """Manages different pre-trained models for tree identification"""
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize the model manager
        
        Args:
            models_dir (str): Directory containing model files
        """
        self.models_dir = models_dir
        self.current_model = None
        self.current_model_name = None
        self.model_configs = {
            "densenet": {
                "model_path": os.path.join(models_dir, "UrbanTreeDenseNet.pt"),
                "labels_path": os.path.join(models_dir, "urban_tree_labels.txt"),
                "input_size": (224, 224),
                "confidence_threshold": 0.05,  # Lowered threshold to 5%
                "description": "DenseNet model trained on urban tree dataset"
            },
            # Add more model configurations here
            # Example:
            # "resnet": {
            #     "model_path": os.path.join(models_dir, "UrbanTreeResNet.pt"),
            #     "labels_path": os.path.join(models_dir, "tree_labels.txt"),
            #     "input_size": (224, 224),
            #     "confidence_threshold": 0.20,
            #     "description": "ResNet model trained on urban tree dataset"
            # }
        }
        
        # Default placeholder trees for when model is not available
        self.placeholder_trees = [
            "Acer platanoides (Norway Maple)",
            "Acer saccharum (Sugar Maple)",
            "Betula pendula (Silver Birch)",
            "Fagus sylvatica (European Beech)",
            "Fraxinus excelsior (European Ash)",
            "Pinus sylvestris (Scots Pine)",
            "Quercus robur (English Oak)",
            "Tilia cordata (Small-leaved Lime)",
            "Ulmus glabra (Wych Elm)",
            "Platanus × acerifolia (London Plane)"
        ]

    def load_model(self, model_name: str) -> bool:
        """
        Load a specific model by name
        
        Args:
            model_name (str): Name of the model to load
            
        Returns:
            bool: True if model was loaded successfully, False otherwise
        """
        if model_name not in self.model_configs:
            print(f"Model {model_name} not found in configurations")
            return False
            
        config = self.model_configs[model_name]
        
        try:
            if not os.path.exists(config["model_path"]):
                print(f"Model file not found at {config['model_path']}")
                return False
                
            self.current_model = torch.load(config["model_path"])
            self.current_model.eval()
            self.current_model_name = model_name
            print(f"Loaded {model_name} model successfully")
            return True
            
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            return False

    def resize_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image_path (str): Path to the image file
            target_size (tuple): Target size (width, height)
            
        Returns:
            PIL.Image: Resized image
        """
        img = Image.open(image_path).convert('RGB')
        ratio = min(target_size[0]/img.size[0], target_size[1]/img.size[1])
        new_size = tuple([int(x*ratio) for x in img.size])
        img = img.resize(new_size, Image.LANCZOS)
        new_img = Image.new('RGB', target_size)
        new_img.paste(img, ((target_size[0]-new_size[0])//2, (target_size[1]-new_size[1])//2))
        return new_img

    def identify_tree_type(self, image_path: str) -> Tuple[str, float]:
        """
        Identify tree type using the current model
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (tree_type, confidence)
        """
        if not self.current_model:
            print("No model loaded. Using placeholder results.")
            return random.choice(self.placeholder_trees), random.uniform(0.7, 0.95)

        try:
            config = self.model_configs[self.current_model_name]
            
            # Load and preprocess image
            img = self.resize_image(image_path, config["input_size"])
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            img_tensor = transform(img).unsqueeze(0)

            # Get prediction
            with torch.no_grad():
                outputs = self.current_model(img_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                
                # Get top 3 predictions
                top3_prob, top3_indices = torch.topk(probabilities, 3)
                
                # Load labels
                if os.path.exists(config["labels_path"]):
                    with open(config["labels_path"], 'r') as f:
                        labels = [line.strip() for line in f.readlines()]
                    
                    # Get the best match
                    best_idx = top3_indices[0].item()
                    best_prob = top3_prob[0].item()
                    best_label = labels[best_idx]
                    
                    # Print top 3 matches for debugging
                    print("\nTop 3 matches:")
                    for i in range(3):
                        idx = top3_indices[i].item()
                        prob = top3_prob[i].item()
                        label = labels[idx]
                        print(f"{label}: {prob:.2%}")
                    
                    # Return the best match if confidence is above threshold
                    if best_prob > config["confidence_threshold"]:
                        print(f"Identified as: {best_label} (confidence: {best_prob:.2%})")
                        return best_label, best_prob
                    else:
                        print(f"Low confidence prediction ({best_prob:.2%}) for {best_label}")
                        # Return the best match even if below threshold
                        return best_label, best_prob
                else:
                    return f"Tree Class {best_idx}", best_prob

        except Exception as e:
            print(f"Error identifying tree type: {str(e)}")
            return "Unknown Tree", 0.0

    def get_available_models(self) -> List[Dict]:
        """
        Get list of available models and their configurations
        
        Returns:
            list: List of dictionaries containing model configurations
        """
        return [
            {"name": name, **config}
            for name, config in self.model_configs.items()
        ]

    def add_model(self, name: str, config: Dict) -> bool:
        """
        Add a new model configuration
        
        Args:
            name (str): Name of the model
            config (dict): Model configuration dictionary
            
        Returns:
            bool: True if model was added successfully, False otherwise
        """
        required_fields = ["model_path", "labels_path", "input_size", "confidence_threshold", "description"]
        if not all(field in config for field in required_fields):
            print("Missing required configuration fields")
            return False
            
        self.model_configs[name] = config
        return True 

# Create a singleton instance
_model_manager = None

def get_model_manager():
    """
    Get or create the ModelManager singleton instance.
    
    Returns:
        ModelManager: ModelManager instance
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager 