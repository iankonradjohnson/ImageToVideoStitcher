#!/usr/bin/env python3

import argparse
import sys
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.video_processor import VideoProcessor
from src.video_generator import VideoGenerator
from src.video_stitcher import VideoStitcher
from src.fal_kling_client import FalKlingClient


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos from images using Kling AI and stitch them together"
    )
    parser.add_argument("input_dir", help="Directory containing images to process")
    parser.add_argument("prompt", help="Prompt to use for video generation")
    
    args = parser.parse_args()
    
    try:
        # Create components
        client = FalKlingClient()
        video_generator = VideoGenerator(client)
        video_stitcher = VideoStitcher()
        processor = VideoProcessor(video_generator, video_stitcher)
        
        # Process folder
        print(f"Processing images in: {args.input_dir}")
        print(f"Using prompt: {args.prompt}")
        
        output_path = processor.process_folder(args.input_dir, args.prompt)
        
        print(f"\nSuccess! Video created at: {output_path}")
        
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
