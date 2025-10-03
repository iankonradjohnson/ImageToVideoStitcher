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
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @patch('src.video_generator.requests.get')
    def test_generate_video_from_single_image(self, mock_get):
        self.given_api_returns_video_content(mock_get, b'fake video content')
        generator = self.given_a_video_generator_with_mock_client()
        image_path = self.given_an_image_file("test_image.jpg")
        
        video_path = self.when_generating_video_from_image(
            generator, 
            image_path, 
            "A beautiful scene"
        )
        
        self.then_video_file_is_created(video_path)
        self.then_video_filename_contains_original_image_name(video_path, "test_image")
        self.then_video_content_matches_api_response(video_path, b'fake video content')
        self.then_api_was_called_once(mock_get)
    
    def given_api_returns_video_content(self, mock_get, content):
        mock_response = Mock()
        mock_response.content = content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
    
    def given_a_video_generator_with_mock_client(self):
        mock_client = MockImageToVideoClient()
        return VideoGenerator(mock_client)
    
    def given_an_image_file(self, filename):
        image_path = Path(self.temp_dir) / filename
        image_path.write_text("fake image content")
        return str(image_path)
    
    def when_generating_video_from_image(self, generator, image_path, prompt):
        return generator.generate_video_from_image(image_path, prompt)
    
    def then_video_file_is_created(self, video_path):
        self.assertIsInstance(video_path, str)
        self.assertTrue(os.path.exists(video_path))
        self.assertTrue(video_path.endswith('.mp4'))
    
    def then_video_filename_contains_original_image_name(self, video_path, expected_name):
        self.assertIn(expected_name, video_path)
    
    def then_video_content_matches_api_response(self, video_path, expected_content):
        with open(video_path, 'rb') as f:
            self.assertEqual(f.read(), expected_content)
    
    def then_api_was_called_once(self, mock_get):
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()