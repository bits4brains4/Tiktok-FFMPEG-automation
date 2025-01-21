import os
from moviepy.editor import VideoFileClip
import random
from datetime import datetime
import shutil
import subprocess

class VideoProcessor:
    def __init__(self):
        self.downloads_dir = os.path.expanduser("~/Downloads")
        self.processed_dir = os.path.join(self.downloads_dir, "processed_tiktoks")
        self.original_dir = os.path.join(self.downloads_dir, "original_tiktoks")
        self.marker_file = os.path.join(os.path.dirname(__file__), ".last_session")
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.original_dir, exist_ok=True)

    def process_video(self, video_path):
        try:
            # Load video to get dimensions and duration
            clip = VideoFileClip(video_path)
            duration = clip.duration
            width = clip.w
            height = clip.h

            # Calculate black bar sizes (15% of the original height)
            bar_height = int(height * 0.075)  # 7.5% for top and 7.5% for bottom

            # Generate output path
            filename = os.path.basename(video_path)
            base_name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.processed_dir, f"{base_name}_processed_{timestamp}.mp4")

            # Prepare duration argument if needed
            duration_arg = []
            if duration >= 60:
                new_duration = random.uniform(50, 59)
                duration_arg = ["-t", str(new_duration)]
                print(f"Trimming video from {duration:.1f}s to {new_duration:.1f}s")

            # ffmpeg command to overlay black bars at the top and bottom without cropping
            command = [
                "ffmpeg",
                "-i", video_path,
                "-vf",
                f"drawbox=x=0:y=0:w={width}:h={bar_height}:color=black:t=fill,"  # Top bar
                f"drawbox=x=0:y={height - bar_height}:w={width}:h={bar_height}:color=black:t=fill",  # Bottom bar
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
            ] + duration_arg + [
                "-y",
                output_path
            ]

            print("Processing video...")
            subprocess.run(command, check=True)

            # Move original to backup
            shutil.move(video_path, os.path.join(self.original_dir, filename))

            print(f"Successfully processed: {filename}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error processing {video_path}: {e}")
            return False
        except Exception as e:
            print(f"Error processing {video_path}: {str(e)}")
            return False

    def get_session_videos(self):
        try:
            # Get session start time from marker file
            with open(self.marker_file, 'r') as f:
                session_time = datetime.strptime(f.read().strip(), "%Y%m%d_%H%M%S")

            # Convert to timestamp
            session_timestamp = session_time.timestamp()

            # Get Snaptik videos created after session start
            videos = []
            for f in os.listdir(self.downloads_dir):
                if f.endswith('.mp4') and 'Snaptik' in f:
                    path = os.path.join(self.downloads_dir, f)
                    created_time = os.path.getctime(path)
                    if created_time > session_timestamp:
                        videos.append(path)

            return videos
        except FileNotFoundError:
            print("No session marker found. Please run the TikTok downloader first.")
            return []

    def process_downloads(self):
        print("\nProcessing videos from current session...")
        video_paths = self.get_session_videos()

        if not video_paths:
            print("No new TikTok videos found from this session.")
            return

        print(f"Found {len(video_paths)} videos to process.")

        for video_path in video_paths:
            if os.path.getsize(video_path) > 0:
                print(f"\nProcessing: {os.path.basename(video_path)}")
                self.process_video(video_path)
            else:
                print(f"Skipping empty file: {os.path.basename(video_path)}")

def main():
    processor = VideoProcessor()
    processor.process_downloads()

if __name__ == "__main__":
    main()
