from django.contrib.auth.backends import BaseBackend
from rating_site.rating.models import CustomUser

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.using('mysql_db').get(login=username)
        except CustomUser.DoesNotExist:
            return None

        if user.password == password:
            return user

        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.using('mysql_db').get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None