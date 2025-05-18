import os
import django
import sys
import shutil
from pathlib import Path
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import MenuItem
from django.conf import settings
from django.core.files.images import ImageFile

def main():
    """Add drink images to the drink menu items from the drinks folder"""
    try:
        # Destination directory for food images
        dest_dir = Path(settings.MEDIA_ROOT) / "food_images"
        
        # Create the destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"Will save images to {dest_dir.absolute()}")
        
        # Source directory with proper drink images
        source_dir = Path("drinks")
        
        if not source_dir.exists():
            print(f"Error: Drinks directory not found at {source_dir.absolute()}")
            return
        
        print(f"Found drinks image directory at {source_dir.absolute()}")
        
        # Get all drink items
        drink_items = MenuItem.objects.filter(category__name="Drinks")
        print(f"Found {drink_items.count()} drink items")
        
        # Update each drink with an image
        images_updated = 0
        for drink_item in drink_items:
            try:
                # Find the corresponding image file
                image_file = None
                for file in source_dir.glob("*.*"):
                    # Check if filename (without extension) matches drink name
                    if file.stem.lower() == drink_item.name.lower() or file.stem.lower() in drink_item.name.lower():
                        image_file = file
                        break
                
                if not image_file:
                    print(f"No matching image found for '{drink_item.name}', skipping")
                    continue
                
                # Create a new filename for the drink image
                new_filename = f"drink_{slugify(drink_item.name)}{image_file.suffix}"
                dest_file = dest_dir / new_filename
                
                # Copy the image to the media folder
                shutil.copy2(image_file, dest_file)
                
                # Update the menu item with the new image path
                with open(dest_file, 'rb') as img_file:
                    drink_item.image.save(new_filename, ImageFile(img_file), save=True)
                
                images_updated += 1
                print(f"Updated image for '{drink_item.name}' using {image_file.name}")
                
            except Exception as e:
                print(f"Error updating image for '{drink_item.name}': {str(e)}")
                
        print(f"\nTotal drink images updated: {images_updated}")
        print("Drink image update completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 