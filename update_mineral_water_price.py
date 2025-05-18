import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import MenuItem

def main():
    """Update price of Mineral Water if it's less than 40"""
    try:
        # Find the Mineral Water menu item
        try:
            mineral_water = MenuItem.objects.get(name="Mineral Water", category__name="Drinks")
            
            print(f"Found Mineral Water with current price: ₹{mineral_water.price}")
            
            if mineral_water.price < 40:
                old_price = mineral_water.price
                # Update to a more appropriate price
                mineral_water.price = 50.00
                mineral_water.save()
                print(f"Updated Mineral Water price from ₹{old_price} to ₹{mineral_water.price}")
            else:
                print("Mineral Water price is already appropriate (≥₹40)")
                
        except MenuItem.DoesNotExist:
            print("Mineral Water item not found in the menu")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 