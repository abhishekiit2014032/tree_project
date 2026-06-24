# 🌳 Tree Analysis Project

A powerful application that combines computer vision and machine learning to analyze trees in urban environments. This tool can identify tree species, calculate dimensions, and map tree locations with high accuracy.

Live At: https://tree-project-bf600.web.app/index.html
         mapView:  https://tree-project-bf600.web.app/map.html



![Tree Project Demo](https://raw.githubusercontent.com/abhishekiit2014032/tree_project/main/chrome-capture-2026-06-24.gif)

## ✨ Key Features

### 🌿 Tree Identification
- Advanced DenseNet model for accurate species identification
- Support for multiple tree species
- Confidence scoring for predictions
- Real-time processing capabilities

### 📏 Dimension Analysis
- Precise height and width measurements
- Reference-based scaling for accurate results
- Support for various measurement units
- Automated dimension calculation

### 📍 Location Tracking
- GPS coordinate extraction from images
- Interactive map visualization
- Tree clustering for better visualization
- Location-based analysis

### 🖥️ Modern Web Interface
- Clean, responsive dashboard
- Interactive data tables
- Real-time map view
- Excel export functionality
- Image preview capabilities

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- PyTorch
- OpenCV
- Flask
- Other dependencies listed in requirements.txt

### Installation

1. Clone the repository:
```bash
git clone https://github.com/abhishekiit2014032/tree_project.git
cd tree_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the model:
```bash
python download_model.py
```

### Usage

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

## 🏗️ Project Structure

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

## 🔄 Recent Updates

### UI Improvements
- 🎨 Modern, clean interface design
- 📱 Responsive layout for all devices
- 🗺️ Interactive map view with clustering
- 📊 Enhanced data visualization

### Functionality Enhancements
- 🔍 Improved tree identification accuracy
- 📏 More precise dimension calculations
- 📍 Better GPS coordinate handling
- 📤 Streamlined data export

### Performance Optimizations
- ⚡ Faster image processing
- 💾 Efficient data storage
- 🔄 Optimized map rendering
- 📊 Better handling of large datasets

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- DenseNet model architecture
- OpenStreetMap for map visualization
- Flask web framework
- All contributors and users of this project

---
Made with ❤️ for urban forestry and environmental conservation 
