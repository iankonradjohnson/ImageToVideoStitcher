import os
import fal_client
from src.image_to_video_client import ImageToVideoClient


class FalKlingClient(ImageToVideoClient):
    def __init__(self):
        if not os.getenv('FAL_KEY'):
            raise ValueError("FAL_KEY environment variable must be set")
    
    def generate_video(self, image_path: str, prompt: str):
        # Upload the image
        image_url = fal_client.upload_file(image_path)
        
        # Call the API
        result = fal_client.subscribe(
            "fal-ai/kling-video/v1.6/pro/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url
            },
            with_logs=True
        )
        
        return result