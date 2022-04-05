from rest_framework import serializers
from home.models import Test, Userss, Videos


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class UserssSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userss
        fields = ('user_id', 'email_id', 'first_name', 'last_name')


class VideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = '__all__'
