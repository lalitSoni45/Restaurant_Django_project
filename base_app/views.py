from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Category, MenuItem, Feedback, TableBooking, Contact, CartItem, Order, Payment
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from .forms import FeedbackForm, TableBookingForm
from django.utils import timezone
from django.urls import reverse
import json
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models

# Mock Razorpay client to avoid authentication errors
class MockRazorpayClient:
    """नकली Razorpay क्लाइंट जो API कीज़ के आधार पर ऑथेंटिकेशन की जरूरत नहीं है"""
    class Order:
        def create(self, data):
            # ऑर्डर आईडी बनाएँ - Make sure this is consistent with the order_id pattern
            order_id = f'order_mock_{random.randint(10000, 99999)}_{int(data["amount"])//100}'
            return {'id': order_id}
    
    class Utility:
        def verify_payment_signature(self, params_dict):
            # सभी मॉक भुगतान हमेशा सफल होंगे
            print(f"Mock verification for: {params_dict}")
            return True
        
        def verify_webhook_signature(self, *args, **kwargs):
            # Mock verification always succeeds
            return True
    
    def __init__(self, **kwargs):
        self.order = self.Order()
        self.utility = self.Utility()
        print("MockRazorpayClient initialized")

# Use real or mock client based on settings
USE_REAL_RAZORPAY = False  # ऑथेंटिकेशन समस्या को बायपास करने के लिए फॉल्स रखें
if USE_REAL_RAZORPAY:
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
else:
    razorpay_client = MockRazorpayClient()

# Create your views here.
def home(request):
    # Get featured menu items for the home page
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)[:6]
    
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
        'featured_items': featured_items,
        'contact_info': contact_info,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'home.html', context)

def menu(request):
    # Get all categories and menu items
    categories = Category.objects.all().order_by('name')
    
    # Get the category filter if specified
    category_id = request.GET.get('category')
    
    if category_id:
        # If filtering by category, get menu items for that category
        menu_items = MenuItem.objects.filter(
            category_id=category_id, 
            is_available=True
        ).order_by('name')
    else:
        # If showing all items, first get Traditional Food and Fast Food categories
        menu_items = MenuItem.objects.filter(
            is_available=True,
            category__name__in=['Traditional Food', 'Fast Food', 'Drinks', 'Desserts']
        ).select_related('category').order_by('category__name', 'name')
    
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

def booktable(request):
    # Get contact information
    contact_info = Contact.objects.first()
    
    # Get categories and menu items for food ordering
    categories = Category.objects.all()
    menu_items = MenuItem.objects.filter(is_available=True)
    
    # Initialize form
    form = TableBookingForm()
    
    if request.method == 'POST':
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Redirect to login page with next parameter
            return redirect('Login' + '?next=' + request.path)
        
        # Process form for authenticated user
        form = TableBookingForm(request.POST)
        if form.is_valid():
            table_booking = form.save(commit=False)
            table_booking.save()
            
            # Create a booking fee (for example, 10% of Rs 500)
            booking_fee = Decimal('50.00')
            total_amount = booking_fee
            
            # Initialize order to None
            order = None
            
            # Check if the user wants to pre-order food
            if 'pre_order_food' in request.POST:
                food_items = []
                food_total = Decimal('0.00')
                
                # Process all the food items
                for key, value in request.POST.items():
                    if key.startswith('item_') and int(value) > 0:
                        item_id = key.replace('item_', '')
                        quantity = int(value)
                        
                        try:
                            menu_item = MenuItem.objects.get(id=item_id)
                            item_total = menu_item.price * quantity
                            food_total += item_total
                            
                            food_items.append({
                                'menu_item': menu_item,
                                'quantity': quantity,
                                'total': item_total,
                            })
                        except MenuItem.DoesNotExist:
                            pass
                
                # If there are food items selected, create an order
                if food_items:
                    # Create the order
                    order = Order.objects.create(
                        user=request.user,
                        total_price=food_total,
                        for_table_booking=True
                    )
                    
                    # Add items to the order
                    for item in food_items:
                        cart_item, created = CartItem.objects.get_or_create(
                            user=request.user,
                            menu_item=item['menu_item'],
                            defaults={'quantity': item['quantity']}
                        )
                        
                        if not created:
                            cart_item.quantity = item['quantity']
                            cart_item.save()
                            
                        order.items.add(cart_item)
                    
                    # Add food total to total amount
                    total_amount += food_total
            
            # Create a Payment object
            payment = Payment.objects.create(
                user=request.user,
                table_booking=table_booking,
                order=order,
                amount=total_amount,
                payment_status='pending'
            )
            
            # Redirect to the payment page
            return redirect('Process_Payment', payment_id=payment.id)
    
    context = {
        'form': form,
        'contact_info': contact_info,
        'user_authenticated': request.user.is_authenticated,
        'categories': categories,
        'menu_items': menu_items,
    }
    return render(request, 'book_table.html', context)

