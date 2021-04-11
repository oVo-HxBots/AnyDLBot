import os

import pyrogram

# the secret configuration specific things
from helper_funcs.shortlink_generator import generate_short_link

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

@pyrogram.Client.on_message(pyrogram.filters.command(["zagl"]))
async def zagl_short_link(bot, update):
    update.command[0] = "zagl"
    txt = " ".join(update.command)
    if txt.find("zagl") > -1 and len(txt.strip()) > 5:
        url_to_shorten = txt[txt.find("gplink") + 5:]
        file_name = None
        if (url_to_shorten.find('workers.dev') > -1):
            file_name = url_to_shorten[url_to_shorten.rindex("/")+1:]
        if file_name is not None and len(file_name) > 0:
            await generate_short_link(update, url_to_shorten, file_name)
        else:
            await generate_short_link(update, url_to_shorten, None)
    else:
        await update.reply_text(f"Please enter URL to shorten Ex:/zagl https://google.com")
