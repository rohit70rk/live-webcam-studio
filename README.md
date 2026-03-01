# Webcam Studio 🎥

Webcam Studio is a lightweight, browser-based media suite built with Django and WebRTC. It allows users to capture high-resolution photos, record local videos directly to their device, and host real-time, peer-to-peer video streams with friends without needing any heavy external media servers (like FFmpeg or RTSP).

## ✨ Features

* **Peer-to-Peer Live Streaming (WebRTC):** * Sub-second latency video and audio streaming directly between browsers.
    * Secure, dynamically generated room URLs for private sharing.
    * On-the-fly Camera and Microphone toggles.
    * Powered by Django Channels acting as a high-speed WebSocket signaling server.
* **Local Video Recording:** Record video and audio using your local hardware and save it instantly to your disk as a `.webm` file.
* **Photo Booth:** Snap instant, high-quality `.png` pictures using your webcam.

## 🛠️ Tech Stack

* **Backend:** Python, Django 5.x, Django Channels, Daphne (ASGI)
* **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Custom responsive UI)
* **Real-Time Communication:** WebRTC (RTCPeerConnection, STUN), WebSockets

## 🚀 Local Development Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system. 

### 2. Installation
Clone the repository and navigate into the project directory:
