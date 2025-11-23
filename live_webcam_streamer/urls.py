"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    # --- UI Pages ---
    path('', views.home, name='home'),
    path('stream/', views.stream_video_page, name='stream_video'),
    path('record/', views.record_video_page, name='record_video'),
    path('capture/', views.take_picture_page, name='take_picture'),

    # --- API Endpoints (Used by JavaScript) ---
    path('api/start/', views.start_stream, name='start_stream'),
    path('api/stop/', views.stop_stream, name='stop_stream'),
    path('api/status/', views.status, name='status'),
    path('api/feed/', views.video_feed, name='video_feed'),
]