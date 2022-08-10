# https://aria2.github.io/manual/en/html/aria2c.html#terminology

import asyncio
import json

import aiohttp

import config


# 一个简单的用于发送请求的函数
async def url_json_request():
    '''Serve ALL aria functions. Give an aria2 request method and some required data.
    
    Return: A responese type object'''

# 添加任务
async def add_task(info_text):
    async with aiohttp.ClientSession() as session:
        async with session.post(config.aria2_url, data=info_text) as resp:
            return await resp.text()