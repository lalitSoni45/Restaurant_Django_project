import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

from base_app.models import Contact

def create_contact():
    # Check if Contact record already exists
    if Contact.objects.exists():
        print("Contact information already exists.")
        return
    
    # Create a new Contact record
    contact = Contact(
        address="123 Main Street, Cityville, State 12345",
        phone="+1 (555) 123-4567",
        email="info@feanerestaurant.com"
    )
    contact.save()
    print("Contact information created successfully!")

if __name__ == "__main__":
    create_contact() 