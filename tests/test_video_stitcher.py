import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import tempfile
import os
from src.video_stitcher import VideoStitcher


class TestVideoStitcher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @patch('src.video_stitcher.subprocess.run')
    def test_stitch_multiple_videos(self, mock_run):
        self.given_ffmpeg_succeeds(mock_run)
        stitcher = self.given_a_video_stitcher()
        video_paths = self.given_three_video_files()
        output_path = self.given_an_output_path("output.mp4")
        self.given_ffmpeg_creates_output_file(output_path)
        
        result_path = self.when_stitching_videos(stitcher, video_paths, output_path)
        
        self.then_output_path_is_returned(result_path, output_path)
        self.then_output_file_exists(output_path)
        self.then_ffmpeg_was_called_with_concat_command(mock_run)
        self.then_all_files_are_in_temp_directory(output_path)
    
    def given_ffmpeg_succeeds(self, mock_run):
        mock_run.return_value = Mock()
    
    def given_a_video_stitcher(self):
        return VideoStitcher()
    
    def given_three_video_files(self):
        video_paths = []
        for i in range(3):
            video_path = Path(self.temp_dir) / f"video_{i}.mp4"
            video_path.write_bytes(f"fake video {i} content".encode())
            video_paths.append(str(video_path))
        return video_paths
    
    def given_an_output_path(self, filename):
        return str(Path(self.temp_dir) / filename)
    
    def given_ffmpeg_creates_output_file(self, output_path):
        Path(output_path).write_bytes(b"stitched video content")
    
    def when_stitching_videos(self, stitcher, video_paths, output_path):
        return stitcher.stitch_videos(video_paths, output_path)
    
    def then_output_path_is_returned(self, result_path, expected_path):
        self.assertEqual(result_path, expected_path)
    
    def then_output_file_exists(self, output_path):
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith('.mp4'))
    
    def then_ffmpeg_was_called_with_concat_command(self, mock_run):
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], 'ffmpeg')
        self.assertIn('-f', call_args)
        self.assertIn('concat', call_args)
    
    def then_all_files_are_in_temp_directory(self, output_path):
        self.assertTrue(output_path.startswith(self.temp_dir))


if __name__ == '__main__':
    unittest.main()