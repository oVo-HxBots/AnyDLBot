import os

# the secret configuration specific things
import pathlib
import time

import pyrogram

from bot import logger
from helper_funcs import gdriveTools
from helper_funcs.bot_utils import sanitize_file_name, sanitize_text, get_readable_file_size
from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.shortlink_generator import generate_short_link
from plugins.gdriveupload import get_path_size
from translation import Translation
from datetime import datetime

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

@pyrogram.Client.on_message(pyrogram.filters.command(["tleech"]))
async def tg_to_gdrive_upload(bot, update):
    download_location = Config.DOWNLOAD_LOCATION + "/"
    reply_message = await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DOWNLOAD_START,
        reply_to_message_id=update.message_id
    )
    c_time = time.time()
    the_real_download_location = await bot.download_media(
        message=update.reply_to_message,
        file_name=download_location,
        progress=progress_for_pyrogram,
        progress_args=(
            Translation.DOWNLOAD_START,
            reply_message,
            c_time
        )
    )
    if the_real_download_location is not None:
        try:
            await bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.chat.id,
                message_id=reply_message.message_id
            )
        except:
            pass
    txt = update.text
    if txt.find("rename") > -1 and len(txt[txt.find("rename") + 7:]) > 0:
        custom_file_name = txt[txt.find("rename") + 7:]
        custom_file_name = await sanitize_file_name(custom_file_name)
        custom_file_name = await sanitize_text(custom_file_name)
        new_file_name = download_location + custom_file_name
        os.rename(the_real_download_location, new_file_name)
        the_real_download_location = new_file_name
    download_directory = the_real_download_location
    if os.path.exists(download_directory):
        end_one = datetime.now()
        up_name = pathlib.PurePath(download_directory).name
        size = get_readable_file_size(get_path_size(download_directory))
        try:
            await bot.edit_message_text(
                text="Download Completed!!!\n Upload in progress",
                chat_id=reply_message.chat.id,
                message_id=reply_message.message_id
            )
        except Exception as e:
            logger.info(str(e))
            pass
        logger.info(f"Upload Name : {up_name}")
        drive = gdriveTools.GoogleDriveHelper(up_name)
        gd_url, index_url = drive.upload(download_directory)
        button = []
        button.append([pyrogram.types.InlineKeyboardButton(text="☁️ CloudUrl ☁️", url=f"{gd_url}")])
        if Config.INDEX_URL:
            logger.info(index_url)
            button.append([pyrogram.types.InlineKeyboardButton(text="ℹ️ IndexUrl ℹ️", url=f"{index_url}")])
        button_markup = pyrogram.types.InlineKeyboardMarkup(button)
        await bot.send_message(
            text=f"🤖: <b>{up_name}</b> has been Uploaded successfully to your Cloud🤒 \n📀 Size: {size}",
            chat_id=update.chat.id,
            reply_to_message_id=update.message_id,
            reply_markup=button_markup)
        if Config.INDEX_URL:
            await generate_short_link(reply_message, index_url, up_name)
        await reply_message.delete()