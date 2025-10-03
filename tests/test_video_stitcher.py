import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import tempfile
import os
from src.video_stitcher import VideoStitcher


class TestVideoStitcher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.stitcher = VideoStitcher()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @patch('src.video_stitcher.subprocess.run')
    def test_stitch_multiple_videos(self, mock_run):
        """Test stitching multiple videos into one"""
        # Setup mock
        mock_run.return_value = Mock()
        
        # Create fake video files
        video_paths = []
        for i in range(3):
            video_path = Path(self.temp_dir) / f"video_{i}.mp4"
            video_path.write_bytes(f"fake video {i} content".encode())
            video_paths.append(str(video_path))
        
        output_path = str(Path(self.temp_dir) / "output.mp4")
        
        # Create fake output file since ffmpeg is mocked
        Path(output_path).write_bytes(b"stitched video content")
        
        # Stitch videos
        result_path = self.stitcher.stitch_videos(video_paths, output_path)
        
        # Check that output file was created
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith("output.mp4"))
        
        # Verify ffmpeg was called
        mock_run.assert_called_once()
        
        # Verify the command structure
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], 'ffmpeg')
        self.assertIn('-f', call_args)
        self.assertIn('concat', call_args)
        
        # Verify all files are in temp_dir (will be cleaned up in tearDown)
        self.assertTrue(output_path.startswith(self.temp_dir))


if __name__ == '__main__':
    unittest.main()