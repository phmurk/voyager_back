"""
URL configuration for travel_agency project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tours.views import (
    TourViewSet, DestinationViewSet, BlogPostViewSet, ForumTopicViewSet,
    ForumReplyViewSet, OrderViewSet, ReviewViewSet,  # <-- Добавлен ReviewViewSet
    RegisterView, LoginView, ProfileView,
    FavoritesView, ForumActivityView, NewsletterSubscribeView
)

# DRF Router
router = DefaultRouter()
router.register(r'tours', TourViewSet, basename='tour')
router.register(r'destinations', DestinationViewSet, basename='destination')
router.register(r'blog', BlogPostViewSet, basename='blogpost')
router.register(r'forum-topics', ForumTopicViewSet, basename='forumtopic')
router.register(r'forum-replies', ForumReplyViewSet, basename='forumreply')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/favorites/', FavoritesView.as_view(), name='favorites'),
    path('api/forum-activity/', ForumActivityView.as_view(), name='forum-activity'),
    path('api/newsletter/', NewsletterSubscribeView.as_view(), name='newsletter'),
]