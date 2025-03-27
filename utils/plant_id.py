import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import random
from .model_manager import ModelManager

# Define the model path
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'UrbanTreeDenseNet.pt')
LABELS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'urban_tree_labels.txt')

# Initialize model manager and load the model
model_manager = ModelManager()
model_manager.load_model("densenet")  # Load the DenseNet model

def resize_image(image_path, target_size=(224, 224)):
    """Resize image to target size while maintaining aspect ratio"""
    img = Image.open(image_path)
    img.thumbnail(target_size, Image.LANCZOS)
    return img

def identify_tree_type(image_path):
    """Identify tree type using pre-trained model"""
    return model_manager.identify_tree_type(image_path)