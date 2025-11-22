import asyncio
import os
import json
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRecorder

RTSP_URL = os.getenv("RTSP_URL", "rtsp://rtsp-server:8554/live")
routes = web.RouteTableDef()

pcs = set()

@routes.post("/offer")
async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    # recorder will push to RTSP via ffmpeg (aiortc spawns ffmpeg)
    recorder = MediaRecorder(RTSP_URL, format="rtsp")

    @pc.on("track")
    def on_track(track):
        print("Track %s received" % track.kind)
        recorder.addTrack(track)

    # handle disconnect cleanup
    async def on_shutdown():
        await recorder.stop()
        await pc.close()

    await recorder.start()
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

async def on_shutdown(app):
    coros = []
    for pc in pcs:
        coros.append(pc.close())
    await asyncio.gather(*coros)

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
