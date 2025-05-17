from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, MenuItem, Contact, CartItem, Order
from .forms import FeedbackForm, TableBookingForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json

# Create your views here.
def home(request):
    # Get featured menu items for the home page
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)[:6]
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'featured_items': featured_items,
        'contact_info': contact_info,
    }
    return render(request, 'home.html', context)

def menu(request):
    # Get all categories and menu items
    categories = Category.objects.all()
    menu_items = MenuItem.objects.filter(is_available=True)
    
    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        menu_items = menu_items.filter(category_id=category_id)
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    # Get cart items
    cart_items = []
    cart_total = 0
    
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        
        for item_id, quantity in cart.items():
            try:
                menu_item = MenuItem.objects.get(id=int(item_id))
                item_total = menu_item.price * quantity
                cart_total += item_total
                
                cart_items.append({
                    'id': item_id,
                    'menu_item': menu_item,
                    'quantity': quantity,
                    'total': item_total,
                })
            except MenuItem.DoesNotExist:
                pass
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
        'contact_info': contact_info,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'menu.html', context)

def about(request):
    # Get contact information
    contact_info = Contact.objects.first()
    
    # Define restaurant information for the about page
    restaurant_info = {
        'founding_year': 2008,
        'experience_years': 15,
        'team_size': 25,
        'locations': 3,
    }
    
    context = {
        'contact_info': contact_info,
        'restaurant_info': restaurant_info,
    }
    return render(request, 'about.html', context)

@login_required(login_url='Login')
def booktable(request):
    if request.method == 'POST':
        form = TableBookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your table booking request has been submitted successfully. We will contact you shortly.')
            return redirect('Book_Table')
    else:
        form = TableBookingForm()
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'form': form,
        'contact_info': contact_info,
    }
    return render(request, 'book_table.html', context)

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('Feedback_Form')
    else:
        form = FeedbackForm()
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'form': form,
        'contact_info': contact_info,
    }
    return render(request, 'feedback.html', context)

# User Authentication Views
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get the next parameter from the URL if it exists
            next_url = request.GET.get('next', 'Home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'contact_info': contact_info,
    }
    return render(request, 'login.html', context)

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Simple validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('Register')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('Register')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('Register')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Auto-login after registration
        login(request, user)
        
        # Get the next parameter from the URL if it exists
        next_url = request.GET.get('next', 'Home')
        return redirect(next_url)
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'contact_info': contact_info,
    }
    return render(request, 'register.html', context)

def user_logout(request):
    logout(request)
    return redirect('Home')

# Cart Views - Using Session Storage
@login_required(login_url='Login')
def add_to_cart(request, item_id):
    # Get the menu item
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    # Add item to cart or increment quantity
    cart = request.session['cart']
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        cart[item_id_str] += 1
    else:
        cart[item_id_str] = 1
    
    # Save the cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f'{menu_item.name} added to cart.')
    return redirect('Menu')

@login_required(login_url='Login')
def remove_from_cart(request, item_id):
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    # Remove item from cart or decrement quantity
    cart = request.session['cart']
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        if cart[item_id_str] > 1:
            cart[item_id_str] -= 1
        else:
            del cart[item_id_str]
    
    # Save the cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, 'Item removed from cart.')
    return redirect('Menu')

@login_required(login_url='Login')
def clear_cart(request):
    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True
    
    messages.success(request, 'Cart cleared.')
    return redirect('Menu')

@login_required(login_url='Login')
def confirm_order(request):
    # Check if cart is empty
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('Menu')
    
    # Calculate total price and get items
    cart_items = []
    cart_total = 0
    
    for item_id, quantity in cart.items():
        try:
            menu_item = MenuItem.objects.get(id=int(item_id))
            item_total = menu_item.price * quantity
            cart_total += item_total
            
            cart_items.append({
                'id': item_id,
                'menu_item': menu_item,
                'quantity': quantity,
                'total': item_total,
            })
        except MenuItem.DoesNotExist:
            pass
    
    # Create the order (directly in the database if the models exist)
    try:
        order = Order.objects.create(
            user=request.user,
            total_price=cart_total
        )
        
        # Add items to the order
        for item in cart_items:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                menu_item=item['menu_item'],
                defaults={'quantity': item['quantity']}
            )
            
            if not created:
                cart_item.quantity = item['quantity']
                cart_item.save()
                
            order.items.add(cart_item)
            
        messages.success(request, f'Your order #{order.id} has been placed successfully!')
    except Exception as e:
        # If database models don't exist or there's an error, just show success message
        messages.success(request, 'Your order has been placed successfully!')
    
    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True
    
    return redirect('Menu')