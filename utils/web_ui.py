"""
Web Interface Module for Tree Analysis Application

This module provides a Flask-based web interface for the tree analysis application.
It includes routes for displaying tree data in both table and map formats,
handling image serving, and exporting data to Excel.

Dependencies:
    - Flask: Web framework
    - pandas: Data manipulation and Excel export
    - openpyxl: Excel file handling
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, send_from_directory
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
from .database import Database
from .image_processing import calculate_tree_dimensions

# Get the absolute path to the tree_images directory
TREE_IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tree_images'))

# Initialize Flask app with the correct static folder
app = Flask(__name__, static_folder=TREE_IMAGES_DIR, static_url_path='/images')

def get_db():
    """Create a new database connection for each request"""
    return Database()

@app.route('/')
def index():
    """
    Render the main dashboard page displaying tree analysis results in a table format.
    
    Returns:
        str: Rendered HTML template with tree data
    """
    results = get_db().get_all_trees()
    trees = []
    for i, result in enumerate(results, start=1):
        # Extract filename from image_path
        image_name = os.path.basename(result[1])
        tree_data = {
            'id': i,  # Use sequential ID starting from 1
            'image_name': image_name,
            'image_path': result[1],
            'tree_type': result[3],
            'height_m': result[4],
            'width_m': result[5],
            'latitude': result[6],
            'longitude': result[7],
            'processed_date': result[8]
        }
        trees.append(tree_data)
    return render_template('index.html', trees=trees)

@app.route('/map')
def map_view():
    """
    Render the map view page showing tree locations on an interactive map.
    
    Returns:
        str: Rendered HTML template with tree data for map visualization
    """
    results = get_db().get_all_trees()
    tree_data = []
    for i, result in enumerate(results, start=1):
        # Extract filename from image_path
        image_name = os.path.basename(result[1])
        # Add a small offset based on the tree's index
        # This will spread the trees in a small area around the actual GPS coordinates
        offset = 0.0001  # approximately 10 meters
        lat_offset = offset * (i % 3)  # spread in 3 columns
        lon_offset = offset * (i // 3)  # spread in rows
        
        tree_data.append({
            'id': i,
            'image_name': image_name,
            'image_path': result[1],
            'tree_type': result[3],
            'height_m': result[4],
            'width_m': result[5],
            'latitude': result[6] + lat_offset,
            'longitude': result[7] + lon_offset,
            'processed_date': result[8]
        })

    return render_template('map.html', trees=tree_data)

@app.route('/images/<filename>')
def serve_image(filename):
    """
    Serve tree images from the tree_images directory.
    
    Args:
        filename (str): Name of the image file to serve
        
    Returns:
        Response: Image file with appropriate MIME type
    """
    return send_file(
        os.path.join('tree_images', filename),
        mimetype='image/jpeg'
    )

@app.route('/export')
def export_to_excel():
    """
    Export tree analysis data to an Excel file.
    
    The exported Excel file includes:
    - Tree ID (sequential)
    - Image name
    - Tree type
    - Height and width measurements
    - GPS coordinates
    - Processing date
    
    Returns:
        Response: Excel file with tree analysis data
    """
    try:
        # Get all trees from database
        results = get_db().get_all_trees()
        
        # Create a DataFrame
        data = []
        for i, result in enumerate(results, start=1):
            # Extract filename from image_path
            image_name = os.path.basename(result[1])
            data.append({
                'ID': i,  # Use sequential ID starting from 1
                'Image Name': image_name,
                'Tree Type': result[3],
                'Height (m)': f"{result[4]:.2f}",  # Format to 2 decimal places
                'Width (m)': f"{result[5]:.2f}",   # Format to 2 decimal places
                'Latitude': f"{result[6]:.6f}" if result[6] else "",
                'Longitude': f"{result[7]:.6f}" if result[7] else "",
                'Processed Date': result[8]
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel writer
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tree Analysis')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Tree Analysis']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tree_analysis_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error exporting to Excel: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (images)"""
    try:
        return send_from_directory(TREE_IMAGES_DIR, filename, as_attachment=False)
    except Exception as e:
        print(f"Error serving image {filename}: {str(e)}")
        return str(e), 404

@app.route('/edit_tree/<int:tree_id>', methods=['GET', 'POST'])
def edit_tree(tree_id):
    """Handle tree editing"""
    db = get_db()
    try:
        if request.method == 'POST':
            # Get form data
            tree_type = request.form.get('tree_type')
            height_m = float(request.form.get('height_m'))
            width_m = float(request.form.get('width_m'))
            latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
            longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
            
            # Update the tree in database
            success = db.update_tree(tree_id, tree_type, height_m, width_m, latitude, longitude)
            
            if success:
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to update tree'})
        
        # GET request - show edit form
        tree = db.get_tree_by_id(tree_id)
        if tree:
            return render_template('edit.html', tree=tree)
        else:
            return jsonify({'error': 'Tree not found'}), 404
    finally:
        del db  # Ensure database connection is closed

def start_web_interface():
    """Start the Flask web interface"""
    app.run(host='0.0.0.0', port=5000, debug=True) 