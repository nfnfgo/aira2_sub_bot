'''
This file is designed to start with main.py by using python subprocess module.

Args:
[1]: PATH, should be a string of current working path, used to import DIY package
'''
import os
import time
import asyncio
import sys
from multiprocessing import Pipe
from multiprocessing import Process

import aiomysql
from telebot.async_telebot import AsyncTeleBot

import config


# ---------------------------------------------------------------
# 定时激活器部分
def main(path: str):
    asyncio.run(async_main(path))


def regular_update_user_level_main():
    asyncio.run(regular_update_user_level())


# ---------------------------------------------------------------

async def async_main(path: str):
    # 设定运行环境
    print('''----------------------------------------
    Notice:
    Multiprocess now started the main() function in regular_caller.py

    Aegv Received:''')
    print(path)
    print('----------------------------------------')
    # 可以通过二次创建multiprocess来实现激活更多的定时器，同时经过验证，在这里激活的定时器貌似不需要进行环境设置
    p = Process(target=regular_update_user_level_main)
    p.start()
    sys.path.append(path)
    # 开始创建bot实例
    bot = AsyncTeleBot(token=config.bot.token, parse_mode='HTML')
    # 开始激活各个激活器
    await regular_push(path, bot)


# push推送消息激活器
async def regular_push(path: str, bot: AsyncTeleBot):
    await asyncio.sleep(config.bot.regular_call_rate)


# 定时读取数据库并且根据exptime刷新用户状态的激活器以及功能实现（做成一体化了）
async def regular_update_user_level():
    await asyncio.sleep(config.bot.update_user_level_rate)
