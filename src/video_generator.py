from src.image_to_video_client import ImageToVideoClient
from pathlib import Path
import requests


class VideoGenerator:
    def __init__(self, client: ImageToVideoClient):
        self.client = client
        
    def generate_video_from_image(self, image_path: str, prompt: str) -> str:
        # Call the API
        result = self.client.generate_video(image_path, prompt)
        
        # Extract video URL
        video_url = result['video']['url']
        
        # Create output filename based on input image
        base_name = Path(image_path).stem
        output_dir = Path(image_path).parent
        output_path = output_dir / f"{base_name}_generated.mp4"
        
        # Download the video
        response = requests.get(video_url)
        response.raise_for_status()
        
        # Save the video
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        return str(output_path)