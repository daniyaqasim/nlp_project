import gradio as gr
import grpc
import story2audio_pb2
import story2audio_pb2_grpc
import requests
import tempfile
import os

# Setup gRPC
channel = grpc.insecure_channel('localhost:5001')
stub = story2audio_pb2_grpc.Story2AudioStub(channel)

# Updated function
def generate_audio(story_text):
    if not story_text.strip():
        return "Error: Empty input", None

    try:
        # gRPC request
        request = story2audio_pb2.StoryRequest(story_text=story_text)
        response = stub.GenerateAudio(request)

        if response.status == "success":
            # Download the audio from the URL to a temp file
            audio_url = response.audio_url
            audio_data = requests.get(audio_url)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_data.content)
                local_audio_path = temp_audio_file.name

            return "Success! Play below:", local_audio_path
        else:
            return f"Error: {response.message}", None

    except Exception as e:
        return f"gRPC error: {str(e)}", None
gr.Interface(
    fn=generate_audio,
    inputs=gr.Textbox(lines=5, label="Enter Your Story"),
    outputs=[
        gr.Text(label="Status"),
        gr.Audio(label="Generated Audio", type="filepath")
    ],
    title="Story2Audio Generator",
    description="Enter a story and generate an audio narration using gRPC + Coqui TTS"
).launch()
