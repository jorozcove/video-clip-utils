import shutil
import os
import subprocess
import json
from fractions import Fraction

class VideoMerger:
    def __init__(self, input_dir, output_dir, max_videos_per_merge=10):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.max_videos_per_merge = max_videos_per_merge

    def get_video_info(self, video_path):
        """Get video codec, resolution, and frame rate information using FFmpeg."""
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate", "-of", "json", video_path],
            capture_output=True,
            text=True
        )
        info = json.loads(result.stdout)
        codec_name = info['streams'][0]['codec_name']
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        frame_rate = str(Fraction(info['streams'][0]['r_frame_rate']))
        return codec_name, width, height, frame_rate

    def classify_videos(self):
        video_files = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir) if os.path.isfile(os.path.join(self.input_dir, f))]
        video_files.sort()  # Sort files to maintain order
    
        # Group videos by codec, resolution, and frame rate
        video_groups = {}
        for video in video_files:
            codec_name, width, height, frame_rate = self.get_video_info(video)
            key = (codec_name, width, height, frame_rate)
            if key not in video_groups:
                video_groups[key] = []
            video_groups[key].append(video)
    
        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
        # Copy each video to its corresponding folder
        for key, videos in video_groups.items():
            codec_name, width, height, frame_rate = key
            group_dir = os.path.join(self.output_dir, f"{codec_name}_{width}x{height}_{frame_rate}")
            os.makedirs(group_dir, exist_ok=True)
            for video in videos:
                shutil.copy(video, group_dir)

    def merge_videos(self):
        video_files = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir) if os.path.isfile(os.path.join(self.input_dir, f))]
        video_files.sort()  # Sort files to maintain order

        # Group videos by codec, resolution, and frame rate
        video_groups = {}
        for video in video_files:
            codec_name, width, height, frame_rate = self.get_video_info(video)
            key = (codec_name, width, height, frame_rate)
            if key not in video_groups:
                video_groups[key] = []
            video_groups[key].append(video)

        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Merge each group separately
        for key, videos in video_groups.items():
            codec_name, width, height, frame_rate = key
            list_file_path = os.path.join(self.output_dir, f"file_list_{codec_name}_{width}x{height}_{frame_rate}.txt")
            self.create_file_list(videos, list_file_path)
            output_path = os.path.join(self.output_dir, f"merged_video_{codec_name}_{width}x{height}_{frame_rate}.mp4")
            # Ensure the directory for the output file exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Use FFmpeg concat demuxer with -fflags +genpts
            subprocess.run([
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file_path, "-c", "copy", "-fflags", "+genpts", output_path
            ], check=True)
            # Clean up the temporary list file
            os.remove(list_file_path)
        print("Merging completed.")