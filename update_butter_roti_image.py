import os
import django
import sys
import shutil
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import MenuItem
from django.conf import settings
from django.core.files.images import ImageFile

def main():
    """Update Butter Roti menu item with image"""
    try:
        # Source directory with food images
        source_dir = Path("food images")
        # Destination directory for food images
        dest_dir = Path(settings.MEDIA_ROOT) / "food_images"
        
        # Create the destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"Looking for Butter Roti image in {source_dir.absolute()}")
        print(f"Will save image to {dest_dir.absolute()}")
        
        # Image file for Butter Roti
        image_file = "maxresdefault.jpg"
        menu_item_name = "Butter Roti"  # Correct name in database
        
        source_file = source_dir / image_file
        if source_file.exists():
            try:
                # Find the menu item
                menu_item = MenuItem.objects.get(name=menu_item_name)
                
                # Copy the image to the media folder
                dest_file = dest_dir / image_file
                shutil.copy2(source_file, dest_file)
                
                # Update the menu item with the new image path
                rel_path = os.path.join('food_images', image_file)
                with open(dest_file, 'rb') as img_file:
                    menu_item.image.save(image_file, ImageFile(img_file), save=True)
                
                print(f"Updated image for '{menu_item_name}'")
                
            except MenuItem.DoesNotExist:
                print(f"Menu item '{menu_item_name}' not found, skipping")
            except Exception as e:
                print(f"Error updating image for '{menu_item_name}': {str(e)}")
        else:
            print(f"Image file '{image_file}' not found in source directory")
            
        print("Image update completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 