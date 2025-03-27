# Tree Analysis Project

This project analyzes tree images to identify tree species, calculate dimensions, and extract GPS coordinates. It provides both a command-line interface and a web-based dashboard for viewing and managing the analysis results.

## Features

- Tree species identification using DenseNet model
- Tree dimension calculation using reference-based method
- GPS coordinate extraction from images
- Web-based dashboard with:
  - Table view of all analyzed trees
  - Interactive map view showing tree locations
  - Tree clustering for better visualization of multiple trees
  - Detailed tree information including:
    - Tree type
    - Height and width
    - GPS coordinates
    - Processed date
    - Image reference

## Installation

1. Clone the repository:
```bash
git clone https://github.com/abhishekiit2014032/tree_project.git
cd tree_project
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download the model:
```bash
python download_model.py
```

## Usage

1. Place your tree images in the `tree_images` directory

2. Run the analysis:
```bash
python driver_script.py
```

3. Access the web dashboard:
- Open your browser and navigate to `http://localhost:5000`
- View the table of analyzed trees
- Click "Map View" to see trees plotted on an interactive map
- Click on tree markers to view detailed information
- Use the export button to download analysis results

## Project Structure

```
tree_project/
├── driver_script.py      # Main script to run the analysis
├── download_model.py     # Script to download the DenseNet model
├── requirements.txt      # Python package dependencies
├── tree_images/         # Directory for input images
├── models/              # Directory for model files
│   ├── UrbanTreeDenseNet.pt
│   └── urban_tree_labels.txt
└── utils/               # Utility modules
    ├── database.py      # Database operations
    ├── image_processing.py  # Image processing functions
    ├── model_manager.py     # Model management
    ├── plant_id.py          # Tree identification
    ├── web_ui.py            # Web interface
    └── templates/           # HTML templates
        ├── index.html       # Main dashboard
        ├── map.html         # Map view
        └── edit.html        # Edit tree details
```

## Recent Updates

- Improved web interface with a clean, modern design
- Added interactive map view with tree clustering
- Enhanced tree data visualization
- Fixed tree ID sequencing in the table view
- Optimized map performance for large datasets
- Added support for viewing tree images directly from the interface

## Requirements

- Python 3.7+
- PyTorch
- Flask
- OpenCV
- NumPy
- Other dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Directory Structure

```
tree_project/
├── driver_script.py      # Main program entry point
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables (not tracked in Git)
├── .gitignore          # Git ignore rules
├── tree_images/        # Directory for input images
├── utils/
│   ├── __init__.py
│   ├── database.py      # Database operations
│   ├── geolocation.py   # GPS data extraction
│   ├── image_processing.py  # Image analysis
│   ├── plant_id.py      # Tree identification
│   ├── web_ui.py        # Web interface
│   └── templates/       # HTML templates
│       ├── base.html
│       ├── edit.html
│       ├── index.html
│       └── tree_details.html
└── README.md
```

## Usage

1. Place tree images in the `tree_images` directory
2. Run the application:
```bash
python driver_script.py
```
3. Access the web interface at `http://localhost:5000`

### Web Interface Features

- **Main Page**
  - Displays all analyzed trees in a table format
  - Shows tree images, type, dimensions, location, and confidence
  - Provides quick edit access for each entry
  - Export functionality to Excel

- **Edit Page**
  - Form to modify tree details
  - Image preview
  - Input validation
  - Cancel/Save options

### Image Requirements

- Supported formats: JPG, JPEG, PNG, BMP
- Must contain a reference object of known height (default: 180cm)
- GPS metadata recommended but not required
- Clear view of the entire tree

## API Integration

### Plant.id API

The project uses Plant.id API for tree identification. To use this:

1. Get an API key from [Plant.id](https://web.plant.id/)
2. Add the key to your `.env` file
3. The application will automatically use this for identification

### Database Schema

The SQLite database (`tree_analysis.db`) contains the following information for each tree:

- Image path and name
- Tree type and confidence level
- Height and width measurements
- GPS coordinates (latitude/longitude)
- Processing timestamp

## Development

### Adding New Features

1. Create new modules in the `utils` directory
2. Update `driver_script.py` to integrate new functionality
3. Add any new requirements to `requirements.txt`
4. Update documentation as needed

### Testing

- Test image processing with various tree types
- Verify GPS data extraction
- Check database operations
- Test web interface functionality

## Troubleshooting

Common issues and solutions:

1. **Images Not Displaying**
   - Verify image permissions
   - Check file format support
   - Ensure images are in `tree_images` directory

2. **API Key Issues**
   - Verify `.env` file exists
   - Check API key validity
   - Ensure proper environment variable loading

3. **Database Errors**
   - Check write permissions
   - Verify SQLite installation
   - Check for database corruption

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Plant.id API for tree identification
- OpenCV for image processing
- Flask for web interface
- Bootstrap for UI components
- SQLite for database management

# Tree Identification System

A system for identifying tree types from images using various pre-trained deep learning models.

## Model System

The system uses a modular approach to handle different pre-trained models for tree identification. This allows for easy testing and comparison of different models.

### Model Manager

The `ModelManager` class in `utils/model_manager.py` handles all model-related operations:

- Loading different pre-trained models
- Managing model configurations
- Processing images for model input
- Making predictions with confidence scores

### Adding New Models

To add a new model:

1. Place your model file (`.pt` or `.pth`) in the `models` directory
2. Create a corresponding labels file (`.txt`) with one label per line
3. Add the model configuration to the `model_configs` dictionary in `ModelManager`:

```python
"model_name": {
    "model_path": "path/to/model.pt",
    "labels_path": "path/to/labels.txt",
    "input_size": (224, 224),  # Required input size
    "confidence_threshold": 0.15,  # Minimum confidence for prediction
    "description": "Description of the model"
}
```

### Available Models

Currently available models:

1. DenseNet
   - Model file: `models/UrbanTreeDenseNet.pt`
   - Labels file: `models/tree_labels.txt`
   - Input size: 224x224
   - Confidence threshold: 15%

### Model Configuration

Each model configuration should include:

- `model_path`: Path to the model file
- `labels_path`: Path to the labels file
- `input_size`: Required input image size (width, height)
- `confidence_threshold`: Minimum confidence score for valid prediction
- `description`: Description of the model and its training

### Testing New Models

To test a new model:

1. Add the model configuration to `model_configs`
2. Load the model using `model_manager.load_model("model_name")`
3. Test predictions using `model_manager.identify_tree_type(image_path)`

### Example

```python
from utils.model_manager import ModelManager

# Initialize model manager
model_manager = ModelManager()

# Load a specific model
model_manager.load_model("densenet")

# Make predictions
tree_type, confidence = model_manager.identify_tree_type("path/to/image.jpg")
```

## Requirements

- Python 3.7+
- PyTorch
- torchvision
- Pillow
- Flask (for web interface)

## Installation

1. Clone the repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Place model files in the `models` directory
4. Run the application:
   ```bash
   python driver_script.py
   ```

## Usage

1. Place tree images in the `tree_images` directory
2. Run the application
3. Access the web interface at http://localhost:5000

## Contributing

To add a new model:

1. Train your model on tree images
2. Save the model file in the `models` directory
3. Create a labels file
4. Add the model configuration to `ModelManager`
5. Test the model
6. Submit a pull request with your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details. 