import cv2
import numpy as np
from datetime import datetime

class TreeAnalysisUI:
    def __init__(self):
        self.results = []
        self.summary_window = "Analysis Summary"
        self.summary_image = None

    def add_result(self, image_path, latitude, longitude, tree_type, height_m, width_m):
        """Add a new tree analysis result without displaying it"""
        self.results.append({
            'image_path': image_path,
            'latitude': latitude,
            'longitude': longitude,
            'tree_type': tree_type,
            'height_m': height_m,
            'width_m': width_m,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def show_summary(self):
        """Display summary of all analyzed trees"""
        if not self.results:
            return

        # Create a summary image
        summary_height = 600
        summary_width = 800
        summary_image = np.zeros((summary_height, summary_width, 3), dtype=np.uint8)
        
        # Add title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(summary_image, "Tree Analysis Summary", (20, 40), font, 1.0, (0, 255, 0), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(summary_image, f"Generated: {timestamp}", (20, 70), font, 0.5, (200, 200, 200), 1)
        
        # Add results
        y_position = 120
        for idx, result in enumerate(self.results, 1):
            # Add tree number and basic info
            tree_info = f"Tree #{idx}: {result['tree_type']}"
            cv2.putText(summary_image, tree_info, (20, y_position), font, 0.7, (255, 255, 255), 2)
            
            # Add details
            height_str = result['height_m'] if isinstance(result['height_m'], str) else f"{result['height_m']:.2f}m"
            width_str = result['width_m'] if isinstance(result['width_m'], str) else f"{result['width_m']:.2f}m"
            
            details = [
                f"Height: {height_str}",
                f"Width: {width_str}",
                f"Location: {result['latitude']}, {result['longitude']}",
                f"Analyzed: {result['timestamp']}"
            ]
            
            for detail in details:
                y_position += 30
                cv2.putText(summary_image, detail, (40, y_position), font, 0.6, (200, 200, 200), 1)
            
            y_position += 20

        # Store and display the summary image
        self.summary_image = summary_image
        cv2.namedWindow(self.summary_window, cv2.WINDOW_NORMAL)
        cv2.imshow(self.summary_window, summary_image)

    def wait_for_close(self):
        """Wait for user to close the windows"""
        print("\nPress 'q' to close all windows and exit...")
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break

# Create a global instance of the UI
ui = TreeAnalysisUI()

def display_data(image_path, latitude, longitude, tree_type, height_m, width_m):
    """
    Add result to summary without displaying it.
    """
    ui.add_result(image_path, latitude, longitude, tree_type, height_m, width_m)

def show_final_summary():
    """
    Display the final summary of all analyzed trees.
    """
    ui.show_summary()
    ui.wait_for_close()