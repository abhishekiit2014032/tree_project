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
    
    def __init__(self, db_path='tree_analysis.db'):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise
    
    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS trees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    tree_type TEXT,
                    type_confidence REAL,
                    height_m REAL,
                    width_m REAL,
                    measurement_method TEXT,
                    measurement_confidence REAL,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error creating tables: {str(e)}")
            raise
    
    def add_tree(self, image_path, tree_type, height_m, width_m, type_confidence=None,
                 measurement_method=None, measurement_confidence=None, gps_data=None):
        """
        Add a tree record to the database.
        
        Args:
            image_path (str): Path to the image file
            tree_type (str): Identified tree type
            height_m (float): Tree height in meters
            width_m (float): Tree width in meters
            type_confidence (float, optional): Confidence in tree type identification
            measurement_method (str, optional): Method used for measurement
            measurement_confidence (float, optional): Confidence in measurements
            gps_data (dict, optional): GPS coordinates and altitude
        """
        try:
            # Extract GPS data if provided
            latitude = None
            longitude = None
            altitude = None
            if gps_data:
                latitude = gps_data.get('latitude')
                longitude = gps_data.get('longitude')
                altitude = gps_data.get('altitude')
            
            # Store only the filename, not the full path
            image_filename = os.path.basename(image_path)
            
            self.cursor.execute('''
                INSERT INTO trees (
                    image_path, tree_type, type_confidence,
                    height_m, width_m, measurement_method,
                    measurement_confidence, latitude, longitude, altitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_filename, tree_type, type_confidence,
                height_m, width_m, measurement_method,
                measurement_confidence, latitude, longitude, altitude
            ))
            self.conn.commit()
            logging.info(f"Added tree record for {image_filename}")
            
        except Exception as e:
            logging.error(f"Error adding tree record: {str(e)}")
            self.conn.rollback()
            raise
    
    def get_tree_by_image_path(self, image_path):
        """
        Get tree record by image path.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: Tree record or None if not found
        """
        try:
            # Use only the filename for lookup
            image_filename = os.path.basename(image_path)
            
            self.cursor.execute('''
                SELECT * FROM trees WHERE image_path = ?
            ''', (image_filename,))
            return self.cursor.fetchone()
            
        except Exception as e:
            logging.error(f"Error retrieving tree record: {str(e)}")
            return None
    
    def get_all_trees(self):
        """
        Get all tree records.
        
        Returns:
            list: List of tree records
        """
        try:
            self.cursor.execute('SELECT * FROM trees')
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error retrieving all trees: {str(e)}")
            return []
    
    def update_tree(self, tree_id, tree_type, height_m, width_m, type_confidence=None,
                    measurement_method=None, measurement_confidence=None, gps_data=None):
        """
        Update an existing tree record.
        
        Args:
            tree_id (int): ID of the tree record to update
            tree_type (str): Updated tree type
            height_m (float): Updated height in meters
            width_m (float): Updated width in meters
            type_confidence (float, optional): Updated type confidence
            measurement_method (str, optional): Updated measurement method
            measurement_confidence (float, optional): Updated measurement confidence
            gps_data (dict, optional): Updated GPS data
        """
        try:
            # Extract GPS data if provided
            latitude = None
            longitude = None
            altitude = None
            if gps_data:
                latitude = gps_data.get('latitude')
                longitude = gps_data.get('longitude')
                altitude = gps_data.get('altitude')
            
            self.cursor.execute('''
                UPDATE trees SET
                    tree_type = ?,
                    type_confidence = ?,
                    height_m = ?,
                    width_m = ?,
                    measurement_method = ?,
                    measurement_confidence = ?,
                    latitude = ?,
                    longitude = ?,
                    altitude = ?,
                    timestamp = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                tree_type, type_confidence,
                height_m, width_m,
                measurement_method, measurement_confidence,
                latitude, longitude, altitude,
                tree_id
            ))
            self.conn.commit()
            logging.info(f"Updated tree record {tree_id}")
            
        except Exception as e:
            logging.error(f"Error updating tree record: {str(e)}")
            self.conn.rollback()
            raise
    
    def delete_tree(self, tree_id):
        """
        Delete a tree record.
        
        Args:
            tree_id (int): ID of the tree record to delete
        """
        try:
            self.cursor.execute('DELETE FROM trees WHERE id = ?', (tree_id,))
            self.conn.commit()
            logging.info(f"Deleted tree record {tree_id}")
        except Exception as e:
            logging.error(f"Error deleting tree record: {str(e)}")
            self.conn.rollback()
            raise
    
    def clean_database(self):
        """Remove all records from the database."""
        try:
            self.cursor.execute('DELETE FROM trees')
            self.conn.commit()
            logging.info("Database cleaned")
        except Exception as e:
            logging.error(f"Error cleaning database: {str(e)}")
            self.conn.rollback()
            raise
    
    def __del__(self):
        """Close database connection on object destruction."""
        if self.conn:
            self.conn.close()

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