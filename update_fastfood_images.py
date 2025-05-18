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
    """Update fast food menu items with images from the fast food images folder"""
    try:
        # Source directory with fast food images
        source_dir = Path("fast food images")
        # Destination directory for food images
        dest_dir = Path(settings.MEDIA_ROOT) / "food_images"
        
        # Create the destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"Looking for fast food images in {source_dir.absolute()}")
        print(f"Will save images to {dest_dir.absolute()}")
        
        # Dictionary mapping image filenames to menu item names
        image_mappings = {
            "Classic Chicken Burger.jpeg": "Classic Chicken Burger",
            "Double Cheese Burger.jpg": "Double Cheese Burger",
            "Veggie Supreme Burger.jpeg": "Veggie Supreme Burger",
            "Aloo Tikki Burger.jpeg": "Aloo Tikki Burger",
            "Tandoori Paneer Pizza.jpeg": "Tandoori Paneer Pizza",
            "Deluxe Veggie Pizza.jpeg": "Deluxe Veggie Pizza",
            "Chicken Supreme Pizza.jpeg": "Chicken Supreme Pizza",
            "Cheese Overloaded Pizza.jpeg": "Cheese Overloaded Pizza",
            "Club Sandwich.jpeg": "Club Sandwich",
            "Grilled Cheese Sandwich.jpg": "Grilled Cheese Sandwich",
            "Cheese Garlic Bread.jpeg": "Cheese Garlic Bread",
            "Loaded Nacho.jpeg": "Loaded Nachos",
            "Chicken Wings.jpeg": "Chicken Wings",
            "Onion Rings.jpeg": "Onion Rings",
            "Veg Wrap.jpg": "Veg Wrap",
            "Chicken Tikka Wrap.jpeg": "Chicken Tikka Wrap",
            "Classic Burger.jpeg": "Classic Burger",
            "Cheese Burger.jpeg": "Cheese Burger",
            "Margherita Pizza.jpg": "Margherita Pizza",
            "Pepperoni Pizza.jpeg": "Pepperoni Pizza",
            "Spaghetti Bolognese.jpeg": "Spaghetti Bolognese",
            "Fettuccine Alfredo.jpg": "Fettuccine Alfredo",
            "French Fries.jpeg": "French Fries",
            "Loaded Fries.jpeg": "Loaded Fries",
        }
        
        # Process fast food images
        images_updated = 0
        for image_file, menu_item_name in image_mappings.items():
            source_file = source_dir / image_file
            if source_file.exists():
                try:
                    # Find the menu item
                    menu_item = MenuItem.objects.get(name=menu_item_name)
                    
                    # Copy the image to the media folder
                    dest_file = dest_dir / image_file
                    shutil.copy2(source_file, dest_file)
                    
                    # Update the menu item with the new image path
                    with open(dest_file, 'rb') as img_file:
                        menu_item.image.save(image_file, ImageFile(img_file), save=True)
                    
                    images_updated += 1
                    print(f"Updated image for '{menu_item_name}'")
                    
                except MenuItem.DoesNotExist:
                    print(f"Menu item '{menu_item_name}' not found, skipping")
                except Exception as e:
                    print(f"Error updating image for '{menu_item_name}': {str(e)}")
            else:
                print(f"Image file '{image_file}' not found in source directory")
                
        print(f"\nTotal images updated: {images_updated}")
        print("Fast food image update completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 