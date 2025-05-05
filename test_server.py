import grpc
import story2audio_pb2
import story2audio_pb2_grpc
import time
import concurrent.futures

# Create a gRPC channel and stub
channel = grpc.insecure_channel('localhost:5001')
stub = story2audio_pb2_grpc.Story2AudioStub(channel)

# Helper function to send a request with a timeout
def send_request(story_text):
    try:
        print(f"Sending request for story: {story_text[:30]}...")  # Log the first part of the story
        request = story2audio_pb2.StoryRequest(story_text=story_text)
        response = stub.GenerateAudio(request, timeout=120)  # Set a 30-second timeout
        
        print(f"Story: {story_text[:30]}... | Status: {response.status} | URL: {response.audio_url}")
        
        # Handle different status codes
        if response.status == "success":
            print(f"Audio successfully generated! You can listen to it here: {response.audio_url}")
        else:
            print(f"Error generating audio: {response.message}")
    
    except grpc.RpcError as e:
        print(f"RPC Error: {e}")
    except grpc.FutureTimeoutError:
        print("Request timed out!")

# Test: Single Valid Request
def test_single_valid():
    print("🔹 Test: Single Valid Request")
    send_request("Once upon a time in a land far away")

# Test: Empty Input Request
def test_empty_input():
    print("\n🔹 Test: Empty Input Request")
    send_request("")  # Empty input should trigger error

# Stress Test: Multiple Concurrent Requests (using ThreadPoolExecutor)
def stress_test_multiple_requests():
    print("\n🔹 Test: Multiple Concurrent Requests")
    stories = [
        "She opened the door to find",
        "The wind howled as it passed",
        "Once upon a time, a king",
        "A dark shadow loomed over the forest",
        "The sun rose, signaling a new day"
    ]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(send_request, stories)

# Performance Test: Test response time for a large story
def test_performance_large_story():
    print("\n🔹 Test: Performance Test (Moderately Large Story)")

    # Simulate a moderately long story by repeating a paragraph 10 times
    paragraph = (
        "Once upon a time in a distant land, there lived a curious young girl named Lila. "
        "She had a deep love for stories and dreamed of exploring faraway places. "
        "Each night, she would read tales by candlelight until she drifted off to sleep. "
    )
    large_story = paragraph * 3  # Adjust this multiplier for safe testing

    start = time.time()
    send_request(large_story)
    end = time.time()
    print(f"⏱️  Response time: {end - start:.2f} seconds")

# Edge Case: Non-ASCII characters (e.g., emoji, non-Latin)
def edge_case_non_ascii():
    print("\n🔹 Test: Edge Case (Non-ASCII characters)")
    send_request("Once upon a time 🏰👑✨")

# Edge Case: Empty Story
def edge_case_empty_story():
    print("\n🔹 Test: Edge Case (Empty Story)")
    send_request("")  # Empty story should trigger error

# Run all tests
if __name__ == "__main__":
    # Test Single Valid Request
    test_single_valid()
    
    # Test Empty Input Request
    test_empty_input()
    
    # Stress Test Multiple Concurrent Requests
    stress_test_multiple_requests()
    
    # Performance Test for Large Story
    test_performance_large_story()
    
    # Edge Case: Non-ASCII Characters
    edge_case_non_ascii()
    
    # Edge Case: Empty Story
    edge_case_empty_story()
