import os
import tempfile
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart

from config import MAX_FILE_SIZE, COMPRESSED_DIR
from services.video_service import compress_video_ffmpeg

def register_handlers(dp, bot):
    @dp.message(CommandStart())
    async def start(message: types.Message):
        await message.answer(
            "Hi! Send me a video (up to 100 MB), and I'll compress it with great quality and a small size 🔥"
        )

    @dp.message()
    async def handle_video(message: types.Message):
        video_file = message.video or (message.document if message.document.mime_type.startswith("video") else None)

        if not video_file:
            await message.answer("Please send a video 🎥")
            return

        if video_file.file_size > MAX_FILE_SIZE:
            await message.answer(f"The video is too large (more than {MAX_FILE_SIZE // (1024*1024)} MB).")
            return

        await message.answer("⬇️ Downloading the video...")

        file_info = await bot.get_file(video_file.file_id)
        file_data = await bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as input_tmp:
            input_tmp.write(file_data.read())
            input_path = input_tmp.name

        output_path = os.path.join(COMPRESSED_DIR, f"compressed_{message.from_user.id}.mp4")

        await message.answer("🎞 Compressing the video... This may take a few minutes ⏳")

        try:
            await compress_video_ffmpeg(input_path, output_path)

            await message.answer("✅ Done! Here is your compressed video:")
            compressed_file = FSInputFile(output_path)
            await message.reply_video(
                video=compressed_file,
                caption="🎬 Compressed video ready!",
                supports_streaming=True
            )

        except Exception as e:
            await message.answer(f"Error while compressing: {e}")

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
