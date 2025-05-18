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
    """Add more fast food items to the menu"""
    try:
        # First ensure the Fast Food category exists
        fast_food, created = Category.objects.get_or_create(
            name="Fast Food",
            defaults={"description": "Western style fast food including pizza, burger, and more"}
        )
        if created:
            print(f"Created new category: {fast_food.name}")
        else:
            print(f"Using existing category: {fast_food.name}")
        
        # Define fast food items
        fast_food_items = [
            # Burgers
            {
                "name": "Classic Chicken Burger",
                "description": "Juicy chicken patty with fresh lettuce, tomato, and our special mayo sauce",
                "price": Decimal("149.00")
            },
            {
                "name": "Double Cheese Burger",
                "description": "Two beef patties with double cheese, pickles, onions, and our signature burger sauce",
                "price": Decimal("199.00")
            },
            {
                "name": "Veggie Supreme Burger",
                "description": "Spiced vegetable patty with fresh salad, cheese, and tangy sauce",
                "price": Decimal("159.00")
            },
            {
                "name": "Aloo Tikki Burger",
                "description": "Potato patty with Indian spices, fresh veggies, and mint chutney",
                "price": Decimal("129.00")
            },
            
            # Pizzas
            {
                "name": "Tandoori Paneer Pizza",
                "description": "Tandoori spiced paneer cubes with capsicum, onion, and cheese on a crispy base",
                "price": Decimal("249.00")
            },
            {
                "name": "Deluxe Veggie Pizza",
                "description": "Loaded with mushrooms, olives, bell peppers, onions, corn, and extra cheese",
                "price": Decimal("239.00")
            },
            {
                "name": "Chicken Supreme Pizza",
                "description": "BBQ chicken, grilled chicken, and chicken salami with bell peppers and onions",
                "price": Decimal("279.00")
            },
            {
                "name": "Cheese Overloaded Pizza",
                "description": "Four cheese pizza with mozzarella, cheddar, parmesan, and cream cheese",
                "price": Decimal("259.00")
            },
            
            # Sandwiches
            {
                "name": "Club Sandwich",
                "description": "Triple-decker sandwich with chicken, egg, cheese, and veggies",
                "price": Decimal("159.00")
            },
            {
                "name": "Grilled Cheese Sandwich",
                "description": "Classic grilled sandwich with melted cheese and butter",
                "price": Decimal("119.00")
            },
            
            # Sides
            {
                "name": "Cheese Garlic Bread",
                "description": "Buttery garlic bread topped with melted cheese",
                "price": Decimal("109.00")
            },
            {
                "name": "Loaded Nachos",
                "description": "Crispy nachos with cheese sauce, salsa, guacamole, and sour cream",
                "price": Decimal("169.00")
            },
            {
                "name": "Chicken Wings",
                "description": "Spicy chicken wings served with blue cheese dip",
                "price": Decimal("189.00")
            },
            {
                "name": "Onion Rings",
                "description": "Crispy battered onion rings served with mayo dip",
                "price": Decimal("99.00")
            },
            
            # Wraps
            {
                "name": "Veg Wrap",
                "description": "Grilled vegetables with cheese and sauce wrapped in a soft tortilla",
                "price": Decimal("149.00")
            },
            {
                "name": "Chicken Tikka Wrap",
                "description": "Spicy chicken tikka with onions and mint chutney in a tortilla wrap",
                "price": Decimal("169.00")
            }
        ]
        
        # Add items to database
        with transaction.atomic():
            items_added = 0
            for item_data in fast_food_items:
                # Check if item already exists
                if not MenuItem.objects.filter(name=item_data["name"], category=fast_food).exists():
                    MenuItem.objects.create(
                        name=item_data["name"],
                        description=item_data["description"],
                        price=item_data["price"],
                        category=fast_food,
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