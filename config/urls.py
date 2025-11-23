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


from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Fixes 404: Redirects root URL "http://127.0.0.1:8000/" to the app
    path('', RedirectView.as_view(url='live-webcam-streaming/', permanent=False)),

    # 2. Main UI Page
    path('live-webcam-streaming/', views.webcam_project, name='webcam_project'),

    # 3. API Endpoints (Required by script.js to control the stream)
    path('projects/webcam/start_stream', views.start_stream, name='start_stream'),
    path('projects/webcam/stop_stream', views.stop_stream, name='stop_stream'),
    path('projects/webcam/status', views.status, name='status'),
    path('projects/webcam/video_feed', views.video_feed, name='video_feed'),
]