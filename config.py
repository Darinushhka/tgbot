import os

MAX_FILE_SIZE = 100 * 1024 * 1024  


COMPRESSED_DIR = os.path.join(os.getcwd(), "compressed_videos")
os.makedirs(COMPRESSED_DIR, exist_ok=True)
