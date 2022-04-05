from rest_framework import serializers
from home.models import *


class UserSerializers(serializers.ModelSerializer):
    isOriginalUser = serializers.SerializerMethodField('get_is_original')

    class Meta:
        model = Userss
        fields = ['user_id', 'banner_image_url', 'profile_pic_url', 'isOriginalUser', 'channel_name']

    def get_is_original(self, obj):
        try:
            if Userss.objects.get(django_user=self.context['request'].user).user_id == obj.user_id:
                return True
        except:
            return False


class VideoSerializers(serializers.ModelSerializer):
    videos = UserSerializers(read_only=True, source="user_id")

    class Meta:
        model = Videos
        fields = '__all__'


class CommentSerializers(serializers.ModelSerializer):
    user = UserSerializers(read_only=True, source="user_id")
    video = VideoSerializers(read_only=True, source="video_id")
    class Meta:
        model = Comments
        fields = '__all__'


class WatchHistorySerializers(serializers.ModelSerializer):
    videos = VideoSerializers(read_only=True, source="video_id")
    user = UserSerializers(read_only=True, source="user_id")

    class Meta:
        model = WatchHistory
        fields = '__all__'
