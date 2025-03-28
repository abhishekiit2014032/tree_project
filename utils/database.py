"""
Database Management Module for Tree Analysis Application

This module handles all database operations for the tree analysis application.
It provides functionality for storing and retrieving tree data using SQLite.

The database schema includes:
- Tree ID (primary key)
- Image path
- Tree type
- Height and width measurements
- GPS coordinates
- Processing date
"""

import sqlite3
import os
from datetime import datetime
import logging

class Database:
    """Database management class for tree analysis data."""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = 'tree_analysis.db'
        self._create_tables()
    
    def _create_tables(self):
        """
        Create the necessary database tables if they don't exist.
        
        Creates a 'trees' table with columns for storing tree analysis data.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Create trees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                tree_type TEXT NOT NULL,
                height_m REAL NOT NULL,
                width_m REAL NOT NULL,
                latitude REAL,
                longitude REAL,
                processed_date TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_db_connection(self):
        """
        Create and return a database connection.
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_path)
    
    def add_tree(self, image_path, tree_type, height_m, width_m, latitude=None, longitude=None):
        """
        Add a new tree record to the database.
        
        Args:
            image_path (str): Path to the tree image (relative to tree_images directory)
            tree_type (str): Identified tree species
            height_m (float): Tree height in meters
            width_m (float): Tree width in meters
            latitude (float, optional): GPS latitude
            longitude (float, optional): GPS longitude
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store only the filename in the database
            image_filename = os.path.basename(image_path)
            logging.info(f"Storing image filename: {image_filename}")
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trees (image_path, tree_type, height_m, width_m, latitude, longitude, processed_date)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (image_filename, tree_type, height_m, width_m, latitude, longitude))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error adding tree to database: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_all_trees(self):
        """
        Retrieve all tree records from the database.
        
        Returns:
            list: List of tuples containing tree data
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trees ORDER BY id')
        trees = cursor.fetchall()
        
        conn.close()
        return trees
    
    def get_tree(self, tree_id):
        """
        Retrieve a specific tree record by ID.
        
        Args:
            tree_id (int): ID of the tree to retrieve
            
        Returns:
            tuple: Tree data if found, None otherwise
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trees WHERE id = ?', (tree_id,))
        tree = cursor.fetchone()
        
        conn.close()
        return tree
    
    def update_tree(self, tree_id, tree_type=None, height_m=None, width_m=None, latitude=None, longitude=None):
        """
        Update an existing tree record.
        
        Args:
            tree_id (int): ID of the tree to update
            tree_type (str, optional): New tree species
            height_m (float, optional): New height in meters
            width_m (float, optional): New width in meters
            latitude (float, optional): New GPS latitude
            longitude (float, optional): New GPS longitude
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided parameters
        update_fields = []
        values = []
        
        if tree_type is not None:
            update_fields.append('tree_type = ?')
            values.append(tree_type)
        if height_m is not None:
            update_fields.append('height_m = ?')
            values.append(height_m)
        if width_m is not None:
            update_fields.append('width_m = ?')
            values.append(width_m)
        if latitude is not None:
            update_fields.append('latitude = ?')
            values.append(latitude)
        if longitude is not None:
            update_fields.append('longitude = ?')
            values.append(longitude)
        
        if not update_fields:
            conn.close()
            return False
        
        # Add tree_id to values
        values.append(tree_id)
        
        # Execute update query
        query = f'''
            UPDATE trees 
            SET {', '.join(update_fields)}
            WHERE id = ?
        '''
        
        cursor.execute(query, values)
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def delete_tree(self, tree_id):
        """
        Delete a tree record from the database.
        
        Args:
            tree_id (int): ID of the tree to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM trees WHERE id = ?', (tree_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success

    def get_tree_by_image_path(self, image_path):
        """
        Retrieve a tree record by image path.
        
        Args:
            image_path (str): Path to the tree image
            
        Returns:
            tuple: Tree data if found, None otherwise
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trees WHERE image_path = ?', (image_path,))
        tree = cursor.fetchone()
        
        conn.close()
        return tree

# Create a singleton instance
_db = None

