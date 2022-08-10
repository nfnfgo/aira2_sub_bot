from ast import Call
import asyncio
from audioop import add
from email import message
import json
import time

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from telebot.async_telebot import AsyncTeleBot

from services import aria
from services.user import UserStatus
from services.bot_command import send_to


async def home(message: Message, bot: AsyncTeleBot):
    '''Use to handle the initial /add command'''
    # Set user status class
    user_status = UserStatus(message)
    # If no info behind the comm, into plain text mode.
    text = message.text
    if text == '/add':
        await send_to(message, bot, '''<b>🚀添加下载任务</b>

请输入指向文件的URL或者输入Magnet磁力链接。如果需要批量下载，请每行填写一个链接''')
        user_status.set_status_info({'button': 'add_task'})
        return
    # if it has info behind the comm, deal with it
    text = text.replace('/add ', '')
    url_list = text.split('\n')
    await add_task(url_list, bot)


# add_task
async def add_task(user_info: Message | CallbackQuery | str | int, bot: AsyncTeleBot, url_list):
    '''Use to deal with download request'''
    user_status = UserStatus(user_info)
    if len(url_list) > 1:
        await send_to(user_info, bot, f'您正在批量导入 <b>{len(url_list)}</b> 个下载项')
    res_data = await aria.add_uri(url_list)
    await send_to(user_info, bot, str(res_data))
    