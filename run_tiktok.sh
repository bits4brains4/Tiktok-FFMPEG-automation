#!/bin/bash
# Navigate to the tiktok-downloader directory
cd ~/Desktop/tiktok-downloader

# Activate the virtual environment
source venv/bin/activate

# Run the Python scripts
python3 tiktok_automation.py
python3 process_videos.py
