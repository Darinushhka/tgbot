import os
import tempfile
from time import time

from aiogram import types, F
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart
from aiogram.utils.chat_action import ChatActionSender

from config import MAX_FILE_SIZE, COMPRESSED_DIR
from services.video_service import compress_video_ffmpeg

RATE_LIMIT_SECONDS = 60
last_request_time = {}

def register_handlers(dp, bot):
    @dp.message(CommandStart())
    async def start(message: types.Message):
        await message.answer(
            "Hi! Send me a video (up to 100 MB), and I'll compress it with great quality and a small size 🔥"
        )

    @dp.message(F.video | (F.document & F.document.mime_type.startswith("video")))
    async def handle_video(message: types.Message):
        user_id = message.from_user.id
        now = time()

        if user_id in last_request_time and now - last_request_time[user_id] < RATE_LIMIT_SECONDS:
            await message.answer("⏳ Please wait a bit before sending another video.")
            return
        last_request_time[user_id] = now

        video_file = message.video or message.document
        if video_file.file_size > MAX_FILE_SIZE:
            await message.answer(f"The video is too large (more than {MAX_FILE_SIZE // (1024*1024)} MB).")
            return

        await message.answer("⬇️ Downloading the video...")
        file_info = await bot.get_file(video_file.file_id)
        file_data = await bot.download_file(file_info.file_path)

        temp_dir = tempfile.gettempdir()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir=temp_dir) as input_tmp:
            input_tmp.write(file_data.read())
            input_path = input_tmp.name

        output_path = os.path.join(COMPRESSED_DIR, f"compressed_{user_id}.mp4")

        await message.answer("🎞 Compressing the video... This may take a few minutes ⏳")

        try:
            async with ChatActionSender.upload_video(message.chat.id, bot=bot):
                await compress_video_ffmpeg(input_path, output_path)

            compressed_file = FSInputFile(output_path)
            await message.reply_video(
                video=compressed_file,
                caption="🎬 Compressed video ready!",
                supports_streaming=True
            )

        except Exception as e:
            await message.answer(f"❌ Error while compressing: {e}")

        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

    @dp.message()
    async def unknown(message: types.Message):
        await message.answer("Please send a video file 🎥")
