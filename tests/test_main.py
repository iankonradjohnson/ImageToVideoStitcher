import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
from src.image_to_video_client import MockImageToVideoClient


class TestVideoProcessor(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_empty_folder_raises_exception(self):
        # Given
        processor = self.given_video_processor_with_mock_client()
        folder = self.given_an_empty_folder()
        
        # When/Then
        self.then_processing_raises_error_with_message(processor, folder, "No images found")
    
    def test_folder_with_non_image_file_prints_and_raises(self):
        # Given
        processor = self.given_video_processor_with_mock_client()
        folder = self.given_a_folder_with_file('document.txt', "text content")
        
        # When/Then
        self.then_processing_prints_and_raises(processor, folder, "No images found")
    
    @patch('requests.get')
    def test_folder_with_one_image_creates_video_with_specific_size(self, mock_get):
        # Given
        self.given_mock_video_download_returns_42_bytes(mock_get)
        processor = self.given_video_processor_with_mock_client()
        folder = self.given_a_folder_with_real_image('photo.jpg')
        
        # When
        output_path = self.when_processing_folder(processor, folder, "Test prompt")
        
        # Then
        self.then_output_is_video_file(output_path, folder)
        self.then_video_has_expected_size(output_path, 42)  # Mock always returns 42 bytes
    
    @patch('requests.get')
    def test_folder_with_two_images_creates_stitched_video(self, mock_get):
        # Given
        self.given_mock_video_downloads_return_two_videos(mock_get)
        processor = self.given_video_processor_with_stitcher()
        folder = self.given_a_folder_with_two_images('photo1.jpg', 'photo2.jpg')
        
        # When
        output_path = self.when_processing_folder(processor, folder, "Test prompt")
        
        # Then
        self.then_output_is_stitched_video_file(output_path, folder)
    
    def given_video_processor_with_mock_client(self):
        from src.video_processor import VideoProcessor
        from src.video_generator import VideoGenerator
        client = MockImageToVideoClient()
        video_generator = VideoGenerator(client)
        return VideoProcessor(video_generator)
    
    def given_an_empty_folder(self):
        return self.temp_dir
    
    def given_a_folder_with_file(self, filename, content):
        Path(self.temp_dir, filename).write_text(content)
        return self.temp_dir
    
    def given_a_folder_with_real_image(self, filename):
        # Create a minimal valid JPEG file header (enough for our mock to work)
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        Path(self.temp_dir, filename).write_bytes(jpeg_header)
        return self.temp_dir
    
    def given_mock_video_download_returns_42_bytes(self, mock_get):
        # When GET is called on the video URL, return video bytes
        mock_response = Mock()
        mock_response.content = b'x' * 42  # Exactly 42 bytes of video content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
    
    def given_mock_video_downloads_return_two_videos(self, mock_get):
        # Return real video data that ffmpeg can process
        # Create minimal valid MP4 files
        mock_responses = []
        
        # MP4 file header (simplified but valid for ffmpeg)
        video1_data = self._create_minimal_mp4(duration=1)
        video2_data = self._create_minimal_mp4(duration=2)
        
        for video_data in [video1_data, video2_data]:
            mock_response = Mock()
            mock_response.content = video_data
            mock_response.raise_for_status = Mock()
            mock_responses.append(mock_response)
        mock_get.side_effect = mock_responses
    
    def _create_minimal_mp4(self, duration):
        # Create a minimal valid MP4 that ffmpeg can process
        # This is a tiny valid MP4 with just headers
        import subprocess
        import tempfile
        import os
        
        # Use ffmpeg to create a minimal test video
        tmp_path = os.path.join(self.temp_dir, f'test_video_{duration}s.mp4')
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'color=c=black:s=32x32:d={duration}:r=1',
            '-pix_fmt', 'yuv420p', '-y', tmp_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # If ffmpeg fails, create a minimal fake MP4 for testing
            # This is a minimal valid MP4 file header
            return b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42isom' + b'\x00' * 100
        return Path(tmp_path).read_bytes()
    
    def given_video_processor_with_stitcher(self):
        from src.video_processor import VideoProcessor
        from src.video_generator import VideoGenerator
        from src.video_stitcher import VideoStitcher
        client = MockImageToVideoClient()
        video_generator = VideoGenerator(client)
        video_stitcher = VideoStitcher()
        return VideoProcessor(video_generator, video_stitcher)
    
    def given_a_folder_with_two_images(self, filename1, filename2):
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        Path(self.temp_dir, filename1).write_bytes(jpeg_header)
        Path(self.temp_dir, filename2).write_bytes(jpeg_header)
        return self.temp_dir
    
    def then_output_is_stitched_video_file(self, output_path, folder):
        self.assertTrue(Path(output_path).exists())
        self.assertEqual(Path(output_path).parent, Path(folder))
        self.assertTrue(output_path.endswith('.mp4'))
        self.assertIn('stitched', Path(output_path).name)
        
        # Verify the stitched video has approximately 3 seconds (1s + 2s)
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            output_path
        ], capture_output=True, text=True)
        
        duration = float(result.stdout.strip())
        self.assertAlmostEqual(duration, 3.0, delta=0.5)
    
    def when_processing_folder(self, processor, folder, prompt):
        return processor.process_folder(folder, prompt)
    
    def then_output_is_video_file(self, output_path, folder):
        self.assertTrue(Path(output_path).exists())
        self.assertEqual(Path(output_path).parent, Path(folder))
        self.assertTrue(output_path.endswith('.mp4'))
    
    def then_video_has_expected_size(self, output_path, expected_size):
        actual_size = Path(output_path).stat().st_size
        self.assertEqual(actual_size, expected_size)
    
    def then_processing_raises_error_with_message(self, processor, folder, expected_message):
        with self.assertRaises(ValueError) as context:
            processor.process_folder(folder, "Test prompt")
        
        self.assertIn(expected_message, str(context.exception))
    
    def then_processing_prints_and_raises(self, processor, folder, expected_message):
        from io import StringIO
        import sys
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            with self.assertRaises(ValueError) as context:
                processor.process_folder(folder, "Test prompt")
            
            self.assertIn(expected_message, str(context.exception))
            self.assertIn(expected_message, captured_output.getvalue())
        finally:
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()