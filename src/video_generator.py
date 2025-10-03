from src.image_to_video_client import ImageToVideoClient
from pathlib import Path
import requests


class VideoGenerator:
    def __init__(self, client: ImageToVideoClient):
        self.client = client
        
    def generate_video_from_image(self, image_path: str, prompt: str) -> bytes:
        # Call the API
        result = self.client.generate_video(image_path, prompt)
        
        # Extract video URL
        video_url = result['video']['url']
        
        # Download the video
        response = requests.get(video_url)
        response.raise_for_status()
        
        return response.content