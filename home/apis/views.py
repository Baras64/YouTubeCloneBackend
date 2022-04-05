from rest_framework.generics import ListAPIView, RetrieveAPIView
from home.models import Test, Userss, Videos
from .serializers import TestSerializer, UserssSerializer, VideosSerializer
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
import ffmpeg_streaming, random, json
from ffmpeg_streaming import Formats, Bitrate, Representation, Size, S3, CloudManager
from django.core.files.storage import FileSystemStorage
from YoutubeClone import settings
from rest_framework.decorators import api_view, renderer_classes

class TestView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        posts = Test.objects.all()
        serializer = TestSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        print("NIGGA NIGGA IS ", request.data)
        posts_serializer = TestSerializer(data=request.data)

        # fs = FileSystemStorage()
        # file = fs.save('nikal.mp4', request.data['image'])

        # video = ffmpeg_streaming.input('media/NMEvsBREZ.webm')
        #
        # dash = video.dash(Formats.h264())
        # dash.auto_generate_representations()
        # #
        # # s3 = S3(aws_access_key_id='<KEY_ID>', aws_secret_access_key='<ACCESS_KEY>', region_name='ap-south-1')
        # # save_to_s3 = CloudManager().add(s3, bucket_name="youtubeclonestorage")
        # # dash.output(clouds=save_to_s3)
        #
        # dash.output('media/NMEvsBREZ.webm')
        #
        # # fs.delete('media/nikal.mp4')

        if posts_serializer.is_valid():
            # posts_serializer.save()
            return Response(posts_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', posts_serializer.errors)
            return Response(posts_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestListView(ListAPIView):
    queryset = Videos.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = VideosSerializer
    def get_queryset(self):
        return self.request.user.django_user.all()

    def perform_create(self, serializer):
        serializer.save(django_user=self.request.user)


class TestDetailView(RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class UserssListView(ListAPIView):
    queryset = Userss.objects.all()
    serializer_class = UserssSerializer


class UserssDetailView(RetrieveAPIView):
    queryset = Userss.objects.all()
    serializer_class = UserssSerializer


class VideosListView(ListAPIView):
    queryset = Videos.objects.all()
    serializer_class = VideosSerializer


class VideoDetailView(RetrieveAPIView):
    queryset = Videos.objects.all()
    serializer_class = VideosSerializer


@api_view(['GET'])
def serveMpd(request, fileName):
    print(fileName)
    path = request.META['HTTP_HOST']
    path1 = "http://" + path + settings.MEDIA_URL
    url = path1 + 'dash.mpd'
    dd = {'file': url}
    return Response(dd)


@api_view(['POST'])
def postVideo(request):

    filename = request.data['image'].name
    print(request.data)

    videoID = generateB64Id()

    data = {
        'link': f'http://127.0.0.1:8000/v/{videoID}',
        'filename': f'{filename}'
    }

    return Response(data)


def generateB64Id():
    charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

    res = ''
    for i in range(11):
        res += charset[random.randint(0, 63)]

    return res