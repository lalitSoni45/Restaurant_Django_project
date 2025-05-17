import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import Category, MenuItem

def create_sample_data():
    # Create categories if they don't exist
    categories = {
        'Burger': 'Delicious burgers made with premium ingredients',
        'Pizza': 'Fresh pizzas with a variety of toppings',
        'Pasta': 'Authentic Italian pasta dishes',
        'Fries': 'Crispy and golden french fries',
        'Drinks': 'Refreshing beverages',
        'Desserts': 'Sweet treats to finish your meal'
    }
    
    for name, description in categories.items():
        Category.objects.get_or_create(name=name, description=description)
        print(f"Category '{name}' created or already exists.")
    
    # Create menu items
    menu_items = [
        {
            'name': 'Classic Burger',
            'description': 'Juicy beef patty with lettuce, tomato, onion, and our special sauce on a toasted bun',
            'price': 12.99,
            'category_name': 'Burger',
            'is_featured': True
        },
        {
            'name': 'Cheese Burger',
            'description': 'Classic burger topped with melted cheddar cheese',
            'price': 14.99,
            'category_name': 'Burger',
            'is_featured': True
        },
        {
            'name': 'Margherita Pizza',
            'description': 'Traditional pizza with tomato sauce, mozzarella cheese, and fresh basil',
            'price': 16.99,
            'category_name': 'Pizza',
            'is_featured': True
        },
        {
            'name': 'Pepperoni Pizza',
            'description': 'Classic pizza topped with pepperoni slices',
            'price': 18.99,
            'category_name': 'Pizza',
            'is_featured': True
        },
        {
            'name': 'Spaghetti Bolognese',
            'description': 'Spaghetti pasta with rich meat sauce',
            'price': 15.99,
            'category_name': 'Pasta',
            'is_featured': True
        },
        {
            'name': 'Fettuccine Alfredo',
            'description': 'Fettuccine pasta in creamy Alfredo sauce',
            'price': 14.99,
            'category_name': 'Pasta',
            'is_featured': False
        },
        {
            'name': 'French Fries',
            'description': 'Crispy golden fries seasoned with salt',
            'price': 5.99,
            'category_name': 'Fries',
            'is_featured': True
        },
        {
            'name': 'Loaded Fries',
            'description': 'French fries topped with cheese, bacon bits, and sour cream',
            'price': 8.99,
            'category_name': 'Fries',
            'is_featured': False
        }
    ]
    
    for item in menu_items:
        category = Category.objects.get(name=item['category_name'])
        
        # Check if the item already exists
        if not MenuItem.objects.filter(name=item['name'], category=category).exists():
            MenuItem.objects.create(
                name=item['name'],
                description=item['description'],
                price=item['price'],
                category=category,
                is_featured=item['is_featured'],
                is_available=True
            )
            print(f"Menu item '{item['name']}' created.")
        else:
            print(f"Menu item '{item['name']}' already exists.")

if __name__ == "__main__":
    create_sample_data() 