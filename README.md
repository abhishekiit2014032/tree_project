# Tree Analysis Project

A Python-based application that analyzes tree images to extract information about tree types, dimensions, and locations. The project uses computer vision techniques and machine learning to identify trees and calculate their dimensions, with a modern web interface for viewing and managing the analysis results.

## Features

- **Tree Type Identification**
  - Uses Plant.id API for accurate tree species identification
  - Provides confidence scores for identifications
  - Supports multiple tree species

- **Dimension Analysis**
  - Calculates tree height and width using computer vision
  - Uses reference object for accurate scaling
  - Supports measurements in meters

- **Location Tracking**
  - Extracts GPS coordinates from image EXIF metadata
  - Displays location data in a user-friendly format
  - Handles cases where GPS data is not available

- **Modern Web Interface**
  - Clean, responsive design using Bootstrap
  - Real-time data updates
  - Image preview functionality
  - Edit capabilities for all tree data
  - Sortable and filterable results table

- **Data Management**
  - SQLite database for persistent storage
  - Excel export functionality
  - Automatic image processing
  - Caching system to avoid reprocessing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/abhishekiit2014032/tree_project.git
cd tree_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Plant.id API key:
```
PLANT_ID_API_KEY=your_api_key_here
```

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