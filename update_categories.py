import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import Category, MenuItem
from django.db import transaction

def main():
    """Update the restaurant menu categories to have two main categories:
    1. Traditional Food (Sabji, Roti, etc.)
    2. Fast Food (Pizza, Burger, etc.)
    """
    try:
        with transaction.atomic():
            # Clear existing categories
            print("Checking existing categories...")
            existing_categories = Category.objects.all()
            print(f"Found {existing_categories.count()} existing categories.")
            
            # Create new main categories if they don't exist
            trad_food, created = Category.objects.get_or_create(
                name="Traditional Food",
                defaults={"description": "Authentic Indian dishes including sabji, roti, dal, and more"}
            )
            if created:
                print(f"Created new category: {trad_food.name}")
            else:
                print(f"Using existing category: {trad_food.name}")
                
            fast_food, created = Category.objects.get_or_create(
                name="Fast Food",
                defaults={"description": "Western style fast food including pizza, burger, and more"}
            )
            if created:
                print(f"Created new category: {fast_food.name}")
            else:
                print(f"Using existing category: {fast_food.name}")
            
            # Map old categories to new ones
            category_mapping = {
                "Burger": fast_food,
                "Pizza": fast_food,
                "Pasta": fast_food,
                "Fries": fast_food,
                "Drinks": None,  # Keep as is
                "Desserts": None  # Keep as is
            }
            
            # Update menu items to use the new categories
            updated_items = 0
            for old_cat_name, new_cat in category_mapping.items():
                if new_cat:
                    try:
                        old_cat = Category.objects.get(name=old_cat_name)
                        items = MenuItem.objects.filter(category=old_cat)
                        count = items.count()
                        
                        if count > 0:
                            items.update(category=new_cat)
                            updated_items += count
                            print(f"Moved {count} items from '{old_cat_name}' to '{new_cat.name}'")
                            
                            # Delete the old category if no longer needed
                            if not MenuItem.objects.filter(category=old_cat).exists():
                                old_cat.delete()
                                print(f"Deleted empty category: {old_cat_name}")
                    except Category.DoesNotExist:
                        print(f"Category '{old_cat_name}' not found, skipping")
            
            # List any categories that still have menu items
            print("\nRemaining categories with items:")
            for cat in Category.objects.all():
                item_count = MenuItem.objects.filter(category=cat).count()
                print(f"- {cat.name}: {item_count} items")
                
            print(f"\nTotal items updated: {updated_items}")
            print("Category update completed!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 