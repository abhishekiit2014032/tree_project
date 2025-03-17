# Tree Analysis Project

A Python-based application that analyzes tree images to extract information about tree types, dimensions, and locations. The project uses computer vision techniques and machine learning to identify trees and calculate their dimensions.

## Features

- Tree type identification using Plant.id API
- Height and width calculation using computer vision
- GPS data extraction from image EXIF metadata
- Web-based user interface for viewing and editing results
- Excel export functionality
- Persistent storage using SQLite database
- Image caching to avoid reprocessing

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Flask
- Pandas
- XlsxWriter
- Pillow
- Requests
- Geopy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tree_project.git
cd tree_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Plant.id API key:
   - Get an API key from [Plant.id](https://web.plant.id/)
   - Update the `API_KEY` variable in `driver_script.py`

## Usage

1. Place your tree images in the `tree_images` directory
2. Run the program:
```bash
python driver_script.py
```
3. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
tree_project/
├── driver_script.py      # Main program entry point
├── requirements.txt      # Project dependencies
├── tree_images/         # Directory for input images
├── utils/
│   ├── __init__.py
│   ├── database.py      # Database operations
│   ├── geolocation.py   # GPS data extraction
│   ├── image_processing.py  # Image analysis
│   ├── plant_id.py      # Tree identification
│   ├── web_ui.py        # Web interface
│   └── templates/       # HTML templates
└── README.md
```

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