def feedback(request):
    # Get contact information
    contact_info = Contact.objects.first()
    
    # Initialize form
    form = FeedbackForm()
    
    if request.method == 'POST':
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Redirect to login page with next parameter
            return redirect('Login' + '?next=' + request.path)
        
        # Process form for authenticated user
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'धन्यवाद! आपके फीडबैक के लिए!')
            return redirect('Feedback_Form')
    
    context = {
        'form': form,
        'contact_info': contact_info,
        'user_authenticated': request.user.is_authenticated,
    }
    return render(request, 'feedback.html', context)

# User Authentication Views
def user_login(request):
    if request.method == 'POST':
        # Check if login input is email, phone, or username
        login_id = request.POST.get('login_id')
        password = request.POST.get('password')
        
        # Try to authenticate with username first
        user = authenticate(request, username=login_id, password=password)
        
        # If not found, try with email
        if user is None and '@' in login_id:
            try:
                username = User.objects.get(email=login_id).username
                user = authenticate(request, username=username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            
            # Get the next parameter from the URL if it exists
            next_url = request.GET.get('next', 'Home')
            return redirect(next_url)
        else:
            messages.error(request, 'इनवैलिड लॉगिन क्रेडेंशियल्स।')
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'contact_info': contact_info,
    }
    return render(request, 'login.html', context)

def user_register(request):
    """Handle user registration"""
    # If the user is already authenticated, redirect to profile
    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!")
        return redirect('Home')
    
    # If this is a form submission for registration
    if request.method == 'POST' and 'form_type' in request.POST and request.POST['form_type'] == 'registration':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validations
        if not username:
            messages.error(request, "Username is required.")
            return redirect('Register')
            
        if not email and not phone_number:
            messages.error(request, "Either email or phone number is required.")
            return redirect('Register')
            
        if not password1 or not password2:
            messages.error(request, "Both password fields are required.")
            return redirect('Register')
            
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('Register')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('Register')
            
        # Check if email already exists
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('Register')
        
        # All validation passed, create a new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                is_active=True  # Set user as active immediately - skipping OTP verification
            )
            
            # Create a profile for the user if you have a profile model
            # UserProfile.objects.create(user=user, phone_number=phone_number)
            
            # Log the user in
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            
            # Redirect to homepage
            return redirect('Home')
            
        except Exception as e:
            messages.error(request, f"Registration error: {str(e)}")
            return redirect('Register')
    
    # If this is a GET request, just show the register form
    context = {}
    return render(request, 'register.html', context)

def user_logout(request):
    logout(request)
    return redirect('Home')

