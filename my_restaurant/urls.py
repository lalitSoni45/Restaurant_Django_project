"""
URL configuration for my_restaurant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from base_app.views import *


urlpatterns = [
    path('admin/dashboard/', admin_dashboard, name='Admin_Dashboard'),
    path('admin/', admin.site.urls),
    path('', home, name='Home'),
    path('menu/', menu, name='Menu'),
    path('about/', about, name='About'),
    path('booktable/',booktable, name='Book_Table'),
    path('feedback/',feedback, name='Feedback_Form'),
    
    # Authentication URLs
    path('login/', user_login, name='Login'),
    path('register/', user_register, name='Register'),
    path('logout/', user_logout, name='Logout'),
    
    # Cart URLs
    path('cart/add/<int:item_id>/', add_to_cart, name='Add_To_Cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='Remove_From_Cart'),
    path('cart/clear/', clear_cart, name='Clear_Cart'),
    path('cart/confirm/', confirm_order, name='Confirm_Order'),
    
    # Payment URLs
    path('payment/process/<int:payment_id>/', process_payment, name='Process_Payment'),
    path('payment/callback/', payment_callback, name='Payment_Callback'),
    path('payment/success/', payment_success, name='Payment_Success'),
    path('payment/failed/', payment_failed, name='Payment_Failed'),
]

# Always include static and media URLs, even in production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)