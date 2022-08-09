import asyncio
import time
import os
import subprocess
from multiprocessing import Process, Pipe, current_process

from telebot.async_telebot import AsyncTeleBot

from functions import help
import config

# ------------------------------------------------------------------
# 启动regular_caller


# 获取系统类型
path = os.getcwd().replace('\\', '/')
print(path)


# -----------------------------------------------------------------


bot = AsyncTeleBot(config.bot.token, parse_mode='HTML')

bot.register_message_handler(help.help, commands=['help', 'start'], pass_bot=True)


# -----------------------------------------------------------------
# 启动Bot

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())
