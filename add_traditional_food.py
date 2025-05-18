import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import Category, MenuItem
from django.db import transaction
from decimal import Decimal

def main():
    """Add traditional Indian food items to the menu"""
    try:
        # First ensure the Traditional Food category exists
        trad_food, created = Category.objects.get_or_create(
            name="Traditional Food",
            defaults={"description": "Authentic Indian dishes including sabji, roti, dal, and more"}
        )
        if created:
            print(f"Created new category: {trad_food.name}")
        else:
            print(f"Using existing category: {trad_food.name}")
        
        # Define traditional food items
        traditional_items = [
            {
                "name": "Dal Tadka",
                "description": "Yellow lentils tempered with cumin, garlic, and spices",
                "price": Decimal("120.00")
            },
            {
                "name": "Paneer Butter Masala",
                "description": "Cottage cheese cubes in rich tomato and butter gravy",
                "price": Decimal("180.00")
            },
            {
                "name": "Mix Veg Sabji",
                "description": "Assorted vegetables cooked with Indian spices",
                "price": Decimal("150.00")
            },
            {
                "name": "Chana Masala",
                "description": "Chickpeas cooked in a spicy and tangy tomato-based sauce",
                "price": Decimal("140.00")
            },
            {
                "name": "Aloo Gobi",
                "description": "Potatoes and cauliflower cooked with Indian spices",
                "price": Decimal("130.00")
            },
            {
                "name": "Butter Roti",
                "description": "Traditional Indian bread with a touch of butter",
                "price": Decimal("25.00")
            },
            {
                "name": "Plain Roti",
                "description": "Traditional whole wheat Indian bread",
                "price": Decimal("20.00")
            },
            {
                "name": "Butter Naan",
                "description": "Soft leavened bread with butter topping",
                "price": Decimal("40.00")
            },
            {
                "name": "Garlic Naan",
                "description": "Soft leavened bread with garlic flavoring",
                "price": Decimal("50.00")
            },
            {
                "name": "Jeera Rice",
                "description": "Basmati rice cooked with cumin seeds",
                "price": Decimal("100.00")
            },
        ]
        
        # Add items to database
        with transaction.atomic():
            items_added = 0
            for item_data in traditional_items:
                # Check if item already exists
                if not MenuItem.objects.filter(name=item_data["name"], category=trad_food).exists():
                    MenuItem.objects.create(
                        name=item_data["name"],
                        description=item_data["description"],
                        price=item_data["price"],
                        category=trad_food,
                        is_available=True
                    )
                    items_added += 1
                    print(f"Added new item: {item_data['name']}")
                else:
                    print(f"Item already exists: {item_data['name']}")
            
            print(f"\nTotal new items added: {items_added}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 