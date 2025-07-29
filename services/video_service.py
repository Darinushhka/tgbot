import asyncio
from asyncio import Semaphore

semaphore = Semaphore(2)  


async def compress_video_ffmpeg(input_path: str, output_path: str):
    async with semaphore:
        command = [
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-preset", "medium",
            "-movflags", "+faststart",
            output_path
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
