import unittest
import os
from unittest.mock import patch, Mock


class TestFalKlingClient(unittest.TestCase):
    
    def setUp(self):
        # Save original FAL_KEY
        self.original_fal_key = os.environ.get('FAL_KEY')
        # Remove FAL_KEY for tests
        os.environ.pop('FAL_KEY', None)
    
    def tearDown(self):
        # Restore original FAL_KEY
        if self.original_fal_key:
            os.environ['FAL_KEY'] = self.original_fal_key
        else:
            os.environ.pop('FAL_KEY', None)
    
    def test_raises_error_when_fal_key_not_set(self):
        # Given
        self.given_no_fal_key_in_environment()
        
        # When/Then
        self.then_initialization_raises_value_error()
    
    def test_creates_client_when_fal_key_is_set(self):
        # Given
        self.given_fal_key_in_environment()
        
        # When
        client = self.when_creating_client()
        
        # Then
        self.then_client_is_created_successfully(client)
    
    @patch('fal_client.upload_file')
    def test_uploads_image_when_generating_video(self, mock_upload):
        # Given
        self.given_fal_key_in_environment()
        client = self.given_client()
        image_path = "/path/to/test.jpg"
        self.given_upload_returns_url(mock_upload)
        
        # When
        with patch('fal_client.subscribe'):
            self.when_generating_video(client, image_path, "test prompt")
        
        # Then
        self.then_image_was_uploaded(mock_upload, image_path)
    
    @patch('fal_client.subscribe')
    @patch('fal_client.upload_file')
    def test_calls_subscribe_with_correct_parameters(self, mock_upload, mock_subscribe):
        # Given
        self.given_fal_key_in_environment()
        client = self.given_client()
        image_path = "/path/to/test.jpg"
        uploaded_url = self.given_upload_returns_url(mock_upload)
        prompt = "Make it dynamic"
        
        # When
        self.when_generating_video(client, image_path, prompt)
        
        # Then
        self.then_subscribe_called_with_correct_params(mock_subscribe, uploaded_url, prompt)
    
    @patch('fal_client.subscribe')
    @patch('fal_client.upload_file')
    def test_returns_video_result_from_subscribe(self, mock_upload, mock_subscribe):
        # Given
        self.given_fal_key_in_environment()
        client = self.given_client()
        self.given_upload_returns_url(mock_upload)
        expected_result = self.given_subscribe_returns_video_result(mock_subscribe)
        
        # When
        result = self.when_generating_video(client, "/path/to/test.jpg", "test prompt")
        
        # Then
        self.then_result_matches_expected(result, expected_result)
    
    def given_no_fal_key_in_environment(self):
        # Already done in setUp
        pass
    
    def given_fal_key_in_environment(self):
        os.environ['FAL_KEY'] = 'test-api-key'
    
    def then_initialization_raises_value_error(self):
        from src.fal_kling_client import FalKlingClient
        
        with self.assertRaises(ValueError) as context:
            FalKlingClient()
        
        self.assertIn("FAL_KEY", str(context.exception))
    
    def when_creating_client(self):
        from src.fal_kling_client import FalKlingClient
        return FalKlingClient()
    
    def then_client_is_created_successfully(self, client):
        from src.fal_kling_client import FalKlingClient
        from src.image_to_video_client import ImageToVideoClient
        self.assertIsInstance(client, FalKlingClient)
        self.assertIsInstance(client, ImageToVideoClient)
    
    def given_client(self):
        from src.fal_kling_client import FalKlingClient
        return FalKlingClient()
    
    def given_upload_returns_url(self, mock_upload):
        uploaded_url = "https://storage.fal.ai/uploaded_image.jpg"
        mock_upload.return_value = uploaded_url
        return uploaded_url
    
    def when_generating_video(self, client, image_path, prompt):
        return client.generate_video(image_path, prompt)
    
    def then_image_was_uploaded(self, mock_upload, image_path):
        mock_upload.assert_called_once_with(image_path)
    
    def then_subscribe_called_with_correct_params(self, mock_subscribe, uploaded_url, prompt):
        mock_subscribe.assert_called_once()
        call_args = mock_subscribe.call_args
        
        # Check model name
        self.assertEqual(call_args[0][0], "fal-ai/kling-video/v1.6/pro/image-to-video")
        
        # Check arguments
        args = call_args[1]['arguments']
        self.assertEqual(args['prompt'], prompt)
        self.assertEqual(args['image_url'], uploaded_url)
        
        # Check other params
        self.assertTrue(call_args[1]['with_logs'])
    
    def given_subscribe_returns_video_result(self, mock_subscribe):
        result = {
            'video': {
                'url': 'https://storage.fal.ai/generated_video.mp4'
            }
        }
        mock_subscribe.return_value = result
        return result
    
    def then_result_matches_expected(self, actual_result, expected_result):
        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    unittest.main()