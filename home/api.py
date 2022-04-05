import datetime

from home.models import *
from rest_framework import viewsets, permissions
from .serializers import *
from rest_framework.response import Response
import random, time, asyncio, os
from django.core.files.storage import FileSystemStorage
import ffmpeg_streaming, sys, shutil
from ffmpeg_streaming import Formats, Bitrate, Representation, Size, S3, CloudManager
from rest_framework.decorators import api_view, renderer_classes, action
from django_filters.rest_framework import DjangoFilterBackend
from django.core import serializers
from rest_framework import generics, filters


# Video Viewset
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Videos.objects.all().order_by('-release_date')
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = VideoSerializers

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk is not None:
            obj = Videos.objects.get(video_id=pk)
            if obj is not None:
                obj.views += 1
                obj.save()
                self.add_watch_history(self.request.user, obj)
                db_connect(f"UPDATE WATCH_HISTORY SET VIEWS = VIEWS + 1 WHERE USER_ID={pk}")
        print(self.request.user)

        queryset = Videos.objects.prefetch_related('user_id').order_by('-release_date')
        db_connect("SELECT * FROM VIDEOS NATURAL JOIN USERSS ORDER BY RELEASE_DATE DESC")
        return queryset

    def add_watch_history(self, user, video):
        existing_user = Userss.objects.get(django_user=user)
        db_connect(f"SELECT * FROM USERSS WHERE USER_ID = {user}")
        already_in_watch_history = WatchHistory.objects.filter(user_id=existing_user, video_id=video).exists()
        db_connect(f"SELECT * FROM WATCH_HISTORY WHERE USER_ID = {existing_user} AND VIDEO_ID = {video}")

        if already_in_watch_history:
            old_history = WatchHistory.objects.get(user_id=existing_user, video_id=video)
            old_history.delete()
            db_connect(f"DELETE FROM WATCH_HISTORY WHERE USER_ID = {existing_user} AND VIDEO_ID = {video}")

        db_connect(f"INSERT INTO WATCH_HISTORY (USER_ID, VIDEO_ID) VALUES ({existing_user}, {video})")
        new_history = WatchHistory(user_id=existing_user, video_id=video)
        new_history.save()

    def update(self, request, *args, **kwargs):
        print(request.data, self.kwargs)
        instance = self.get_object()
        instance.title = request.data.get('title')

        if request.data.get('description') is not None:
            instance.description = request.data.get('description')

        if request.data.get('image') is not None:
            fs = FileSystemStorage()
            image_obj = request.data.get('image')
            filename = f"{self.kwargs.get('pk')}_{image_obj.name}"
            if os.path.exists(f'media/{filename}'):
                os.remove(f'media/{filename}')
            file = fs.save(filename, image_obj)
            instance.thumbnail = f'http://127.0.0.1:8000/media/{filename}'

        sql_filename = "fvmewaSB8he_default-profile-picture.jpg"
        db_connect(f"UPDATE VIDEOS SET TITLE = {request.data.get('title')}, DESCRIPTION = {request.data.get('description')}, THUMBNAIL = {sql_filename}")
        instance.save()

        print(request.data.get('title'), instance.title)
        print(instance)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.data.get('video') is not None:
            user_exists = Userss.objects.filter(django_user=self.request.user).exists()
            if user_exists:
                user = Userss.objects.filter(django_user=self.request.user)[0]
                filename = request.data.get('video').name
                video_id = self.generateB64Id()

                filename = f"{video_id}_{filename}"

                fs = FileSystemStorage()
                file = fs.save(filename, request.data.get('video'))
                print("I HAVE ENTERED")

                async def transcode(filename):
                    loop = asyncio.get_event_loop()

                    def transcode_util(filename):
                        video = ffmpeg_streaming.input(f'media/{filename}')
                        dash = video.dash(Formats.h264())
                        dash.auto_generate_representations()
                        dash.output(f'media/{filename.split(".")[0]}/{filename.split(".")[0]}.mpd')

                        fs.delete(filename)

                    future = loop.run_in_executor(None, transcode_util, filename)
                    response = future

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(transcode(filename))

                data = {
                    'link': f'http://127.0.0.1:8000/v/{video_id}',
                    'filename': f'{request.data.get("video").name}'
                }
                new_video = Videos(video_id=video_id, user_id=user, title=filename,
                                   video_url=f'http://127.0.0.1:8000/media/{filename.split(".")[0]}/{filename.split(".")[0]}.mpd')
                # change the user to request.user

                db_connect(f"INSERT INTO VIDEOS (VIDEO_ID, USER_ID, TITLE, VIDEO_URL) VALUES ({video_id}, {user}, {filename}, {filename}) ")
                new_video.save()
                return Response(data)
        else:
            return Response("No video content provided")

    def generateB64Id(self):
        charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

        res = ''
        for i in range(11):
            res += charset[random.randint(0, 63)]

        return res


class DeleteVideo(viewsets.ModelViewSet):
    queryset = Videos.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = VideoSerializers

    def create(self, request, *args, **kwargs):
        if request.data.get('video_ids') is not None:
            ids = request.data.get('video_ids').split(',')
            for id in ids:
                obj = Videos.objects.get(video_id=id)
                video_dir = 'media/' + obj.video_url.split('/')[-2]
                shutil.rmtree(video_dir)
                db_connect(f"DELETE FROM VIDEOS WHERE VIDEO_ID = {id}")
                obj.delete()
        return Response('Videos Successf ully deleted')


