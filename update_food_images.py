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
    """Update menu items with images from the food images folder"""
    try:
        # Source directory with food images
        source_dir = Path("food images")
        # Destination directory for food images
        dest_dir = Path(settings.MEDIA_ROOT) / "food_images"
        
        # Create the destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"Looking for food images in {source_dir.absolute()}")
        print(f"Will save images to {dest_dir.absolute()}")
        
        # Dictionary mapping image filenames to menu item names
        image_mappings = {
            "plain roti.jpeg": "Plain Roti",
            "paneer-butter-masala-5.webp": "Paneer Butter Masala",
            "mix veg sabji.jpg": "Mix Veg Sabji",
            "JEERARICE_2.webp": "Jeera Rice",
            "Garlic naan.jpeg": "Garlic Naan",
            "punjabi-dal-tadka-recipe_1637897436.avif": "Dal Tadka",
            "restaurant-style-channa-masala-recipe-1-5.jpg": "Chana Masala",
            "aloo-gobi.jpg": "Aloo Gobi",
            "maxresdefault.jpg": "Butter Naan",  # Assuming this is Butter Naan
        }
        
        # Fast food image mappings - using the existing f*.png images from Static/images
        fast_food_mappings = {
            "f1.png": "Classic Chicken Burger",
            "f2.png": "Double Cheese Burger",
            "f3.png": "Veggie Supreme Burger",
            "f4.png": "Aloo Tikki Burger",
            "f5.png": "Tandoori Paneer Pizza",
            "f6.png": "Deluxe Veggie Pizza",
            "f7.png": "Chicken Supreme Pizza",
            "f8.png": "Cheese Overloaded Pizza",
            "f9.png": "Club Sandwich",
        }
        
        # Process traditional food images
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
                    rel_path = os.path.join('food_images', image_file)
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
        
        # Process fast food images (from Static/images directory)
        static_dir = Path(settings.STATICFILES_DIRS[0]) / "images"
        for image_file, menu_item_name in fast_food_mappings.items():
            source_file = static_dir / image_file
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
                    
                    images_updated += 1
                    print(f"Updated image for '{menu_item_name}'")
                    
                except MenuItem.DoesNotExist:
                    print(f"Menu item '{menu_item_name}' not found, skipping")
                except Exception as e:
                    print(f"Error updating image for '{menu_item_name}': {str(e)}")
            else:
                print(f"Image file '{image_file}' not found in Static/images directory")
                
        print(f"\nTotal images updated: {images_updated}")
        print("Image update completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 