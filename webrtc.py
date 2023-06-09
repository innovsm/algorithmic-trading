

from streamlit_webrtc import webrtc_streamer


from streamlit_webrtc import webrtc_streamer
import av
webrtc_streamer(key="sample")

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    flipped = img[::-1,:,:]

    return av.VideoFrame.from_ndarray(flipped, format="bgr24")


webrtc_streamer(key="example", video_frame_callback=video_frame_callback)