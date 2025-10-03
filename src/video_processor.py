from pathlib import Path
import concurrent.futures
from typing import List, Tuple


class VideoProcessor:
    def __init__(self, video_generator, video_stitcher=None):
        self.video_generator = video_generator
        self.video_stitcher = video_stitcher
        
    def process_folder(self, folder_path: str, prompt: str) -> str:
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png'}
        image_files = []
        
        for file in Path(folder_path).iterdir():
            if file.suffix.lower() in image_extensions:
                image_files.append(file)
        
        if not image_files:
            print("No images found")
            raise ValueError("No images found")
        
        # Process single image
        if len(image_files) == 1:
            video_bytes = self.video_generator.generate_video_from_image(str(image_files[0]), prompt)
            output_path = Path(folder_path) / "output.mp4"
            output_path.write_bytes(video_bytes)
            return str(output_path)
        
        # Process multiple images
        if len(image_files) > 1 and self.video_stitcher:
            # Sort files for consistent ordering
            sorted_files = sorted(image_files)
            
            # Process images in parallel
            def process_image(args: Tuple[int, Path]) -> Tuple[int, bytes]:
                i, image_file = args
                print(f"Processing image {i+1}/{len(sorted_files)}: {image_file.name}")
                video_bytes = self.video_generator.generate_video_from_image(str(image_file), prompt)
                return i, video_bytes
            
            # Use ThreadPoolExecutor for I/O bound tasks
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(sorted_files)) as executor:
                # Submit all tasks
                future_to_index = {
                    executor.submit(process_image, (i, img)): i 
                    for i, img in enumerate(sorted_files)
                }
                
                # Collect results in order
                video_data = [None] * len(sorted_files)
                for future in concurrent.futures.as_completed(future_to_index):
                    i, video_bytes = future.result()
                    video_data[i] = video_bytes
            
            # Write videos to temp files
            video_paths = []
            for i, video_bytes in enumerate(video_data):
                temp_video_path = Path(folder_path) / f"temp_video_{i}.mp4"
                temp_video_path.write_bytes(video_bytes)
                video_paths.append(str(temp_video_path))
            
            output_path = Path(folder_path) / "stitched_output.mp4"
            return self.video_stitcher.stitch_videos(video_paths, str(output_path))