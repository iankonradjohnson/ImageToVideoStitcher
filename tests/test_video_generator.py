import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import tempfile
import os
from src.video_generator import VideoGenerator
from src.image_to_video_client import MockImageToVideoClient


class TestVideoGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MockImageToVideoClient()
        self.generator = VideoGenerator(self.mock_client)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @patch('src.video_generator.requests.get')
    def test_generate_video_from_single_image(self, mock_get):
        """Test generating a video from a single image"""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = b'fake video content'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Create a fake image file
        image_path = Path(self.temp_dir) / "test_image.jpg"
        image_path.write_text("fake image content")
        
        # Generate video - should download and save locally
        video_path = self.generator.generate_video_from_image(
            str(image_path), 
            "A beautiful scene"
        )
        
        # Check that a video file was created
        self.assertIsInstance(video_path, str)
        self.assertTrue(os.path.exists(video_path))
        self.assertTrue(video_path.endswith('.mp4'))
        self.assertIn('test_image', video_path)
        
        # Verify the mock was called
        mock_get.assert_called_once()
        
        # Verify the content was written
        with open(video_path, 'rb') as f:
            self.assertEqual(f.read(), b'fake video content')


if __name__ == '__main__':
    unittest.main()