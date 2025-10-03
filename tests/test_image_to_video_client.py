import unittest
from src.image_to_video_client import ImageToVideoClient, MockImageToVideoClient


class TestImageToVideoClient(unittest.TestCase):
    def test_mock_client_implements_interface(self):
        """Test that MockImageToVideoClient implements the ImageToVideoClient interface"""
        mock_client = MockImageToVideoClient()
        self.assertIsInstance(mock_client, ImageToVideoClient)
        
    def test_mock_client_has_generate_video_method(self):
        """Test that MockImageToVideoClient has generate_video method"""
        mock_client = MockImageToVideoClient()
        self.assertTrue(hasattr(mock_client, 'generate_video'))
        self.assertTrue(callable(mock_client.generate_video))
        
    def test_mock_client_returns_fake_video_url(self):
        """Test that MockImageToVideoClient returns a fake video URL"""
        mock_client = MockImageToVideoClient()
        result = mock_client.generate_video("test.jpg", "A test video")
        
        self.assertIsInstance(result, dict)
        self.assertIn('video', result)
        self.assertIn('url', result['video'])
        self.assertEqual(result['video']['url'], 'http://fake-api.com/videos/test.jpg.mp4')


if __name__ == '__main__':
    unittest.main()