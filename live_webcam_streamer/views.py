import subprocess
import socket
import platform
import os
import cv2
import time

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse

# --- Global State ---
streaming = False
ffmpeg_process = None

# --- Helper Functions ---
def get_local_ip():
    """Get local network IP to display valid RTSP links to the user."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generate_frames():
    """
    Generator function:
    1. Connects to the RTSP stream using OpenCV.
    2. Yields JPEG frames for the browser (MJPEG).
    """
    rtsp_server_ip = os.getenv("RTSP_SERVER_IP", "127.0.0.1")
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    rtsp_url = f"rtsp://{rtsp_server_ip}:{rtsp_port}/live"

    # Wait briefly for FFmpeg to establish the stream
    time.sleep(2)

    cap = cv2.VideoCapture(rtsp_url)

    # Retry logic if stream isn't ready immediately
    if not cap.isOpened():
        time.sleep(1)
        cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("[ERROR] Could not open RTSP stream. Is MediaMTX running?")
        return

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            
            # MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        print("[INFO] Releasing video capture.")
        cap.release()

# --- Page Views ---

def home(request):
    """Renders the main dashboard."""
    return render(request, "index.html")

def record_video_page(request):
    """Renders the recording interface."""
    return render(request, "record_video.html")

def stream_video_page(request):
    """Renders the streaming interface."""
    return render(request, "stream_video.html")

def take_picture_page(request):
    """Renders the photography interface."""
    return render(request, "take_picture.html")

# --- API Endpoints (Streaming Logic) ---

def start_stream(request):
    """Starts the FFmpeg subprocess."""
    global streaming, ffmpeg_process

    if streaming:
        return JsonResponse({"status": "already_running"})

    # Configuration for the external RTSP server (MediaMTX)
    rtsp_server_ip = os.getenv("RTSP_SERVER_IP", "127.0.0.1")
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    internal_rtsp_url = f"rtsp://{rtsp_server_ip}:{rtsp_port}/live"

    local_ip = get_local_ip()
    display_rtsp_url = f"rtsp://{local_ip}:{rtsp_port}/live"

    # Platform detection
    system = platform.system().lower()
    if system == "darwin": # macOS
        camera_input = ["-f", "avfoundation", "-framerate", "30", "-i", "0"]
    elif system == "linux": # Linux
        camera_input = ["-f", "v4l2", "-framerate", "30", "-video_size", "640x480", "-i", "/dev/video0"]
    else:
        return JsonResponse({"status": "error", "message": "Unsupported OS"})

    # FFmpeg command
    ffmpeg_command = [
        "ffmpeg", *camera_input,
        "-vcodec", "libx264", "-tune", "zerolatency", "-preset", "ultrafast",
        "-f", "rtsp", internal_rtsp_url
    ]

    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        streaming = True
        print(f"[INFO] Streaming started at {internal_rtsp_url}")
        return JsonResponse({"status": "started", "rtsp_url": display_rtsp_url})
    except Exception as e:
        print(f"[ERROR] Failed to start stream: {e}")
        return JsonResponse({"status": "error", "message": str(e)})

def stop_stream(request):
    """Stops the FFmpeg subprocess."""
    global streaming, ffmpeg_process
    if ffmpeg_process:
        try:
            ffmpeg_process.terminate()
        except Exception:
            pass
        ffmpeg_process = None
    
    streaming = False
    print("[INFO] Streaming stopped.")
    return JsonResponse({"status": "stopped"})

def status(request):
    """Returns status JSON."""
    local_ip = get_local_ip()
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    display_rtsp_url = f"rtsp://{local_ip}:{rtsp_port}/live"
    return JsonResponse({
        "streaming": streaming,
        "rtsp_url": display_rtsp_url if streaming else None
    })

def video_feed(request):
    """Returns the MJPEG stream response."""
    response = StreamingHttpResponse(generate_frames(),
                                     content_type='multipart/x-mixed-replace; boundary=frame')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response