from rest_framework import routers
from .api import *
from django.urls import path, include
from .views import GoogleLogin
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register('api/videos', VideoViewSet, 'videos')
router.register('api/dashboard', VideoDashBoardViewSet, 'dashboard')
router.register('api/delete_videos', DeleteVideo, 'delete_videos')
router.register('api/comments', CommentViewSet, 'comments')
router.register('api/watch_history', WatchHistoryViewset, 'watch_history')
router.register('api/user', UsersViewSet, 'users')

urlpatterns = [
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('rest-auth/google/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/search', SearchViewSet.as_view(), name='search'),
    path('api/comment-dashboard', CommentDashboardViewSet.as_view(), name='comment-dashboard')
]

urlpatterns += router.urls