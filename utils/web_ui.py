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
    results = get_db().get_all_trees()
    trees = []
    for i, result in enumerate(results, start=1):
        # Extract filename from image_path
        image_name = os.path.basename(result[1])
        tree_data = {
            'id': i,  # Use the enumerated index starting from 1
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
    results = get_db().get_all_trees()
    tree_data = []
    for i, result in enumerate(results):
        # Extract filename from image_path
        image_name = os.path.basename(result[1])
        # Add a small offset based on the tree's index
        # This will spread the trees in a small area around the actual GPS coordinates
        offset = 0.0001  # approximately 10 meters
        lat_offset = offset * (i % 3)  # spread in 3 columns
        lon_offset = offset * (i // 3)  # spread in rows
        
        tree_data.append({
            'id': result[0],
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
    """Serve tree images"""
    try:
        return send_from_directory(TREE_IMAGES_DIR, filename, as_attachment=False)
    except Exception as e:
        print(f"Error serving image {filename}: {str(e)}")
        return str(e), 404

@app.route('/export')
def export_excel():
    """Export tree data to Excel"""
    try:
        get_db().export_to_excel()
        return send_file('tree_analysis.xlsx', as_attachment=True)
    except Exception as e:
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