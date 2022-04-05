from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from home.models import Userss, User
from home.serializers import UserSerializers as AppUserSerializer
import random


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def generateB64Id(self):
        charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

        res = ''
        for i in range(20):
            res += charset[random.randint(0, 63)]

        return res

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_id = self.generateB64Id()
        new_user = Userss(user_id=user_id, email_id=user.email, django_user=user)
        new_user.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        temp_user = UserSerializer(user, context=self.get_serializer_context()).data
        print(temp_user)
        django_user = User.objects.get(id=temp_user['id'])
        print(type(django_user))
        app_user = Userss.objects.get(django_user=django_user.id)
        serializer = AppUserSerializer(app_user, context={'request': request})
        serializer = serializer.data

        serializer.update(temp_user)

        return Response({
            "user": serializer,
            "token": AuthToken.objects.create(user)[1]
        })


# Get User API
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    # serializer_class = UserSerializer

    serializer_class = AppUserSerializer

    # def get_object(self):
    #     return self.request.user

    def get_object(self):
        app_user = Userss.objects.get(django_user=self.request.user)
        return app_user
