from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, send_from_directory
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
from .database import TreeDatabase

app = Flask(__name__)
db = TreeDatabase()

@app.route('/')
def index():
    """Display all analyzed trees in a table format"""
    results = db.get_all_results()
    # Convert tuple results to dictionaries
    trees = []
    for result in results:
        trees.append({
            'image_path': result[0],
            'image_name': result[1],
            'tree_type': result[2],
            'height_m': result[3],
            'width_m': result[4],
            'latitude': result[5],
            'longitude': result[6],
            'confidence': result[7],
            'processed_date': result[8]
        })
    return render_template('index.html', trees=trees)

@app.route('/export')
def export_excel():
    """Export tree data to Excel"""
    results = db.get_all_results()
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=[
        'image_path', 'image_name', 'tree_type', 'height_m', 'width_m',
        'latitude', 'longitude', 'confidence', 'processed_date'
    ])
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Tree Analysis', index=False)
        
        # Get the workbook and the worksheet
        workbook = writer.book
        worksheet = writer.sheets['Tree Analysis']
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#f8f9fa',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Auto-adjust columns width
        for idx, col in enumerate(df):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.set_column(idx, idx, max_length + 2)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='tree_analysis.xlsx'
    )

@app.route('/edit/<image_name>', methods=['GET', 'POST'])
def edit_tree(image_name):
    """Edit tree details"""
    if request.method == 'POST':
        # Update tree details in database
        db.update_result(
            image_name=image_name,
            tree_type=request.form['tree_type'],
            height_m=float(request.form['height_m']),
            width_m=float(request.form['width_m']),
            latitude=request.form['latitude'],
            longitude=request.form['longitude'],
            confidence=float(request.form['confidence'])
        )
        return redirect(url_for('index'))
    
    # Get current tree details
    tree = db.get_result(image_name)
    return render_template('edit.html', tree=tree)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (images)"""
    return send_from_directory('tree_images', filename)

@app.route('/tree/<path:image_path>')
def tree_details(image_path):
    """Display detailed view of a single tree analysis"""
    result = db.get_result(image_path)
    if result:
        return render_template('tree_details.html', 
                             image_path=image_path,
                             result=result)
    return "Tree not found", 404

@app.route('/api/update_tree', methods=['POST'])
def update_tree():
    """Update tree analysis details"""
    try:
        data = request.json
        image_path = data.get('image_path')
        updates = {
            'tree_type': data.get('tree_type'),
            'height_m': float(data.get('height_m', 0)),
            'width_m': float(data.get('width_m', 0)),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'confidence': float(data.get('confidence', 0))
        }
        
        # Get existing result to preserve image_name
        existing = db.get_result(image_path)
        if existing:
            db.add_result(
                image_path=image_path,
                image_name=os.path.basename(image_path),
                **updates
            )
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Tree not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/image/<path:image_path>')
def serve_image(image_path):
    """Serve the tree image"""
    try:
        return send_file(image_path)
    except Exception as e:
        return str(e), 404

def run_web_ui(host='0.0.0.0', port=5000):
    """Run the Flask web application"""
    app.run(host=host, port=port, debug=True) 