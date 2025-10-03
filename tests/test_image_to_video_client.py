import unittest
from src.image_to_video_client import ImageToVideoClient, MockImageToVideoClient


class TestImageToVideoClient(unittest.TestCase):
    def test_mock_client_implements_interface(self):
        client = self.given_a_mock_client()
        self.then_client_implements_image_to_video_interface(client)
        
    def test_mock_client_has_generate_video_method(self):
        client = self.given_a_mock_client()
        self.then_client_has_generate_video_method(client)
        
    def test_mock_client_returns_fake_video_url(self):
        client = self.given_a_mock_client()
        result = self.when_generating_video_for_image(client, "test.jpg", "A test video")
        self.then_result_contains_video_url(result)
        self.then_video_url_contains_original_filename(result, "test.jpg")
    
    def given_a_mock_client(self):
        return MockImageToVideoClient()
    
    def when_generating_video_for_image(self, client, image_path, prompt):
        return client.generate_video(image_path, prompt)
    
    def then_client_implements_image_to_video_interface(self, client):
        self.assertIsInstance(client, ImageToVideoClient)
    
    def then_client_has_generate_video_method(self, client):
        self.assertTrue(hasattr(client, 'generate_video'))
        self.assertTrue(callable(client.generate_video))
    
    def then_result_contains_video_url(self, result):
        self.assertIsInstance(result, dict)
        self.assertIn('video', result)
        self.assertIn('url', result['video'])
    
    def then_video_url_contains_original_filename(self, result, image_path):
        expected_url = f'http://fake-api.com/videos/{image_path}.mp4'
        self.assertEqual(result['video']['url'], expected_url)


if __name__ == '__main__':
    unittest.main()