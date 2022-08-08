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

import aiofiles
import aiomysql
from telebot.async_telebot import AsyncTeleBot

import config
from services import bot_status
from services.sql import create_pool
from services.sql import SQLPool
import services.sql
from functions import push


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
    p = Process(target=regular_update_user_level_main)
    p.start()
    sys.path.append(path)
    # 开始创建bot实例
    bot = AsyncTeleBot(token=config.bot.token, parse_mode='HTML')
    # 开始激活各个激活器
    await regular_push(path, bot)


# push推送消息激活器
async def regular_push(path: str, bot: AsyncTeleBot):
    # 设定函数内部变量
    push_start = False
    push_started = False
    # 开始确认是否激活相关函数
    if config.bot.auto_start_pushing == True and push_started == False:
        push_start = True
        push_started = True

    # 开始循环激活
    while True:
        # 确认推送状态
        try:
            push_start = await bot_status.get_status('push_start')
        except:
            print('Error: Cannot get push_start status')
        # 推送频道消息的函数起点
        if push_start == True:
            # print('start start_push Function')
            await push.start_push(bot)
        # 创建线程池
        await create_pool()
        # 睡一会儿，睡指定的时间
        await asyncio.sleep(config.bot.regular_call_rate)


# 定时读取数据库并且根据exptime刷新用户状态的激活器以及功能实现（做成一体化了）
async def regular_update_user_level():
    asyncsql = SQLPool()
    pool = await asyncsql.create()
    while True:
        # print('updating user level')
        async with pool.acquire() as conn:
            conn = aiomysql.Connection = conn
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor = cursor
                await conn.commit()
                # 选中所有身份过期的用户，包括管理员
                await cursor.execute('''SELECT id FROM users WHERE expire_time<%s AND status != 0''', (int(time.time()),))
                res = await cursor.fetchall()
                # 获取受影响的行数
                affected_rows = cursor.rowcount
        if affected_rows > 0:
            # 构造需要处理的用户列表
            user_list = []
            for i in res:
                user_list.append(i[0])
            # print(user_list)
            # user_list 之中是一些已经过期的账号id，现在需要对其进行处理
            for user_id in user_list:
                async with pool.acquire() as conn:
                    conn = aiomysql.Connection = conn
                    async with conn.cursor() as cursor:
                        cursor: aiomysql.Cursor = cursor
                        # 更改用户状态
                        await conn.commit()
                        await cursor.execute('''UPDATE users SET status=1 WHERE id=%s''', (user_id,))
                        await conn.commit()
                        # 获取用户当前频道订阅数量
                        await cursor.execute('''SELECT * FROM ch_subscriptions WHERE user_id=%s and status=1''', (user_id,))
                        sub_count=cursor.rowcount
                        # 如果用户已经超量，则默认删除最新添加的一些频道，保证数量上最大等于免费用户的数量
                        if sub_count>config.premium.ch_max['user']:
                            # 更改用户状态
                            await conn.commit()
                            await cursor.execute('''UPDATE ch_subscriptions SET status=0 WHERE user_id=%s ORDER BY sub_time DESC LIMIT %s''', (user_id,sub_count-config.premium.ch_max['user']))
                            await conn.commit()
                        # 开始恢复用户分流为私信
                        await cursor.execute('''UPDATE ch_subscriptions SET target_chat=%s WHERE user_id=%s and status=1''', (user_id,user_id,))
                        await conn.commit()

        await asyncio.sleep(config.bot.update_user_level_rate)
