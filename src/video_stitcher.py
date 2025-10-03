import subprocess
from typing import List
import os


class VideoStitcher:
    def stitch_videos(self, video_paths: List[str], output_path: str) -> str:
        """Stitch multiple videos together using ffmpeg"""
        # Create a temporary file with the list of videos
        list_file = output_path.replace('.mp4', '_list.txt')
        
        with open(list_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path}'\n")
        
        try:
            # Use ffmpeg to concatenate videos
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y',  # Overwrite output file if exists
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
        finally:
            # Clean up the list file
            if os.path.exists(list_file):
                os.remove(list_file)
                
        return output_path