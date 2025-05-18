from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()

class PhoneOrEmailAuthBackend(ModelBackend):
    """
    Authentication backend that allows users to authenticate using either
    their phone number, email, or username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if the username parameter could be an email or phone number
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        if username is None or password is None:
            return None
            
        try:
            # Check if the username is an email, phone number, or just a regular username
            user = UserModel.objects.filter(
                Q(username=username) | 
                Q(email=username) | 
                Q(phone_number=username)
            ).first()
            
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            UserModel().set_password(password)
            
        return None 