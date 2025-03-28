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

from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory, jsonify
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
from .database import Database
import logging
import math

# Set up image directory path
TREE_IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tree_images'))

# Initialize Flask app
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
           static_folder=TREE_IMAGES_DIR,
           static_url_path='/images')

# Initialize database
db = Database()

@app.route('/')
def index():
    """Render the main page with tree data table."""
    try:
        trees = db.get_all_trees()
        tree_data = []
        
        for tree in trees:
            tree_info = {
                'id': tree[0],
                'image_path': tree[1],
                'tree_type': tree[2],
                'type_confidence': tree[3],
                'height_m': tree[4],
                'width_m': tree[5],
                'measurement_method': tree[6],
                'measurement_confidence': tree[7],
                'latitude': tree[8],
                'longitude': tree[9],
                'altitude': tree[10],
                'timestamp': tree[11]
            }
            tree_data.append(tree_info)
            
        return render_template('index.html', trees=tree_data)
    except Exception as e:
        logging.error(f"Error rendering index page: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/map')
def map_view():
    """Render the map view with tree locations."""
    try:
        trees = db.get_all_trees()
        tree_data = []
        
        for tree in trees:
            tree_info = {
                'id': tree[0],
                'image_path': tree[1],
                'tree_type': tree[2],
                'type_confidence': tree[3],
                'height_m': tree[4],
                'width_m': tree[5],
                'measurement_method': tree[6],
                'measurement_confidence': tree[7],
                'latitude': tree[8],
                'longitude': tree[9],
                'altitude': tree[10],
                'timestamp': tree[11]
            }
            tree_data.append(tree_info)
            
        return render_template('map.html', trees=tree_data)
    except Exception as e:
        logging.error(f"Error rendering map view: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve tree images."""
    try:
        return send_from_directory(TREE_IMAGES_DIR, filename)
    except Exception as e:
        logging.error(f"Error serving image {filename}: {str(e)}")
        return '', 404

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
        results = db.get_all_trees()
        
        # Create a DataFrame
        data = []
        for i, result in enumerate(results, start=1):
            # Extract filename from image_path
            image_name = os.path.basename(result[1])
            data.append({
                'ID': i,  # Use sequential ID starting from 1
                'Image Name': image_name,
                'Tree Type': result[2],
                'Height (m)': f"{result[4]:.2f}",  # Format to 2 decimal places
                'Width (m)': f"{result[5]:.2f}",   # Format to 2 decimal places
                'Latitude': f"{result[8]:.6f}" if result[8] else "",
                'Longitude': f"{result[9]:.6f}" if result[9] else "",
                'Processed Date': result[11]
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
        logging.error(f"Error exporting to Excel: {str(e)}")
        return str(e), 500

@app.route('/edit_tree/<int:tree_id>', methods=['GET', 'POST'])
def edit_tree(tree_id):
    """Handle tree editing"""
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
                return {'status': 'success'}
            else:
                return {'status': 'error', 'message': 'Failed to update tree'}, 500
        
        # GET request - show edit form
        tree = db.get_tree_by_id(tree_id)
        if tree:
            return render_template('edit.html', tree=tree)
        else:
            return {'error': 'Tree not found'}, 404
    except Exception as e:
        logging.error(f"Error editing tree: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/trees')
def get_trees():
    """API endpoint to get tree data in JSON format."""
    try:
        trees = db.get_all_trees()
        tree_data = []
        
        for tree in trees:
            tree_info = {
                'id': tree[0],
                'image_path': tree[1],
                'tree_type': tree[2],
                'type_confidence': tree[3],
                'height_m': tree[4],
                'width_m': tree[5],
                'measurement_method': tree[6],
                'measurement_confidence': tree[7],
                'latitude': tree[8],
                'longitude': tree[9],
                'altitude': tree[10],
                'timestamp': tree[11]
            }
            tree_data.append(tree_info)
            
        return jsonify(tree_data)
    except Exception as e:
        logging.error(f"Error getting tree data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def start_web_interface():
    """Start the Flask web interface."""
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error starting web interface: {str(e)}")
        raise 