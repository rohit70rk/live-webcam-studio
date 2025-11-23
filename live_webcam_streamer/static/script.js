document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const videoStream = document.getElementById('video-stream');
    const statusMessage = document.getElementById('status-message');
    const streamInfo = document.getElementById('stream-info');
    const rtspUrlElement = document.getElementById('rtsp-url');

    // Updated API endpoints to match live_webcam_streamer/urls.py
    const startUrl = '/api/start/';
    const stopUrl = '/api/stop/';
    const statusUrl = '/api/status/';
    const videoFeedUrl = '/api/feed/';

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            fetch(startUrl)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'started' || data.status === 'already_running') {
                        console.log('Stream started:', data.rtsp_url);
                        updateStatus(true, data.rtsp_url);
                    } else {
                        statusMessage.textContent = 'Error: Could not start stream. Check console.';
                    }
                });
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            fetch(stopUrl)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'stopped') {
                        console.log('Stream stopped.');
                        updateStatus(false, null);
                    }
                });
        });
    }

    function updateStatus(isStreaming, url) {
        if (!videoStream) return;
        
        if (isStreaming) {
            // Add timestamp to prevent browser caching
            videoStream.src = videoFeedUrl + '?' + new Date().getTime();
            videoStream.style.display = 'block';
            if (statusMessage) statusMessage.style.display = 'none';
            if (rtspUrlElement) rtspUrlElement.textContent = url;
            if (streamInfo) streamInfo.style.display = 'block';
        } else {
            videoStream.src = '';
            videoStream.style.display = 'none';
            if (statusMessage) {
                statusMessage.textContent = 'Stream is stopped.';
                statusMessage.style.display = 'block';
            }
            if (streamInfo) streamInfo.style.display = 'none';
        }
    }

    // Check status on page load (only if we are on the streaming page)
    if (videoStream) {
        fetch(statusUrl)
            .then(response => response.json())
            .then(data => {
                updateStatus(data.streaming, data.rtsp_url);
            });
    }
});