from django.urls import path
from .views import *

urlpatterns = [
    path('', TestListView.as_view()),
    path('<pk>', TestDetailView.as_view()),
    path('user/', UserssListView.as_view()),
    path('user/<pk>', UserssDetailView.as_view()),
    path('posts/', TestView.as_view()),
    path('media/<fileName>', serveMpd),
    path('videos/<pk>', VideoDetailView.as_view()),
    path('videos/', VideosListView.as_view()),
    path('uploadVideo/', postVideo),
]