# Cart Views - Using Session Storage
def add_to_cart(request, item_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to login page with next parameter to return to menu page
        return redirect('Login' + '?next=' + reverse('Menu'))
    
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
    
    messages.success(request, 'Item added to cart.')
    
    # Check HTTP_REFERER to determine which page to return to
    referer = request.META.get('HTTP_REFERER', '')
    if 'home' in referer.lower():
        return redirect('Home')
    else:
        return redirect('Menu')

def remove_from_cart(request, item_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to login page with next parameter to return to menu page
        return redirect('Login' + '?next=' + reverse('Menu'))
        
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    # Remove item from cart
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
    
    # Check HTTP_REFERER to determine which page to return to
    referer = request.META.get('HTTP_REFERER', '')
    if 'home' in referer.lower():
        return redirect('Home')
    else:
        return redirect('Menu')

def clear_cart(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to login page with next parameter to return to menu page
        return redirect('Login' + '?next=' + reverse('Menu'))
        
    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True
    
    messages.success(request, 'Cart cleared.')
    
    # Check HTTP_REFERER to determine which page to return to
    referer = request.META.get('HTTP_REFERER', '')
    if 'home' in referer.lower():
        return redirect('Home')
    else:
        return redirect('Menu')

def confirm_order(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Redirect to login page with next parameter to return to menu page
        return redirect('Login' + '?next=' + reverse('Menu'))
        
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
    
    # Create the order
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
        
        # Create a Payment object
        payment = Payment.objects.create(
            user=request.user,
            order=order,
            amount=cart_total,
            payment_status='pending'
        )
        
        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True
        
        # Redirect to payment page
        return redirect('Process_Payment', payment_id=payment.id)
        
    except Exception as e:
        messages.error(request, f'Error processing your order: {str(e)}')
        return redirect('Menu')

@login_required(login_url='Login')
def process_payment(request, payment_id):
    # Get the Payment object
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    try:
        # Create Razorpay order
        amount_in_paise = int(payment.amount * 100)  # रुपए से पैसे में कन्वर्ट (1 रुपया = 100 पैसे)
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'  # Auto-capture
        })
    except Exception as e:
        # Error handling for development (नकली पेमेंट काम नहीं करने पर भी यह हैंडल करेगा)
        print(f"Razorpay error: {str(e)}")
        razorpay_order = {'id': f'local_order_{payment_id}_{int(payment.amount)}'}
    
    # Update Payment object with razorpay order ID
    payment.razorpay_order_id = razorpay_order['id']
    payment.save()
    
    # Determine payment type based on what's present
    payment_type = "Combined" if payment.table_booking and payment.order else (
        "Table Booking" if payment.table_booking else "Food Order"
    )
    
    context = {
        'payment': payment,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'callback_url': request.build_absolute_uri('/payment/callback/'),
        'amount': payment.amount,
        'currency': 'INR',
        'contact_info': contact_info,
        'payment_type': payment_type,
    }
    
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_callback(request):
    """Payment callback handler for both real and mock payments"""
    print(f"Payment callback called with method: {request.method}")
    print(f"POST data: {request.POST}")
    
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', 'mock_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', 'mock_signature')
        
        print(f"Payment callback processing order: {razorpay_order_id}")
        
        # For mock payments (order_ids starting with 'local_' or 'order_mock_')
        is_mock_payment = razorpay_order_id.startswith('local_order_') or razorpay_order_id.startswith('order_mock_')
        
        if is_mock_payment:
            print("Processing mock payment")
            try:
                # Extract payment ID from the mock order ID
                if razorpay_order_id.startswith('local_order_'):
                    parts = razorpay_order_id.split('_')
                    if len(parts) >= 3:
                        payment_id = int(parts[2])
                        payment = Payment.objects.get(id=payment_id)
                    else:
                        raise Payment.DoesNotExist("Invalid mock order ID format")
                elif razorpay_order_id.startswith('order_mock_'):
                    # Try to find by razorpay_order_id
                    payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                else:
                    raise Payment.DoesNotExist("Unrecognized mock order ID format")
                
                # Update payment
                payment.payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.payment_status = 'completed'
                payment.save()
                
                # Update related order and/or table booking
                if payment.order:
                    payment.order.payment_complete = True
                    payment.order.save()
                if payment.table_booking:
                    payment.table_booking.payment_complete = True
                    payment.table_booking.save()
                
                # Redirect to success page
                print("Mock payment successful")
                return redirect('Payment_Success')
                
            except Payment.DoesNotExist as e:
                print(f"Payment not found: {str(e)}")
                return redirect('Payment_Failed')
            except Exception as e:
                print(f"Error processing mock payment: {str(e)}")
                return redirect('Payment_Failed')
        else:
            # For real Razorpay payments
            print("Processing real Razorpay payment")
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                # Verify signature
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                # Find the payment
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.payment_status = 'completed'
                payment.save()
                
                # Update related order and/or table booking
                if payment.order:
                    payment.order.payment_complete = True
                    payment.order.save()
                if payment.table_booking:
                    payment.table_booking.payment_complete = True
                    payment.table_booking.save()
                
                # Redirect to success page
                return redirect('Payment_Success')
                
            except (razorpay.errors.SignatureVerificationError, Exception) as e:
                print(f"Payment verification error: {str(e)}")
                return redirect('Payment_Failed')
            except Payment.DoesNotExist:
                print("Payment not found")
                return redirect('Payment_Failed')
    
    # Handle GET requests
    print("Payment callback received GET request instead of POST")
    return redirect('Home')

@login_required(login_url='Login')
def payment_success(request):
    # Get the most recent completed payment for user
    try:
        # Try to get the latest completed payment
        payment = Payment.objects.filter(
            user=request.user, 
            payment_status='completed'
        ).order_by('-id').first()
    except Payment.DoesNotExist:
        payment = None
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'contact_info': contact_info,
        'payment': payment,
        'current_time': timezone.now(),
        'transaction_id': payment.payment_id if payment else 'N/A',
    }
    return render(request, 'payment_success.html', context)

@login_required(login_url='Login')
def payment_failed(request):
    # Get the most recent failed payment for user
    try:
        # Try to get the latest pending or failed payment
        payment = Payment.objects.filter(
            user=request.user
        ).exclude(payment_status='completed').order_by('-id').first()
    except Payment.DoesNotExist:
        payment = None
    
    # Get contact information
    contact_info = Contact.objects.first()
    
    context = {
        'contact_info': contact_info,
        'payment': payment,
        'error_code': request.GET.get('error_code', 'unknown'),
        'support_phone': contact_info.phone if contact_info else '+91 98765 43210',
        'support_email': contact_info.email if contact_info else 'support@example.com',
    }
    return render(request, 'payment_failed.html', context)

# Removed OTP functionality

# Add new admin dashboard view
@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard view that mimics the modern dashboard"""
    # Get some basic stats for the dashboard
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(models.Sum('amount'))['amount__sum'] or 0
    total_orders = Order.objects.count()
    total_customers = User.objects.count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Get trending menu items
    trending_menu_items = MenuItem.objects.all()[:3]
    
    # Get recent payments
    recent_payments = Payment.objects.order_by('-created_at')[:8]
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'cancelled_orders': cancelled_orders,
        'trending_menu_items': trending_menu_items,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'admin/dashboard.html', context)