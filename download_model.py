import torch
import torchvision.models as models
import os

def download_model():
    """Download and save the pre-trained DenseNet model"""
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # Download pre-trained DenseNet model
    print("Downloading pre-trained DenseNet model...")
    model = models.densenet121(pretrained=True)
    
    # Modify the classifier for our number of classes (10 tree species)
    num_classes = 10
    model.classifier = torch.nn.Linear(model.classifier.in_features, num_classes)
    
    # Save the model
    model_path = os.path.join('models', 'UrbanTreeDenseNet.pt')
    torch.save(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    download_model() 