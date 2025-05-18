import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import MenuItem

def main():
    """Update prices for menu items that cost less than 40"""
    try:
        # Find all menu items with price less than 40
        low_price_items = MenuItem.objects.filter(price__lt=40)
        
        print(f"Found {low_price_items.count()} items with price less than 40:")
        
        # Define appropriate price ranges based on food type
        fast_food_prices = {
            'burger': 80.00,
            'pizza': 120.00,
            'pasta': 100.00,
            'fries': 60.00,
            'sandwich': 70.00,
            'wrap': 90.00,
            'cheese': 110.00,
            'loaded': 95.00
        }
        
        traditional_food_prices = {
            'roti': 45.00,
            'naan': 65.00,
            'paratha': 75.00
        }
        
        # Update each item's price based on its category and name
        updated_count = 0
        for item in low_price_items:
            old_price = item.price
            category_name = item.category.name
            item_name_lower = item.name.lower()
            
            # Set new price based on category and item name
            if category_name == "Fast Food":
                # Find the matching food type in the fast_food_prices dictionary
                matched_type = None
                for food_type in fast_food_prices:
                    if food_type in item_name_lower:
                        matched_type = food_type
                        break
                        
                if matched_type:
                    item.price = fast_food_prices[matched_type]
                else:
                    # Default price if no specific match
                    item.price = 90.00
                    
            elif category_name == "Traditional Food":
                # Find the matching food type in the traditional_food_prices dictionary
                matched_type = None
                for food_type in traditional_food_prices:
                    if food_type in item_name_lower:
                        matched_type = food_type
                        break
                        
                if matched_type:
                    item.price = traditional_food_prices[matched_type]
                else:
                    # Default price if no specific match
                    item.price = 80.00
            
            # If the price was changed, save it
            if item.price != old_price:
                # Save the updated price
                item.save()
                updated_count += 1
                print(f"Updated {item.name} price from ₹{old_price} to ₹{item.price}")
        
        print(f"\nTotal items updated: {updated_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 