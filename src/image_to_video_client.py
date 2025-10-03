from abc import ABC, abstractmethod
from typing import Dict, Any


class ImageToVideoClient(ABC):
    @abstractmethod
    def generate_video(self, image_path: str, prompt: str) -> Dict[str, Any]:
        pass


class MockImageToVideoClient(ImageToVideoClient):
    def generate_video(self, image_path: str, prompt: str) -> Dict[str, Any]:
        from pathlib import Path
        filename = Path(image_path).name
        return {
            'video': {
                'url': f'http://fake-api.com/videos/{filename}.mp4'
            }
        }