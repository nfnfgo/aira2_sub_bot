import asyncio
import time
import os
import subprocess
from multiprocessing import Process, Pipe, current_process

from telebot.async_telebot import AsyncTeleBot


# ------------------------------------------------------------------
# 启动regular_caller


# 获取系统类型
path = os.getcwd().replace('\\', '/')
print(path)


# -----------------------------------------------------------------


bot = AsyncTeleBot(config.bot.token, parse_mode='HTML')


# -----------------------------------------------------------------
# 启动Bot

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())

