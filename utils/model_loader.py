import torch
import torchvision.models as models
import logging

def load_model():
    """
    Load the DenseNet model for tree type identification.
    
    Returns:
        tuple: (model, device) where model is the loaded DenseNet model
               and device is the PyTorch device (CPU/GPU)
    """
    try:
        # Set device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info(f"Using device: {device}")
        
        # Load pre-trained DenseNet model
        model = models.densenet121(pretrained=True)
        
        # Modify the classifier for our number of classes
        num_classes = 1000  # Standard ImageNet classes
        model.classifier = torch.nn.Linear(model.classifier.in_features, num_classes)
        
        # Move model to device
        model = model.to(device)
        
        # Set model to evaluation mode
        model.eval()
        
        # Add class names (ImageNet classes)
        model.class_names = get_imagenet_classes()
        
        logging.info("Successfully loaded DenseNet model")
        return model, device
        
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

def get_imagenet_classes():
    """Get ImageNet class names."""
    try:
        # Download class names if not already present
        import urllib.request
        import os
        
        class_file = 'imagenet_classes.txt'
        if not os.path.exists(class_file):
            url = 'https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt'
            urllib.request.urlretrieve(url, class_file)
            logging.info("Downloaded ImageNet class names")
        
        # Read class names
        with open(class_file, 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
            
        return class_names
        
    except Exception as e:
        logging.error(f"Error getting ImageNet classes: {str(e)}")
        # Return a basic list of tree-related classes as fallback
        return ['tree', 'pine', 'oak', 'maple', 'palm', 'birch', 'cedar', 'spruce'] 