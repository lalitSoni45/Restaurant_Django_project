import os
import shutil
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
CHEF_IMAGES_DIR = BASE_DIR / "chefff"
STATIC_IMAGES_DIR = BASE_DIR / "my_restaurant" / "Static" / "images"

# Ensure the static images directory exists
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

def update_chef_images():
    """
    Update chef images in the static folder with images from the chefff folder
    and update the references in about.html
    """
    # Check if chef images exist in the chefff folder
    chef_images = list(CHEF_IMAGES_DIR.glob("*.jpeg"))
    
    if not chef_images:
        print("No chef images found in the chefff folder.")
        return
    
    # Define the mapping of chef names to positions and their current images
    chef_data = {
        "John Doe": {
            "position": "Executive Chef",
            "old_image": "client1.jpg"
        },
        "Jane Smith": {
            "position": "Pastry Chef", 
            "old_image": "client2.jpg"
        },
        "Mike Wilson": {
            "position": "Head Sous Chef",
            "old_image": "about-img.png"
        }
    }
    
    # Copy images to static folder and rename them
    for chef_image in chef_images:
        chef_name = chef_image.stem  # Get filename without extension
        
        if chef_name in chef_data:
            # Copy image to static folder with a standardized name
            target_path = STATIC_IMAGES_DIR / f"chef_{chef_name.lower().replace(' ', '_')}.jpeg"
            shutil.copy2(chef_image, target_path)
            print(f"Copied {chef_image} to {target_path}")
    
    # Update the about.html template
    about_html_path = BASE_DIR / "my_restaurant" / "Templates" / "about.html"
    
    if not about_html_path.exists():
        print(f"Template file {about_html_path} not found.")
        return
    
    with open(about_html_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update chef images in the template
    updated_content = content
    
    # Replace each image reference and update names if needed
    for chef_name, data in chef_data.items():
        # Template tags need special handling
        old_image_tag = "{% static 'images/" + data['old_image'] + "' %}"
        new_image_tag = "{% static 'images/chef_" + chef_name.lower().replace(' ', '_') + ".jpeg' %}"
        
        # Replace image references
        updated_content = updated_content.replace(
            f'<img src="{old_image_tag}" alt="Chef" class="img-fluid">',
            f'<img src="{new_image_tag}" alt="{chef_name}" class="img-fluid">'
        )
    
    # Update the file
    with open(about_html_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Updated {about_html_path} with new chef images.")

if __name__ == "__main__":
    update_chef_images()
    print("Chef image update completed.") 