def get_db():
    """
    Get or create the database singleton instance.
    
    Returns:
        Database: Database instance
    """
    global _db
    if _db is None:
        _db = Database()
    return _db

    def save_tree_data(self, image_path, image_name, tree_type, height_m, width_m, latitude=None, longitude=None):
        """Save tree analysis data to database"""
        try:
            # Convert GPS coordinates to float if they exist
            if latitude is not None:
                latitude = float(latitude)
            if longitude is not None:
                longitude = float(longitude)
                
            self.cursor.execute('''
                INSERT OR REPLACE INTO tree_analysis 
                (image_path, image_name, tree_type, height_m, width_m, 
                latitude, longitude, processed_date, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (image_path, image_name, tree_type, height_m, width_m, 
                 latitude, longitude, datetime.now(), datetime.now()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving tree data: {e}")
            return False

    def get_all_trees(self):
        """Retrieve all tree analysis records"""
        try:
            self.cursor.execute('''
                SELECT id, image_path, image_name, tree_type, height_m, width_m,
                       latitude, longitude, processed_date
                FROM tree_analysis 
                ORDER BY processed_date DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving tree data: {e}")
            return []

    def get_tree_by_id(self, tree_id):
        """Retrieve a specific tree analysis record by ID"""
        try:
            self.cursor.execute('SELECT * FROM tree_analysis WHERE id = ?', (tree_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving tree data: {e}")
            return None

    def update_tree_data(self, tree_id, tree_type=None, height=None, width=None, latitude=None, longitude=None, confidence=None):
        """Update tree analysis data"""
        try:
            updates = []
            values = []
            if tree_type is not None:
                updates.append('tree_type = ?')
                values.append(tree_type)
            if height is not None:
                updates.append('height_m = ?')
                values.append(height)
            if width is not None:
                updates.append('width_m = ?')
                values.append(width)
            if latitude is not None:
                updates.append('latitude = ?')
                values.append(latitude)
            if longitude is not None:
                updates.append('longitude = ?')
                values.append(longitude)
            if confidence is not None:
                updates.append('confidence = ?')
                values.append(confidence)

            if updates:
                query = f"UPDATE tree_analysis SET {', '.join(updates)} WHERE id = ?"
                values.append(tree_id)
                self.cursor.execute(query, values)
                self.conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error updating tree data: {e}")
            return False

    def clear_database(self):
        """Clear all records from the database"""
        try:
            self.cursor.execute('DELETE FROM tree_analysis')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing database: {e}")
            return False

    def __del__(self):
        """Close database connection when object is destroyed"""
        if self.conn:
            self.conn.close()

    def image_needs_processing(self, image_path, force_refresh=False):
        """
        Check if an image needs processing by comparing file modification time
        with database entry timestamp
        """
        if not os.path.exists(image_path):
            return True
            
        if force_refresh:
            return True

        file_mtime = os.path.getmtime(image_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT processed_date 
                FROM tree_analysis 
                WHERE image_path = ?
            ''', (image_path,))
            
            result = cursor.fetchone()
            
            if not result:
                return True
                
            # Convert processed_date string to timestamp
            processed_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
            processed_timestamp = processed_date.timestamp()
            
            # If file was modified after last processing, it needs reprocessing
            return file_mtime > processed_timestamp
            
        finally:
            conn.close()

    def add_result(self, image_path, image_name, tree_type, height_m, width_m, 
                  latitude, longitude, confidence):
        """Add or update a tree analysis result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO tree_analysis 
                (image_path, image_name, tree_type, height_m, width_m, 
                latitude, longitude, confidence, processed_date, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (image_path, image_name, tree_type, height_m, width_m,
                 latitude, longitude, confidence, datetime.now(), datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding result to database: {str(e)}")
            return False
        finally:
            conn.close()

    def get_result(self, image_path):
        """Retrieve a tree analysis result by image path"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT tree_type, height_m, width_m, latitude, longitude, confidence
                FROM tree_analysis
                WHERE image_path = ?
            ''', (image_path,))
            
            result = cursor.fetchone()
            if result:
                # Update last accessed timestamp
                cursor.execute('''
                    UPDATE tree_analysis
                    SET last_accessed = ?
                    WHERE image_path = ?
                ''', (datetime.now(), image_path))
                conn.commit()
                
                return {
                    'tree_type': result[0],
                    'height_m': result[1],
                    'width_m': result[2],
                    'latitude': result[3],
                    'longitude': result[4],
                    'confidence': result[5]
                }
            return None
        finally:
            conn.close()

    def get_all_results(self):
        """Retrieve all tree analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT image_path, image_name, tree_type, height_m, width_m,
                       latitude, longitude, confidence, processed_date
                FROM tree_analysis
                ORDER BY processed_date DESC
            ''')
            
            return cursor.fetchall()
        finally:
            conn.close()

    def get_processed_images(self):
        """Get a list of all processed image paths"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT image_path FROM tree_analysis')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_tree(self, tree_id, tree_type, height_m, width_m, latitude, longitude):
        """Update tree details in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE tree_analysis 
                SET tree_type = ?, 
                    height_m = ?, 
                    width_m = ?, 
                    latitude = ?, 
                    longitude = ?,
                    last_accessed = ?
                WHERE id = ?
            ''', (tree_type, height_m, width_m, latitude, longitude, datetime.now(), tree_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating tree in database: {str(e)}")
            return False
        finally:
            conn.close()

    def get_tree_by_id(self, tree_id):
        """Get tree details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, image_path, image_name, tree_type, height_m, width_m, 
                       latitude, longitude, processed_date, last_accessed
                FROM tree_analysis
                WHERE id = ?
            ''', (tree_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'image_path': result[1],
                    'image_name': result[2],
                    'tree_type': result[3],
                    'height_m': result[4],
                    'width_m': result[5],
                    'latitude': result[6],
                    'longitude': result[7],
                    'processed_date': result[8],
                    'last_accessed': result[9]
                }
            return None
        finally:
            conn.close() 