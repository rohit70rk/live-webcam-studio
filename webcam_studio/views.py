import secrets
from django.shortcuts import render, redirect

def home(request):
    return render(request, "index.html")

def record_video_page(request):
    return render(request, "record_video.html")

def take_picture_page(request):
    return render(request, "take_picture.html")

def create_stream_room(request):
    room_id = secrets.token_urlsafe(9) # Generate a unique room ID
    return redirect('stream_video', room_id=room_id)

def stream_video_page(request, room_id):
    return render(request, "stream_video.html", {"room_name": room_id})