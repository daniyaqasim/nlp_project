import grpc
from concurrent import futures
import os
import uuid
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import story2audio_pb2
import story2audio_pb2_grpc
from TTS.api import TTS
import threading
import time

# Load the TTS model globally (English multi-speaker)
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

# Lock to ensure no concurrent access to TTS when using GPU, if applicable
lock = threading.Lock()

# Define the service implementation
class Story2AudioServicer(story2audio_pb2_grpc.Story2AudioServicer):
    def GenerateAudio(self, request, context):
        
        story = request.story_text.strip()
        if not story:
            return story2audio_pb2.AudioResponse(
                status="error",
                message="Story text is empty",
                audio_url=""
            )
        try:
            # Generate a unique filename
            audio_filename = f"output_{uuid.uuid4().hex}.wav"

            # Use a lock to prevent concurrent access to the TTS model if needed
            with lock:
                # Generate audio and save to file
                tts_model.tts_to_file(text=story, file_path=audio_filename)

            # Return the URL of the generated audio
            audio_url = f"http://localhost:5000/{audio_filename}"

            return story2audio_pb2.AudioResponse(
                status="success",
                message="Audio generated successfully.",
                audio_url=audio_url
            )
        except Exception as e:
            return story2audio_pb2.AudioResponse(
                status="error",
                message=str(e),
                audio_url=""
            )

# Function to serve the audio files via HTTP
def serve_http():
    os.chdir('./')  # Serve from current directory
    httpd = TCPServer(('localhost', 5000), SimpleHTTPRequestHandler)
    print("🟢 HTTP server started on port 5000")
    httpd.serve_forever()

# Set up and start the gRPC server with concurrency
def serve_grpc():
    # Set up the gRPC server to handle multiple requests concurrently
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # This allows 10 concurrent requests
    story2audio_pb2_grpc.add_Story2AudioServicer_to_server(Story2AudioServicer(), server)
    server.add_insecure_port('[::]:5001')
    print("🟢 gRPC Server started on port 5001")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc)
    grpc_thread.start()

    # Start the HTTP server for serving the audio files
    serve_http() 