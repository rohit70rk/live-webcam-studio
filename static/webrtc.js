document.addEventListener('DOMContentLoaded', async () => {
    const localVideo = document.getElementById('local-video');
    const remoteVideo = document.getElementById('remote-video');
    const startCallBtn = document.getElementById('start-call-btn');
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    
    // NEW: Grab the toggle buttons
    const toggleCamBtn = document.getElementById('toggle-cam-btn');
    const toggleMicBtn = document.getElementById('toggle-mic-btn');

    let localStream;
    let peerConnection;

    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const signalingSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/stream/${roomName}/`);

    const configuration = {
        'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]
    };

    // 1. Get Local Camera & Mic
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error('Error accessing media devices.', error);
        alert("Camera and microphone access is required.");
        return;
    }

    // NEW: Camera Toggle Logic
    toggleCamBtn.addEventListener('click', () => {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            
            // Update button UI
            if (videoTrack.enabled) {
                toggleCamBtn.textContent = 'Camera: ON';
                toggleCamBtn.classList.replace('stop-btn', 'secondary-btn');
            } else {
                toggleCamBtn.textContent = 'Camera: OFF';
                toggleCamBtn.classList.replace('secondary-btn', 'stop-btn');
            }
        }
    });

    // NEW: Microphone Toggle Logic
    toggleMicBtn.addEventListener('click', () => {
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            
            // Update button UI
            if (audioTrack.enabled) {
                toggleMicBtn.textContent = 'Mic: ON';
                toggleMicBtn.classList.replace('stop-btn', 'secondary-btn');
            } else {
                toggleMicBtn.textContent = 'Mic: OFF';
                toggleMicBtn.classList.replace('secondary-btn', 'stop-btn');
            }
        }
    });

    // 2. Initialize WebRTC Peer Connection
    function createPeerConnection() {
        peerConnection = new RTCPeerConnection(configuration);

        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });

        peerConnection.ontrack = event => {
            if (!remoteVideo.srcObject) {
                remoteVideo.srcObject = event.streams[0];
            }
        };

        peerConnection.onicecandidate = event => {
            if (event.candidate) {
                signalingSocket.send(JSON.stringify({'candidate': event.candidate}));
            }
        };
    }

    // 3. Handle incoming Signaling Messages
    signalingSocket.onmessage = async (e) => {
        const data = JSON.parse(e.data);

        if (data.offer) {
            if (!peerConnection) createPeerConnection();
            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            signalingSocket.send(JSON.stringify({'answer': answer}));
        } 
        else if (data.answer) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
        } 
        else if (data.candidate) {
            try {
                await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
            } catch (e) {
                console.error('Error adding received ice candidate', e);
            }
        }
    };

    // 4. Start the Call (Send the Offer)
    startCallBtn.addEventListener('click', async () => {
        startCallBtn.disabled = true;
        createPeerConnection();
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        signalingSocket.send(JSON.stringify({'offer': offer}));
    });
});