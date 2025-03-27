import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tree_analysis.db')
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tree_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT UNIQUE NOT NULL,
                    image_name TEXT NOT NULL,
                    tree_type TEXT NOT NULL,
                    height_m REAL NOT NULL,
                    width_m REAL NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise

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