document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const videoStream = document.getElementById('video-stream');
    const statusMessage = document.getElementById('status-message');
    const streamInfo = document.getElementById('stream-info');
    const rtspUrlElement = document.getElementById('rtsp-url');

    // URLs for the Flask API endpoints
    const startUrl = '/projects/webcam/start_stream';
    const stopUrl = '/projects/webcam/stop_stream';
    const statusUrl = '/projects/webcam/status';
    const videoFeedUrl = '/projects/webcam/video_feed';

    startBtn.addEventListener('click', () => {
        // Call the /start_stream endpoint
        fetch(startUrl)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started' || data.status === 'already_running') {
                    console.log('Stream started:', data.rtsp_url);
                    updateStatus(true, data.rtsp_url);
                } else {
                    statusMessage.textContent = 'Error: Could not start stream.';
                }
            });
    });

    stopBtn.addEventListener('click', () => {
        // Call the /stop_stream endpoint
        fetch(stopUrl)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'stopped') {
                    console.log('Stream stopped.');
                    updateStatus(false, null);
                }
            });
    });

    function updateStatus(isStreaming, url) {
        if (isStreaming) {
            // Point the <img> src to the video feed route to start viewing
            // A timestamp is added to prevent the browser from caching the stream
            videoStream.src = videoFeedUrl + '?' + new Date().getTime();
            videoStream.style.display = 'block';
            statusMessage.style.display = 'none';
            rtspUrlElement.textContent = url;
            streamInfo.style.display = 'block';
        } else {
            // Clear the <img> src to stop the stream
            videoStream.src = '';
            videoStream.style.display = 'none';
            statusMessage.textContent = 'Stream is stopped.';
            statusMessage.style.display = 'block';
            streamInfo.style.display = 'none';
        }
    }

    // Check the initial stream status when the page loads
    fetch(statusUrl)
        .then(response => response.json())
        .then(data => {
            updateStatus(data.streaming, data.rtsp_url);
        });
});