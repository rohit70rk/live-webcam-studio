document.addEventListener('DOMContentLoaded', function() {
    // --- Elements ---
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const videoStream = document.getElementById('video-stream');
    const statusMessage = document.getElementById('status-message');
    const streamContainer = document.getElementById('stream-container');
    const rtspInfo = document.getElementById('rtsp-info');
    const rtspLink = document.getElementById('rtsp-link');

    // --- API Endpoints ---
    const API = {
        START: '/api/start/',
        STOP: '/api/stop/',
        STATUS: '/api/status/',
        FEED: '/api/feed/'
    };

    // --- Functions ---
    function updateUI(isStreaming, url) {
        if (isStreaming) {
            // Streaming State
            if (streamContainer) streamContainer.classList.remove('hidden');
            
            // Cache busting for video feed
            if (videoStream) {
                videoStream.src = API.FEED + '?t=' + new Date().getTime();
                videoStream.style.display = 'block';
            }

            if (rtspInfo) rtspInfo.classList.remove('hidden');
            if (rtspLink) rtspLink.textContent = url || 'Unavailable';
            
            if (statusMessage) statusMessage.style.display = 'none';

            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;

        } else {
            // Stopped State
            if (streamContainer) streamContainer.classList.add('hidden');
            if (videoStream) {
                videoStream.src = ''; 
                videoStream.style.display = 'none';
            }

            if (rtspInfo) rtspInfo.classList.add('hidden');

            if (statusMessage) {
                statusMessage.textContent = 'Stream is currently offline. Click "Start Server" to begin.';
                statusMessage.style.display = 'block';
            }

            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        }
    }

    // --- Event Listeners ---
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            statusMessage.textContent = 'Starting FFmpeg process...';
            statusMessage.style.display = 'block';
            
            // Disable button immediately to prevent double clicks
            startBtn.disabled = true;

            fetch(API.START)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'started' || data.status === 'already_running') {
                        updateUI(true, data.rtsp_url);
                    } else {
                        statusMessage.textContent = 'Error: ' + data.message;
                        startBtn.disabled = false;
                    }
                })
                .catch(err => {
                    statusMessage.textContent = 'Connection Error: ' + err;
                    startBtn.disabled = false;
                });
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            // Optimistic UI update
            stopBtn.disabled = true;
            
            fetch(API.STOP)
                .then(res => res.json())
                .then(data => {
                    updateUI(false, null);
                });
        });
    }

    // --- Init ---
    if (startBtn || videoStream) {
        fetch(API.STATUS)
            .then(res => res.json())
            .then(data => {
                updateUI(data.streaming, data.rtsp_url);
            })
            .catch(() => {
                console.log("Backend offline or unreachable");
            });
    }
});