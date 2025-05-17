import os
import django
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_restaurant.settings')
django.setup()

# Run collectstatic command
print("Collecting static files...")
call_command('collectstatic', interactive=False, verbosity=1)
print("Static files collected successfully!") 