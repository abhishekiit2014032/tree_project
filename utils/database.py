import sqlite3
import os
from datetime import datetime

class TreeDatabase:
    def __init__(self, db_path="tree_analysis.db"):
        """Initialize database with persistent storage"""
        self.db_path = db_path
        self._create_database()

    def _create_database(self):
        """Create the database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for tree analysis results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tree_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT UNIQUE,
                image_name TEXT,
                tree_type TEXT,
                height_m REAL,
                width_m REAL,
                latitude TEXT,
                longitude TEXT,
                confidence REAL,
                processed_date TIMESTAMP,
                last_accessed TIMESTAMP,
                hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

<<<<<<< HEAD
    def image_needs_processing(self, image_path, force_refresh=False):
=======
    def image_needs_processing(self, image_path):
>>>>>>> 30295fea7552591f2e02c26203007b00277688b0
        """
        Check if an image needs processing by comparing file modification time
        with database entry timestamp
        """
        if not os.path.exists(image_path):
            return True
<<<<<<< HEAD
            
        if force_refresh:
            return True
=======
>>>>>>> 30295fea7552591f2e02c26203007b00277688b0

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

    def clear_database(self):
        """Clear all data and recreate the database"""
        try:
            # Close any existing connections
            conn = sqlite3.connect(self.db_path)
            conn.close()
            
            # Remove the database file
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print(f"Removed existing database: {self.db_path}")
            
            # Recreate the database
            self._create_database()
            print("Created fresh database")
            return True
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return False

    def get_processed_images(self):
        """Get a list of all processed image paths"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT image_path FROM tree_analysis')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close() 