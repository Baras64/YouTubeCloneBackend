from django.shortcuts import render

# Create your views here.
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .models import *
import random

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def generateB64Id(self):
        charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

        res = ''
        for i in range(11):
            res += charset[random.randint(0, 63)]

        return res

    def process_login(self):
        print(self.user)

        new_user = Userss.objects.filter(django_user=self.user).exists()
        if not new_user:
            user_id = self.generateB64Id()
            new_user = Userss(user_id=user_id, email_id=self.user.email, django_user=self.user)
            new_user.save()


        return super().process_login()


