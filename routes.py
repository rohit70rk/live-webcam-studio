# ======== fspp/projects/live_webcam/routes.py ========
from flask import Blueprint, render_template, jsonify, Response
import subprocess
import socket
import platform
import os
import cv2
import time

live_webcam_bp = Blueprint('live_webcam', __name__,
                           template_folder='templates',
                           static_folder='static')

streaming = False
ffmpeg_process = None


def get_local_ip():
    """Get local network IP."""
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


@live_webcam_bp.route("/details")
def details():
     return render_template("live_webcam/project_detail.html")


@live_webcam_bp.route("/live_webcam")
def webcam_project():
    return render_template("live_webcam/webcam_project.html")


@live_webcam_bp.route("/start_stream")
def start_stream():
    """Start FFmpeg stream to RTSP server (auto detects Mac/Linux)."""
    global streaming, ffmpeg_process

    if streaming:
        return jsonify({"status": "already_running"})

    rtsp_server_ip = os.getenv("RTSP_SERVER_IP", "127.0.0.1")
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    
    # Internal URL for FFmpeg to connect to the RTSP server inside Docker
    internal_rtsp_url = f"rtsp://{rtsp_server_ip}:{rtsp_port}/live"
    
    # --- CHANGE ---
    # External URL for the user to view the stream in an app like VLC
    local_ip = get_local_ip()
    display_rtsp_url = f"rtsp://{local_ip}:{rtsp_port}/live"
    # --- END CHANGE ---

    system = platform.system().lower()
    if system == "darwin":
        camera_input = ["-f", "avfoundation", "-framerate", "30", "-i", "0"]
    elif system == "linux":
        camera_input = ["-f", "v4l2", "-framerate", "30", "-video_size", "640x480", "-i", "/dev/video0"]
    else:
        return jsonify({"status": "error", "message": "Unsupported OS"})

    ffmpeg_command = [
        "ffmpeg", *camera_input,
        "-vcodec", "libx264", "-tune", "zerolatency", "-preset", "ultrafast",
        "-f", "rtsp", internal_rtsp_url
    ]

    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        streaming = True
        print(f"[INFO] Streaming started at {internal_rtsp_url}")
        # --- CHANGE ---
        # Return the user-facing URL to the frontend
        return jsonify({"status": "started", "rtsp_url": display_rtsp_url})
        # --- END CHANGE ---
    except Exception as e:
        print(f"[ERROR] Failed to start stream: {e}")
        return jsonify({"status": "error", "message": str(e)})


@live_webcam_bp.route("/stop_stream")
def stop_stream():
    """Stop FFmpeg stream."""
    global streaming, ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.terminate()
        ffmpeg_process = None
    streaming = False
    print("[INFO] Streaming stopped.")
    return jsonify({"status": "stopped"})


@live_webcam_bp.route("/status")
def status():
    """Return current streaming status."""
    # --- CHANGE ---
    # Return the user-facing URL to the frontend
    local_ip = get_local_ip()
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    display_rtsp_url = f"rtsp://{local_ip}:{rtsp_port}/live"
    return jsonify({
        "streaming": streaming,
        "rtsp_url": display_rtsp_url if streaming else None
    })
    # --- END CHANGE ---


def generate_frames():
    """Connects to the RTSP stream and yields frames as MJPEG."""
    rtsp_server_ip = os.getenv("RTSP_SERVER_IP", "127.0.0.1")
    rtsp_port = os.getenv("RTSP_PORT", "8554")
    rtsp_url = f"rtsp://{rtsp_server_ip}:{rtsp_port}/live"
    
    time.sleep(2)
    
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("[ERROR] Could not open RTSP stream.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("[INFO] Stream ended or failed to grab frame.")
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    print("[INFO] Releasing video capture.")
    cap.release()

@live_webcam_bp.route('/video_feed')
def video_feed():
    """Video streaming route that returns a multipart response."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

