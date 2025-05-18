import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import MenuItem, Category
from django.utils.text import slugify

def main():
    """Add drink items to the menu"""
    try:
        # Find the Drinks category or create it if it doesn't exist
        drinks_category, created = Category.objects.get_or_create(
            name="Drinks",
            defaults={
                "description": "Refreshing beverages to complement your meal",

            }
        )

        if created:
            print("Created new category: Drinks")
        else:
            print("Using existing category: Drinks")

        # Define drink items
        drinks = [
            {
                "name": "Mango Lassi",
                "description": "Refreshing yogurt-based drink with sweet mango pulp, cardamom, and a hint of saffron",
                "price": 80.00,
            },
            {
                "name": "Sweet Lassi",
                "description": "Traditional yogurt-based drink with a sweet touch and topped with dry fruits",
                "price": 70.00,
            },
            {
                "name": "Salted Lassi",
                "description": "Traditional yogurt-based drink with a savory touch, cumin, and mint",
                "price": 70.00,
            },
            {
                "name": "Fresh Lime Soda",
                "description": "Refreshing drink made with fresh lime juice, soda water, and a choice of sweet or salted",
                "price": 60.00,
            },
            {
                "name": "Masala Chai",
                "description": "Traditional Indian spiced tea with ginger, cardamom, cinnamon, and cloves",
                "price": 50.00,
            },
            {
                "name": "Cold Coffee",
                "description": "Refreshing blend of coffee, milk, and ice cream, topped with chocolate sauce",
                "price": 90.00,
            },
            {
                "name": "Strawberry Milkshake",
                "description": "Creamy milkshake made with fresh strawberries, milk, and vanilla ice cream",
                "price": 100.00,
            },
            {
                "name": "Mango Milkshake",
                "description": "Creamy milkshake made with fresh mangoes, milk, and vanilla ice cream",
                "price": 100.00,
            },
            {
                "name": "Chocolate Milkshake",
                "description": "Rich and creamy milkshake made with chocolate ice cream and milk",
                "price": 100.00,
            },
            {
                "name": "Fresh Fruit Juice",
                "description": "Choice of seasonal fresh fruit juices - orange, pineapple, watermelon, or mixed",
                "price": 80.00,
            },
            {
                "name": "Iced Tea",
                "description": "Refreshing tea served cold with lemon and mint",
                "price": 70.00,
            },
            {
                "name": "Virgin Mojito",
                "description": "Refreshing blend of lime juice, mint leaves, sugar, and soda",
                "price": 90.00,
            },
            {
                "name": "Blue Lagoon",
                "description": "A refreshing mocktail with blue curacao syrup, lemonade, and soda",
                "price": 110.00,
            },
            {
                "name": "Mineral Water",
                "description": "Bottle of pure mineral water",
                "price": 40.00,
            },
            {
                "name": "Soft Drinks",
                "description": "Choice of popular soft drinks - Cola, Lemon, Orange, or Soda",
                "price": 50.00,
            }
        ]

        # Add each drink to the database
        items_added = 0
        for drink in drinks:
            # Check if drink already exists
            if not MenuItem.objects.filter(name=drink["name"], category=drinks_category).exists():
                MenuItem.objects.create(
                    name=drink["name"],
                    description=drink["description"],
                    price=drink["price"],
                    category=drinks_category,

                )
                print(f"Added new item: {drink['name']}")
                items_added += 1
            else:
                print(f"Item '{drink['name']}' already exists, skipping")

        print(f"Total new items added: {items_added}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 