class CommentDashboardViewSet(generics.ListCreateAPIView):
    search_fields = ['video_id__comments_set__user_id_id']
    filter_backends = (filters.SearchFilter,)

    queryset = Comments.objects.prefetch_related('user_id').prefetch_related('video_id')

    # queryset = Comments.objects.prefetch_related('video_id__comments_set__user_id_id')
    serializer_class = CommentSerializers

    permission_classes = [
        permissions.AllowAny
    ]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.prefetch_related('user_id').prefetch_related('video_id').order_by('-comment_date')
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = CommentSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['video_id', 'user_id']

    def create(self, request, *args, **kwargs):
        user_exists = Userss.objects.filter(django_user=self.request.user).exists()
        if user_exists:
            user = Userss.objects.filter(django_user=self.request.user)[0]
            comment_content = request.data.get('comment_content')
            video_id = request.data.get('video_id')
            user_id = user
            comment_id = self.generateB64Id()
            new_comment = Comments(video_id=Videos.objects.filter(video_id=video_id)[0],
                                   comment_content=comment_content, user_id=user_id, comment_id=comment_id)
            new_comment.save()
            db_connect(f"INSERT INTO COMMENTS (VIDEO_ID, COMMENT_CONTENT, USER_ID, COMMENT_ID) VALUES ({video_id}, {comment_content}, {user_id}, {comment_id})")
            data = Comments.objects.filter(comment_id=comment_id)[0]
            serializer = self.get_serializer(data)
            return Response(serializer.data)

    def generateB64Id(self):
        charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

        res = ''
        for i in range(20):
            res += charset[random.randint(0, 63)]

        return res


class VideoDashBoardViewSet(viewsets.ModelViewSet):
    # queryset = Videos.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = VideoSerializers

    def get_queryset(self):
        print(self.request.user)
        qs = Videos.objects.all()
        user_exists = Userss.objects.filter(django_user=self.request.user).exists()
        if user_exists:
            user = Userss.objects.filter(django_user=self.request.user)[0]
            db_connect(f"SELECT * FROM USERSS WHERE USER_ID = {self.request.user}")
            return qs.filter(user_id=user).order_by('-release_date')
        return []
        # return self.request.user.django_user.all()

    def perform_create(self, serializer):
        serializer.save(user_id='acdefghijklmnopqrst')

    def perform_update(self, serializer):
        return "Hello"


class WatchHistoryViewset(viewsets.ModelViewSet):
    # queryset = WatchHistory.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = WatchHistorySerializers

    def get_queryset(self):
        user = Userss.objects.get(django_user=self.request.user)
        # JOINS
        # queryset = WatchHistory.objects.prefetch_related('video_id').order_by('-watch_date').filter(user_id_id=user)

        queryset = WatchHistory.objects.prefetch_related('video_id').prefetch_related('user_id').order_by(
            "-watch_date").filter(user_id_id=user)

        db_connect(f"SELECT * FROM WATCH_HISTORY NATURAL JOIN VIDEOS NATURAL JOIN USERSS WHERE USER_ID = {user} ORDER BY WATCH_DATE DESC")

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        db_connect(f"DELETE FROM WATCH_HISTORY WHERE ID = {id}")
        self.perform_destroy(instance)
        return Response(id)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Userss.objects.all()
    serializer_class = UserSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        print(self.kwargs.get('pk'), self.request.user)
        if self.kwargs.get('pk') == None:
            queryset = Userss.objects.filter(django_user=self.request.user)
            db_connect(f"SELECT * FROM USERSS WHERE USER_ID = {self.kwargs.get('pk')}")
            return queryset
        else:
            return super().get_queryset()

    def create(self, request, *args, **kwargs):
        query = Videos.objects.filter(user_id=request.data.get('user_id'))
        serializer = VideoSerializers(query, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if Userss.objects.get(django_user=request.user).user_id == Userss.objects.get(
                user_id=self.kwargs.get('pk')).user_id:
            print(request.data, self.kwargs)
            instance = self.get_object()
            print(instance)
            if request.data.get('channel_name') != '':
                instance.channel_name = request.data.get('channel_name')

            if request.data.get('profile_pic') != 'null':
                fs = FileSystemStorage()
                new_profile_pic = request.data.get('profile_pic')
                filename = f"{self.kwargs.get('pk')}_profile_pic"

                if os.path.exists(f'media/{filename}'):
                    os.remove(f'media/{filename}')

                file = fs.save(filename, new_profile_pic)
                instance.profile_pic_url = f"http://127.0.0.1:8000/media/{filename}"

            if request.data.get('banner_image') != 'null':
                fs = FileSystemStorage()
                new_banner_image = request.data.get('banner_image')
                filename = f"{self.kwargs.get('pk')}_banner_image"
                if os.path.exists(f'/media/{filename}'):
                    print("EXISTS")
                file = fs.save(filename, new_banner_image)
                instance.banner_image_url = f"http://127.0.0.1:8000/media/{filename}"

            sql_filename = "fvmewaSB8he_default-profile-picture.jpg"

            db_connect(f"UPDATE USERSS SET BANNER_IMAGE = {sql_filename}, PROFILE_PIC = {sql_filename}, CHANNEL_NAME = {request.data.get('channel_name')} WHERE USER_ID = {request.user}")

            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


class SearchViewSet(generics.ListCreateAPIView):
    search_fields = ['description', 'title']
    filter_backends = (filters.SearchFilter,)

    queryset = Videos.objects.prefetch_related('user_id')
    serializer_class = VideoSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]


def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()

def db_connect(sql_query):
    print(sql_query)
