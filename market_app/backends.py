from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


# this authenticate function overrides the default authenticate 
# function to use email instead of username
class EmailBackend(ModelBackend):
    """Authenticate using email and password. Username remains for in-app use only."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
