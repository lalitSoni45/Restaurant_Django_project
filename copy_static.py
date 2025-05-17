import os
import shutil
from pathlib import Path

# Define source and destination directories
source_dir = Path('my_restaurant/Static')
dest_dir = Path('static')

# Create destination directory if it doesn't exist
os.makedirs(dest_dir, exist_ok=True)

# Copy all files and subdirectories from source to destination
def copy_files(src, dst):
    for item in os.listdir(src):
        s = src / item
        d = dst / item
        
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            copy_files(s, d)
        else:
            # Only copy if the file doesn't exist or is newer
            if not os.path.exists(d) or os.path.getmtime(s) > os.path.getmtime(d):
                shutil.copy2(s, d)
                print(f"Copied: {s} -> {d}")

# Run the copy process
try:
    copy_files(source_dir, dest_dir)
    print("Static files copied successfully!")
except Exception as e:
    print(f"Error copying files: {e}") 